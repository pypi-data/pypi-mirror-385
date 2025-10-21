# /usr/bin/env python
# -*- mode: python -*-
# =============================================================================
#  @@-COPYRIGHT-START-@@
#
#  Copyright (c) 2024, Qualcomm Innovation Center, Inc. All rights reserved.
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
"""Sequential MSE implementation"""

from typing import List, Optional, Tuple, Callable, overload
import contextlib
import copy
import warnings
import torch
from torch.utils.data import DataLoader

from aimet_common.utils import AimetLogger, _red
from aimet_torch._base.seq_mse import SequentialMseBase, SeqMseParams, SUPPORTED_MODULES
from aimet_torch.v2.quantization.base import QuantizerBase
from aimet_torch.v2.quantization.affine import (
    AffineQuantizerBase,
    QuantizeDequantize,
    GroupedBlockQuantizeDequantize,
)
from aimet_torch.utils import place_model, get_device
from aimet_torch.v2.utils import (
    default_forward_fn,
    remove_all_quantizers,
)
from aimet_torch.v2.nn.base import BaseQuantizationMixin
from aimet_torch.v2.quantsim import QuantizationSimModel
from aimet_torch.v2.deepspeed_utils import SafeGatheredParameters
from .utils import remove_activation_quantizers, remove_param_quantizers

__all__ = [
    "SequentialMse",
    "SeqMseParams",
    "apply_seq_mse",
    "get_candidates",
    "optimize_module",
]

_logger = AimetLogger.get_area_logger(AimetLogger.LogAreas.SeqMse)


@overload
def apply_seq_mse(
    sim: QuantizationSimModel,
    data_loader: DataLoader,
    num_candidates: int = 20,
    forward_fn: Callable = default_forward_fn,
    modules_to_exclude: Optional[List[torch.nn.Module]] = None,
    checkpoints_config: Optional[str] = None,
): ...


@overload
def apply_seq_mse(
    model: torch.nn.Module,
    sim: QuantizationSimModel,
    data_loader: DataLoader,
    params: SeqMseParams,
    modules_to_exclude: Optional[List[torch.nn.Module]] = None,
    checkpoints_config: Optional[str] = None,
):
    # Deprecated
    ...


def apply_seq_mse(*args, **kwargs):
    """
    Sequentially minimizing activation MSE loss in layer-wise way to decide optimal param quantization encodings.

        1 Disable all input/output quantizers, param quantizers of non-supported modules
        2 Find and feeze optimal parameter encodings candidate for remaining supported modules
        3 Re-enable disabled quantizers from step 1

    Example userflow:
    model = Model().eval()
    sim = QuantizationSimModel(...)
    apply_seq_mse(...)
    sim.compute_encodings(...) [compute encodings for all activations and parameters of non-supported modules]
    sim.export(...)

    NOTE: modules in modules_to_exclude won't be quantized and skipped when applying sequential MSE.

    :param sim: QuantizationSimModel object
    :param data_loader: Data loader
    :param num_candidates: Number of candidate encodings to evaluate for each layer
    :param forward_fn: callback function to perform forward pass given accepts model, inputs
    :param modules_to_exclude: List of supported type module(s) to exclude when applying Sequential MSE
    :param checkpoints_config: Config files to split fp32/quant model by checkpoints to speedup activations sampling
    """
    if "model" in kwargs or (args and isinstance(args[0], torch.nn.Module)):
        warnings.warn(
            _red(
                "apply_seq_mse was called using a deprecated function signature. This will raise an error in future releases."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        return SequentialMse.apply_seq_mse(*args, **kwargs)

    return _apply_seq_mse(*args, **kwargs)


def _apply_seq_mse(
    sim: QuantizationSimModel,
    data_loader: DataLoader,
    num_candidates: int = 20,
    forward_fn: Callable = default_forward_fn,
    modules_to_exclude: Optional[List[torch.nn.Module]] = None,
    checkpoints_config: Optional[str] = None,
):
    params = SeqMseParams(
        num_batches=None,
        num_candidates=num_candidates,
        forward_fn=forward_fn,
        inp_symmetry=SequentialMse.inp_symmetry,
        loss_fn=SequentialMse.loss_fn,
    )

    with (
        place_model(sim.model, torch.device("cpu")),
        remove_all_quantizers(sim.model),
    ):
        weight_shared_fp_model = _copy_as_fp_model_with_shared_weights(sim.model)

    model_device = get_device(sim.model)
    with place_model(weight_shared_fp_model, model_device):
        return SequentialMse.apply_seq_mse(
            model=weight_shared_fp_model,
            sim=sim,
            data_loader=data_loader,
            params=params,
            modules_to_exclude=modules_to_exclude,
            checkpoints_config=checkpoints_config,
        )


class SequentialMse(SequentialMseBase):
    """
    Sequentially minimizing activation MSE loss in layer-wise way to decide optimal param quantization encodings.
    """

    inp_symmetry: str = "symqt"
    loss_fn: str = "mse"

    @classmethod
    def apply_seq_mse(
        cls,
        model: torch.nn.Module,
        sim: QuantizationSimModel,
        data_loader: DataLoader,
        params: SeqMseParams,
        modules_to_exclude: Optional[List[torch.nn.Module]] = None,
        checkpoints_config: Optional[str] = None,
    ):
        if not modules_to_exclude:
            modules_to_exclude = []
        modules_to_exclude.extend(
            cls._get_grouped_convs_with_blockwise_quantization(sim)
        )
        with cls._handle_grouped_block_quantizers(sim):
            super().apply_seq_mse(
                model, sim, data_loader, params, modules_to_exclude, checkpoints_config
            )

    @staticmethod
    def _get_grouped_convs_with_blockwise_quantization(sim):
        """Return a list of all grouped conv modules using blockwise quantization for weights"""
        grouped_convs_with_blockwise_quantization = []
        for module in sim.model.modules():
            if (
                isinstance(module, torch.nn.Conv2d)
                and isinstance(module, BaseQuantizationMixin)
                and module.groups != 1
                and module.param_quantizers["weight"].block_size is not None
                and module.param_quantizers["weight"].block_size[1]
                != module.weight.shape[1]
            ):
                grouped_convs_with_blockwise_quantization.append(module)
        return grouped_convs_with_blockwise_quantization

    @staticmethod
    @contextlib.contextmanager
    def _handle_grouped_block_quantizers(sim: QuantizationSimModel):
        """Set all grouped block quantizers to regular blockwise quantization for the duration of the context manager"""
        grouped_block_quantize_dequantizers = []
        for module in sim.model.modules():
            if isinstance(module, GroupedBlockQuantizeDequantize):
                grouped_block_quantize_dequantizers.append(
                    (module, module.block_grouping)
                )
                module.block_grouping = tuple(1 for _ in enumerate(module.shape))

        yield

        for module, block_grouping in grouped_block_quantize_dequantizers:
            module.block_grouping = block_grouping

    @classmethod
    def compute_all_param_encodings(cls, sim: QuantizationSimModel):
        """
        Compute encodings for all parameters, needed for initializing Sequential MSE

        :param sim: Quant sim
        """
        for _, qmodule in sim.named_qmodules():
            qmodule._compute_param_encodings(overwrite=True)  # pylint: disable=protected-access

    @classmethod
    @contextlib.contextmanager
    def temporarily_disable_quantizers(
        cls,
        model: torch.nn.Module,
        sim: QuantizationSimModel,
        modules_to_exclude: Optional[List[torch.nn.Module]],
    ):
        """
        For given quantsim model, disable quantizers needed to be diabled before applying sequential MSE.

        :param model: Original fp32 model
        :param sim: QuantizationSimModel object
        :param modules_to_exclude: List of supported modules to exclude when applying Sequential MSE
        :return: List of quantizers to be disabled.
        """
        # pylint: disable=protected-access
        fp_modules_to_exclude = set(modules_to_exclude or [])
        qmodules_to_exclude = set(
            sim.model.get_submodule(name)
            for name, fp_module in model.named_modules()
            if fp_module in fp_modules_to_exclude
        )

        with contextlib.ExitStack() as stack:
            for _, qmodule in sim.named_qmodules():
                ctx = remove_activation_quantizers(qmodule)
                stack.enter_context(ctx)

                if (
                    not isinstance(qmodule, SUPPORTED_MODULES)
                    or qmodule in qmodules_to_exclude
                ):
                    ctx = remove_param_quantizers(qmodule)
                    stack.enter_context(ctx)

            yield

    @classmethod
    def compute_param_encodings(
        cls, quantizer: QuantizerBase, x_min: torch.Tensor, x_max: torch.Tensor
    ):
        """
        Compute encodings for parameter quantizer using given x_min and x_max values.

        :param quantizer: Tensor quantizer
        :param x_min: min values
        :param x_max: max values
        """
        quantize_dequantize = QuantizeDequantize(
            quantizer.shape,
            quantizer.bitwidth,
            quantizer.symmetric,
            block_size=quantizer.block_size,
        ).to(x_min.device)

        min_tensor = x_min
        max_tensor = x_max
        if quantizer.block_size:
            for axis, blk_size in enumerate(quantizer.block_size):
                if blk_size == -1:
                    continue
                min_tensor = min_tensor.repeat_interleave(blk_size, axis)
                max_tensor = max_tensor.repeat_interleave(blk_size, axis)

        with quantize_dequantize.compute_encodings():
            _ = quantize_dequantize(torch.stack([min_tensor, max_tensor]))  # pylint: disable=not-callable
            # (pylint throws a false alarm)

        quantizer.set_range(quantize_dequantize.min, quantize_dequantize.max)

    @classmethod
    def _is_symmetric_quantizer(cls, quantizer: AffineQuantizerBase):
        # pylint: disable=protected-access
        return quantizer._symmetric

    @classmethod
    def _freeze_quantizer_encoding(cls, quantizer: QuantizerBase):
        # pylint: disable=protected-access
        quantizer.requires_grad_(False)
        quantizer.allow_overwrite(False)

    @classmethod
    def _get_quantized_weight(cls, quant_module: BaseQuantizationMixin):
        w = quant_module.weight
        return quant_module.param_quantizers["weight"](w)

    @classmethod
    def _get_original_module(cls, quant_module: BaseQuantizationMixin):
        return quant_module

    @staticmethod
    def _get_input_channel_block_size(quant_module):
        if not isinstance(quant_module, (torch.nn.Linear, torch.nn.Conv2d)):
            raise NotImplementedError("Unsupported module type: ", type(quant_module))
        if quant_module.param_quantizers["weight"].block_size is None:
            # Per tensor or per channel case. For either one, treat loss computation as per channel
            return quant_module.weight.shape[1]
        return (
            quant_module.weight.shape[1]
            // quant_module.param_quantizers["weight"].shape[1]
        )

    @staticmethod
    def _get_indices_to_reduce(block_size, reshaped_weight):
        """
        Return indices in reshaped_weight corresponding to block_sizes. Reshaped_weight is expected to contain
        alternating dimensions of num_blocks and block_sizes.
        """
        indices_to_reduce = []
        for idx, _ in enumerate(block_size):
            indices_to_reduce.insert(0, (len(reshaped_weight.shape) - 2 * idx) - 1)
        return indices_to_reduce

    @classmethod
    def get_min_and_max_for_candidate_selection(
        cls, quant_module: BaseQuantizationMixin
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Get min/max values for candidate selection.

        :param quant_module: Quant module to be optimized
        :return: Tuple of min and max values for candidate selection.
        """
        # pylint: disable=protected-access
        assert hasattr(quant_module.param_quantizers["weight"], "block_size")
        if not isinstance(quant_module, (torch.nn.Conv2d, torch.nn.Linear)):
            raise ValueError("Unsupported module: ", quant_module)

        max_tensor = quant_module.param_quantizers["weight"].get_max()
        min_tensor = quant_module.param_quantizers["weight"].get_min()

        return min_tensor, max_tensor

    @classmethod
    def _get_candidate(
        cls,
        candidate_idx: int,
        num_candidates: int,
        min_tensor: torch.Tensor,
        max_tensor: torch.Tensor,
    ):
        """
        Get candidate min and max tensors
        """
        cand_max = max_tensor / num_candidates * (candidate_idx + 1)
        cand_min = min_tensor / num_candidates * (candidate_idx + 1)
        return cand_min, cand_max

    @classmethod
    def _compute_loss(
        cls,
        quant_module: BaseQuantizationMixin,
        x: torch.Tensor,
        xq: torch.Tensor,
        w: torch.Tensor,
        wq: torch.Tensor,
        params: SeqMseParams,
    ) -> torch.Tensor:
        """
        Compute loss for the given (x, w) and (xq, wq) input/weight pairs. Assumes that block size will be on
        input_channel dimension.
        """
        # pylint: disable=too-many-locals
        block_size = cls._get_input_channel_block_size(quant_module)

        if isinstance(quant_module, torch.nn.Linear):
            # General strategy (Linear):
            # Compute blockwise reconstruction loss using batched matrix multiplication
            out_channels = quant_module.weight.shape[0]
            in_channels = quant_module.weight.shape[1]
            num_blocks = in_channels // block_size

            # Reshape and permute x and w
            #                  reshape                     permute
            #   * x: (N,    Cin) -> (N,    NUM_BLK, BLK_SIZE) -> (NUM_BLK, N, BLK_SIZE)
            #   * w: (Cout, Cin) -> (Cout, NUM_BLK, BLK_SIZE) -> (NUM_BLK, BLK_SIZE, Cout)
            x = x.reshape(-1, num_blocks, block_size).permute(1, 0, 2)
            w = w.reshape(out_channels, num_blocks, block_size).permute(1, 2, 0)
            xq = xq.reshape(-1, num_blocks, block_size).permute(1, 0, 2)
            wq = wq.reshape(out_channels, num_blocks, block_size).permute(1, 2, 0)

            # Blockwise batched matmul
            #           xw        =           x            @           w
            #  (NUM_BLK, N, Cout)   (NUM_BLK, N, BLK_SIZE)   (NUM_BLK, BLK_SIZE, Cout)
            xw = torch.bmm(x, w)
            xqwq = torch.bmm(xq, wq)

            # Permute to restore axis 0 back to batch dimension
            #                          permute
            #   * xw: (NUM_BLK, N, Cout) -> (N, Cout, NUM_BLK)
            xw = xw.permute(1, 2, 0)
            xqwq = xqwq.permute(1, 2, 0)

            loss = (
                params.get_loss_fn()(xw, xqwq, reduction="none")
                .sum(0)
                .view(out_channels, num_blocks)
            )
            return loss

        # General strategy (Conv):
        # Split weights and input per block, and run a separate forward pass for each split.
        # In the case of per tensor and per channel, the entire input channel is treated as one block.

        # NOTE: Similar to Linear, convolution can be also vectorized with depthwise grouped conv.
        #       However, vectorizing convolution in this manner harms the performance
        #       because PyTorch grouped convolution kernels are much slower than regular convolution
        assert isinstance(quant_module, torch.nn.Conv2d)
        w_blocks = torch.split(w, block_size, dim=1)
        wq_blocks = torch.split(wq, block_size, dim=1)
        groups = quant_module.groups
        x_blocks = torch.split(x, block_size * groups, dim=-3)
        xq_blocks = torch.split(xq, block_size * groups, dim=-3)

        block_losses = []
        for idx, x_block in enumerate(x_blocks):
            xqwq, xw = cls.compute_outputs(
                quant_module, x_block, xq_blocks[idx], w_blocks[idx], wq_blocks[idx]
            )
            block_losses.append(cls.compute_recon_loss(xqwq, xw, params))
        # Stack losses in the input channel dimension
        block_losses = torch.stack(block_losses, dim=-1)
        return block_losses

    @classmethod
    def optimize_module(
        cls,
        quant_module: BaseQuantizationMixin,
        x: torch.Tensor,
        xq: torch.Tensor,
        params: SeqMseParams,
    ):
        """
        Find and freeze optimal parameter encodings candidate for given module.

        :param quant_module: Quant module to be optimized
        :param x: Inputs to module from FP32 model
        :param xq: Inputs to module from QuantSim model
        :param params: Sequenial MSE parameters
        """
        # pylint: disable=too-many-locals
        with SafeGatheredParameters(quant_module.parameters(recurse=True)):
            min_tensor, max_tensor = cls.get_min_and_max_for_candidate_selection(
                quant_module
            )

            total_loss = []
            for i in range(params.num_candidates):
                cand_min, cand_max = cls._get_candidate(
                    i, params.num_candidates, min_tensor, max_tensor
                )
                cls.compute_param_encodings(
                    quant_module.param_quantizers["weight"], cand_min, cand_max
                )
                w = quant_module.weight
                wq = cls._get_quantized_weight(quant_module)
                with torch.no_grad():
                    loss = 0
                    for batch_idx, (batch_x, batch_xq) in enumerate(zip(x, xq)):
                        if params.num_batches and batch_idx >= params.num_batches:
                            break
                        loss += cls._compute_loss(
                            quant_module, batch_x, batch_xq, w, wq, params
                        )
                    total_loss.append(loss)

            best_indices = torch.stack(total_loss).min(0)[1]

        # Unsqueeze best_indices until it matches dim length of max_tensor
        while best_indices.dim() < max_tensor.dim():
            best_indices = best_indices[..., None]

        min_tensor, max_tensor = cls._get_candidate(
            best_indices, params.num_candidates, min_tensor, max_tensor
        )

        # Compute and freeze parameter encodings using best candidate
        cls.compute_param_encodings(
            quant_module.param_quantizers["weight"], min_tensor, max_tensor
        )
        cls._freeze_quantizer_encoding(quant_module.param_quantizers["weight"])


def _copy_as_fp_model_with_shared_weights(model):
    new_model = copy.copy(model)
    # pylint: disable=protected-access
    new_model._modules = copy.copy(new_model._modules)
    new_model._parameters = copy.copy(new_model._parameters)
    new_model._buffers = copy.copy(new_model._buffers)
    for name, child in model.named_children():
        if isinstance(child, BaseQuantizationMixin):
            setattr(new_model, name, child.get_original_module())
        else:
            setattr(new_model, name, _copy_as_fp_model_with_shared_weights(child))
    return new_model


# Global variables for compatibility
get_candidates = SequentialMse.get_candidates
optimize_module = SequentialMse.optimize_module
