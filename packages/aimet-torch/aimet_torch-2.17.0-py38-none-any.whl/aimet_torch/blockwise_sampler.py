# -*- mode: python -*-
# =============================================================================
#  @@-COPYRIGHT-START-@@
#
#  Copyright (c) 2025, Qualcomm Innovation Center, Inc. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#  POSSIBILITY OF SUCH DAMAGE.
#
#  SPDX-License-Identifier: BSD-3-Clause
#
#  @@-COPYRIGHT-END-@@
# =============================================================================

"""Blockwise sampling utilty"""

import itertools
import pickle
import os
import sys
import tempfile
import contextlib
from copy import deepcopy
from tqdm import tqdm
from typing import List, Union, Tuple, Generator, Callable

import torch
from torch.utils.data import DataLoader

from aimet_torch.v2.utils import default_forward_fn, patch_attr
from aimet_torch.utils import change_tensor_device_placement
from aimet_torch import QuantizationSimModel, utils

logger = utils.AimetLogger.get_area_logger(utils.AimetLogger.LogAreas.Utils)


def change_tensor_and_cache_device_placement(inputs, device, cache_movement_fn=None):
    """This function moves all tensors and huggingface Cache objects to the provided device"""

    # Move all tensors to the provided device
    moved_inputs = change_tensor_device_placement(inputs, device)
    # At this point everything except the Cache objects should be placed on the correct device

    # Helper function to find Cache objects in the provided inputs
    def find_cache(inputs):
        if "transformers" not in sys.modules:
            # If the transformers module has not been imported, then there cannot be any Cache objects present
            # Since the base class is provided in transformers
            return None
        if isinstance(inputs, sys.modules["transformers"].cache_utils.Cache):
            return inputs
        if isinstance(inputs, (tuple, list, dict)):
            recursive_results = (
                (find_cache(inp) for inp in inputs.values())
                if isinstance(inputs, dict)
                else (find_cache(inp) for inp in inputs)
            )
            try:
                return next(item for item in recursive_results if item is not None)
            except StopIteration:
                return None
        return None

    cache_obj = find_cache(moved_inputs)
    if cache_obj:
        if cache_movement_fn:
            cache_movement_fn(cache_obj)
        else:
            try:
                # Generally, this strategy should work in most cases. However, there is no guarantee from the base
                # Cache class on this. So, if this fails we will ask users to provide a custom function for moving
                # the contents of their Cache object between devices
                cache_obj.key_cache = change_tensor_device_placement(
                    cache_obj.key_cache, device
                )
                cache_obj.value_cache = change_tensor_device_placement(
                    cache_obj.value_cache, device
                )
            except Exception as e:
                logger.error(
                    "Please provide a cache_movement_fn to move contents of the Cache object used by the model"
                    " between devices. Or, please modify your model to use a DynamicCache object."
                )
                raise e

    return moved_inputs


class CachedBlockInput:
    """
    Class providing disk offloading capabilities for cache block inputs. If specified in the constructor arguments,
    objects of this class will be offloaded to CPU unless they are accessed inside the .load() context manager. This
    allows the blockwise sampler to be used with a much higher number of samples, although there is a slight slowdown
    due to the disk I/O incurred by disk operations.
    """

    def __init__(self, args, kwargs, place_on_disk: bool = False):
        self._args = args
        self._kwargs = kwargs

        self.args_path = None
        self.args_changed = True
        self.kwargs_path = None
        self.kwargs_changed = True
        self.place_on_disk = place_on_disk

        if place_on_disk:
            self.enable_disk_caching()

    def enable_disk_caching(self):
        """Function to enable disk caching"""
        fd, self.args_path = tempfile.mkstemp(suffix=".pkl", text=True)
        os.close(fd)  # If fd is not closed then it remains open
        self.args_changed = True

        fd, self.kwargs_path = tempfile.mkstemp(suffix=".pkl", text=True)
        os.close(fd)  # If fd is not closed then it remains open
        self.kwargs_changed = True

        self.place_on_disk = True
        self._cache_on_disk()

    def disable_disk_caching(self):
        """Function to disable disk caching"""
        if not self.place_on_disk:
            return  # Disk caching already disabled

        self.place_on_disk = False
        os.remove(self.args_path)
        os.remove(self.kwargs_path)

    @contextlib.contextmanager
    def load(self):
        """Context manager that ensures CachedBlockInput is loaded from disk, and returned to the correct location."""
        if self.place_on_disk:
            self._load_from_disk()

        yield

        if self.place_on_disk:
            self._cache_on_disk()

    @property
    def args(self):
        """Getter function for captured args"""
        return self._args

    @args.setter
    def args(self, args):
        """Setter function for captured args"""
        if self._args is None:
            raise RuntimeError(
                "Attempting to modify args without loading from disk. Please place this line inside"
                " a .load() context manager."
            )
        self.args_changed = True
        self._args = args

    @property
    def kwargs(self):
        """Getter function for captured kwargs"""
        return self._kwargs

    @kwargs.setter
    def kwargs(self, kwargs):
        """Setter function for captured kwargs"""
        if self._kwargs is None:
            raise RuntimeError(
                "Attempting to modify kwargs without loading from disk. Please place this line inside"
                " a .load() context manager."
            )
        self.kwargs_changed = True
        self._kwargs = kwargs

    def _cache_on_disk(self):
        """Helper function to cache on disk."""
        assert self.place_on_disk

        if self.args_changed:
            with open(self.args_path, "wb") as args_file:
                pickle.dump(self.args, args_file)

        if self.kwargs_changed:
            with open(self.kwargs_path, "wb") as kwargs_file:
                pickle.dump(self.kwargs, kwargs_file)

        self._args = None
        self._kwargs = None

    def _load_from_disk(self):
        """Helper function to load from disk."""
        assert self.place_on_disk

        with open(self.args_path, "rb") as args_file:
            self._args = pickle.load(args_file)
        with open(self.kwargs_path, "rb") as kwargs_file:
            self._kwargs = pickle.load(kwargs_file)

        self.args_changed = False
        self.kwargs_changed = False

    def to(self, device):
        """Helper function to move loaded args and kwargs between devices."""
        if self.args is not None:
            self._args = change_tensor_and_cache_device_placement(self.args, device)
        if self.kwargs is not None:
            self._kwargs = change_tensor_and_cache_device_placement(self.kwargs, device)

        return self

    def __del__(self):
        """Destructor to make sure that temp files are cleaned up."""
        self.disable_disk_caching()

    def __deepcopy__(self, memo):
        """Custom deepcopy implementation to make sure that tensor computational graphs are not copied."""
        with (
            self.load(),
            patch_attr(
                torch.Tensor, "__deepcopy__", lambda self, memo: self.detach().clone()
            ),
        ):
            return CachedBlockInput(
                deepcopy(self.args), deepcopy(self.kwargs), deepcopy(self.place_on_disk)
            )

    def __iter__(self):
        """Allows tuple unpacking on objects of this class."""
        return iter((self.args, self.kwargs))


class BlockwiseSampler:
    """
    Class providing blockwise sampling utilities. Specifically, BlockWise sampler allows users to specify a list of
    sequential blocks in the module, and the sampler will yield each block, along with the FP and QT inputs to that
    block as a part of the sample() loop.
    BlockwiseSampler caches each block input and resumes computation from that point when the user returns control to
    the sampling loop. This way, excess computational costs for large models is avoided, and the loop is able to make
    use of any user adjustments to quantization parameters for a particular block made in the sampling loop.
    NOTE: users CAN NOT modify model weights during the sample() loop
    """

    def __init__(
        self,
        sim: QuantizationSimModel,
        blocks: List[torch.nn.Module],
        dataloader: DataLoader,
        forward_fn: Callable = default_forward_fn,
        keep_unused_blocks_on_cpu: bool = True,
        cache_activations_on_disk: bool = True,
    ):
        self.sim = sim
        self.blocks = blocks
        self.dataloader = dataloader
        self.forward_fn = forward_fn
        self.keep_unused_blocks_on_cpu = keep_unused_blocks_on_cpu
        self.cache_activations_on_disk = cache_activations_on_disk

    @torch.no_grad()
    def run_inference(self, sample) -> Generator[CachedBlockInput, None, None]:
        """
        Helper function to run inference on the model using the given sample, pausing and yielding the results after
        each block.
        """

        class StopForwardExceptionWithInput(utils.StopForwardException):
            """Exception raised in order to stop forward execution through the model. Holds module input data."""

            def __init__(self, captured_input):
                self.captured_input = captured_input

        def hook_fn(_, args, kwargs):
            raise StopForwardExceptionWithInput(
                deepcopy(CachedBlockInput(args, kwargs))
            )

        hook = self.blocks[0].register_forward_pre_hook(hook_fn, with_kwargs=True)
        try:
            self.forward_fn(self.sim.model, sample)
        except StopForwardExceptionWithInput as e:
            # pylint: disable=used-before-assignment
            hook.remove()
            next_block_input = e.captured_input
            next_block_input.to("cpu")

            if self.cache_activations_on_disk:
                next_block_input.enable_disk_caching()

            yield next_block_input

        for block in self.blocks[:-1]:
            with next_block_input.load():
                next_block_input.to(utils.get_device(block))
                next_block_input.args = block(
                    *next_block_input.args, **next_block_input.kwargs
                )
                next_block_input.to("cpu")

                if not isinstance(next_block_input.args, tuple):
                    next_block_input.args = (next_block_input.args,)

            yield next_block_input

    def sample(
        self, device=None, desc: str = "Blocks processed"
    ) -> Generator[
        Tuple[
            Union[torch.nn.Module, torch.nn.ModuleList],
            List[CachedBlockInput],
            List[CachedBlockInput],
        ],
        None,
        None,
    ]:
        """
        Main generator function for blockwise sampler. Each loop of this generator yields a tuple of
        (block, [list of FP inputs to block], [list of QT inputs to block]) based on the list of blocks provided during
        initialization.
        """
        device = device if device else utils.get_device(self.sim.model)

        fp_inferences = []
        qt_inferences = []

        for sample in itertools.islice(self.dataloader, len(self.dataloader)):
            fp_inferences.append(self.run_inference(sample))
            qt_inferences.append(self.run_inference(sample))

        if self.keep_unused_blocks_on_cpu:
            self.sim.model.to("cpu")

        blocks = iter(self.blocks)
        prev_block = self.blocks[0]
        with tqdm(total=len(self.blocks), desc=desc) as pbar:
            while True:
                try:
                    block = next(blocks)

                    if self.keep_unused_blocks_on_cpu:
                        prev_block.to(device)

                    # Quantizers must be ENABLED when calculating quantized block inputs
                    qt_block_inputs = [
                        next(block_input) for block_input in qt_inferences
                    ]

                    # Quantizers must be DISABLED when calculating FP block inputs
                    with utils.disable_all_quantizers(self.sim.model):
                        fp_block_inputs = [
                            next(block_input) for block_input in fp_inferences
                        ]

                    if self.keep_unused_blocks_on_cpu:
                        prev_block.to("cpu")
                        block.to(device)

                    yield block, fp_block_inputs, qt_block_inputs

                    pbar.update(1)
                    prev_block = block
                except StopIteration:
                    break

            if self.keep_unused_blocks_on_cpu:
                block.to("cpu")
