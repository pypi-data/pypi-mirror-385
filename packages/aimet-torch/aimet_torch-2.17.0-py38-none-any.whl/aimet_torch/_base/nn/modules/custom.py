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

"""Custom modules for functional operations defined under torch and torch.nn.functional packages"""

from typing import Callable, Any, Tuple, Union, List, Type, Optional

import math
import torchvision
import torch
import torch.nn
import torch.nn.functional as F
import scipy


def forward_function_wrapper(functional: Callable) -> Any:
    """
    Wrapper function returning forward method for given functional operation.

    :param functional: torch.nn.functional
    :return: forward method
    """

    def forward(self, *args, **kwargs) -> Any:  # pylint: disable=unused-argument
        """
        Forward-pass routine for the functional operation.
        """
        return functional(*args, **kwargs)

    return forward


def create_wrapper_module(
    class_name: str, functional: Callable
) -> Type[torch.nn.Module]:
    """
    Dynamically create wrapper module for a functional operation.

    :param class_name: Name of the class.
    :param functional: Functional operation.
    """
    wrapped_module = type(
        class_name,
        (torch.nn.Module,),
        {"forward": forward_function_wrapper(functional)},
    )
    return wrapped_module


# modules for functional operations under torch package
Subtract = create_wrapper_module("Subtract", torch.sub)
Divide = create_wrapper_module("Divide", torch.div)
FloorDivide = create_wrapper_module("FloorDivide", torch.floor_divide)
MatMul = create_wrapper_module("MatMul", torch.matmul)
Norm = create_wrapper_module("Norm", torch.norm)
Exponential = create_wrapper_module("Exponential", torch.exp)
Erf = create_wrapper_module("Erf", torch.erf)
Sqrt = create_wrapper_module("Sqrt", torch.sqrt)
Maximum = create_wrapper_module("Maximum", torch.maximum)
Max = create_wrapper_module("Max", torch.max)  # NOTE: Not elementwise
AMax = create_wrapper_module("AMax", torch.amax)
Minimum = create_wrapper_module("Minimum", torch.minimum)
Min = create_wrapper_module("Min", torch.min)  # NOTE: Not elementwise
AMin = create_wrapper_module("AMin", torch.amin)
Where = create_wrapper_module("Where", torch.where)
Greater = create_wrapper_module("Greater", torch.gt)
Less = create_wrapper_module("Less", torch.lt)
GreaterEqual = create_wrapper_module("GreaterEqual", torch.ge)
LessEqual = create_wrapper_module("LessEqual", torch.le)
NotEqual = create_wrapper_module("NotEqual", torch.ne)
Equal = create_wrapper_module("Equal", torch.eq)
Bmm = create_wrapper_module("Bmm", torch.bmm)
CumSum = create_wrapper_module("CumSum", torch.cumsum)
MaskedFill = create_wrapper_module("MaskedFill", torch.Tensor.masked_fill_)
Mean = create_wrapper_module("Mean", torch.mean)
Sum = create_wrapper_module("Sum", torch.sum)
Prod = create_wrapper_module("Prod", torch.prod)
Log = create_wrapper_module("Log", torch.log)
Abs = create_wrapper_module("Abs", torch.abs)
Neg = create_wrapper_module("Neg", torch.neg)
Argmin = create_wrapper_module("Argmin", torch.argmin)
Argmax = create_wrapper_module("Argmax", torch.argmax)
ElementwiseCeil = create_wrapper_module("ElementwiseCeil", torch.ceil)
ElementwiseFloor = create_wrapper_module("ElementwiseFloor", torch.floor)
Sin = create_wrapper_module("Sin", torch.sin)
Cos = create_wrapper_module("Cos", torch.cos)
Asin = create_wrapper_module("Asin", torch.asin)
Atan = create_wrapper_module("Atan", torch.atan)
Round = create_wrapper_module("Round", torch.round)
Gather = create_wrapper_module("Gather", torch.gather)
LogicalOr = create_wrapper_module("LogicalOr", torch.logical_or)
LogicalAnd = create_wrapper_module("LogicalAnd", torch.logical_and)
LogicalNot = create_wrapper_module("LogicalNot", torch.logical_not)
Split = create_wrapper_module("Split", torch.split)
Reshape = create_wrapper_module("Reshape", torch.reshape)
Permute = create_wrapper_module("Permute", torch.permute)
Remainder = create_wrapper_module("Remainder", torch.remainder)
IndexSelect = create_wrapper_module("IndexSelect", torch.index_select)
Fmod = create_wrapper_module("Fmod", torch.fmod)
NonZero = create_wrapper_module("NonZero", torch.nonzero)
TopK = create_wrapper_module("TopK", torch.topk)
Shape = create_wrapper_module("Shape", torch.Tensor.size)
Tile = create_wrapper_module("Tile", torch.tile)
ElementwiseUnarySign = create_wrapper_module("ElementwiseUnarySign", torch.sign)
Baddbmm = create_wrapper_module("Baddbmm", torch.baddbmm)
Addmm = create_wrapper_module("Addmm", torch.addmm)
RSqrt = create_wrapper_module("RSqrt", torch.rsqrt)
Square = create_wrapper_module("Square", torch.square)
Select = create_wrapper_module("Select", torch.select)
Outer = create_wrapper_module("Outer", torch.outer)

# modules for functional operations defined under torch.nn.functional package
Interpolate = create_wrapper_module("Interpolate", torch.nn.functional.interpolate)
MaxPool2d = create_wrapper_module("MaxPool2d", torch.nn.functional.max_pool2d)
AdaptiveAvgPool2d = create_wrapper_module(
    "AdaptiveAvgPool2d", torch.nn.functional.adaptive_avg_pool2d
)
AvgPool2d = create_wrapper_module("AvgPool2d", torch.nn.functional.avg_pool2d)
BatchNorm = create_wrapper_module("BatchNorm", torch.nn.functional.batch_norm)
GroupNorm = create_wrapper_module("GroupNorm", torch.nn.functional.group_norm)
Normalize = create_wrapper_module("Normalize", torch.nn.functional.normalize)
Pad = create_wrapper_module("Pad", torch.nn.functional.pad)
GridSample = create_wrapper_module("GridSample", torch.nn.functional.grid_sample)
ScaledDotProductAttention = create_wrapper_module(
    "ScaledDotProductAttention", torch.nn.functional.scaled_dot_product_attention
)


# following modules are for overloaded operators like + and *,
# which can operate other than torch.Tensor datatype.
class Add(torch.nn.Module):
    """Add module for a functional add"""

    # pylint:disable=arguments-differ
    def forward(self, x: Any, y: Any) -> Any:
        """
        Forward-pass routine for add op
        """
        if isinstance(x, torch.Tensor) or isinstance(y, torch.Tensor):
            out = torch.add(x, y)
        else:
            out = x + y
        return out


class Multiply(torch.nn.Module):
    """Multiply module for a functional multiply"""

    # pylint:disable=arguments-differ
    def forward(self, x: Any, y: Any) -> Any:
        """
        Forward-pass routine for multiply op
        """
        if isinstance(x, torch.Tensor) or isinstance(y, torch.Tensor):
            out = torch.mul(x, y)
        else:
            out = x * y
        return out


# modules for functional requiring special handling
class Concat(torch.nn.Module):
    """Concat module for a functional concat"""

    def __init__(self, axis: int = 0):
        super().__init__()
        self._axis = axis

    # pylint:disable=arguments-differ
    def forward(self, *x) -> torch.Tensor:
        """
        Forward-pass routine for cat op
        """
        return torch.cat(x, dim=self._axis)


class DynamicConv2d(torch.nn.Module):
    """Conv2d module for a functional conv2d"""

    def __init__(self, stride=1, padding=0, dilation=1, groups=1):
        super().__init__()
        self.stride, self.padding, self.dilation, self.groups = (
            stride,
            padding,
            dilation,
            groups,
        )

    def forward(
        self, x: torch.Tensor, weight: torch.Tensor, bias: torch.Tensor = None
    ) -> torch.Tensor:
        """
        Forward-pass routine for conv2d op
        """
        return torch.nn.functional.conv2d(
            x, weight, bias, self.stride, self.padding, self.dilation, self.groups
        )


class Pow(torch.nn.Module):
    """Pow module for a functional pow"""

    # pylint:disable=arguments-differ
    def forward(self, x: Any, y: Any) -> Any:
        """
        Forward-pass routine for Pow op
        """
        return x**y


class CustomSiLU(torch.nn.Module):
    """SiLU as Sigmoid + mul"""

    def __init__(self):
        super().__init__()
        self.sigmoid = torch.nn.Sigmoid()
        self.mul = Multiply()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward-pass routine for custom SiLU
        """
        return self.mul(x, self.sigmoid(x))


class StridedSlice(torch.nn.Module):
    """Custom module for a functional slice"""

    def forward(self, *args) -> torch.Tensor:
        """
        Forward-pass routine for StridedSlice op
        """
        tensor, slice_ranges = args
        slice_params = []
        for slice_range in slice_ranges:
            slice_params.append(slice(*slice_range))
        return tensor[slice_params]


class ChannelShuffle(torch.nn.Module):
    """Custom module for a ChannelShuffle op"""

    def __init__(self, groups):
        super().__init__()
        self.groups = groups

    def forward(self, *args) -> torch.Tensor:
        """
        Forward-pass routine for ChannelShuffle op
        """
        tensor = args[0]
        n, c, h, w = tensor.shape
        return (
            tensor.view(n, self.groups, c // self.groups, h, w)
            .transpose(1, 2)
            .contiguous()
            .view(n, -1, h, w)
        )


class Cast(torch.nn.Module):
    """Cast module for a functional cast"""

    def __init__(self, dtype):
        super().__init__()
        self.dtype = dtype

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward-pass routine for cast op
        """
        return x.type(self.dtype)


class CustomGather(torch.nn.Module):
    """Custom module for ONNX Gather"""

    def forward(
        self, data: torch.Tensor, indices: torch.Tensor, axis: int = 0
    ) -> torch.Tensor:
        """
        Forward-pass routine for ONNX Gather op
        """
        target_shape = data.shape[:axis] + indices.shape + data.shape[axis + 1 :]
        indices = (indices < 0).to(indices.dtype) * data.shape[axis] + indices
        return torch.index_select(data, axis, indices.flatten()).reshape(target_shape)


class DepthToSpaceCRDMode(torch.nn.Module):
    """Depthtospace op implementation in CRD mode"""

    def __init__(self, block_size: List):
        super().__init__()
        self.block_size_h = block_size[0]
        self.block_size_w = block_size[1]

    def forward(self, x: torch.Tensor) -> Any:
        """
        Forward-pass routine for DepthToSpace op in CRD mode
        """
        b, c, h, w = x.shape
        tmp = torch.reshape(
            x,
            (
                b,
                c // (self.block_size_h * self.block_size_w),
                self.block_size_h,
                self.block_size_w,
                h,
                w,
            ),
        )
        tmp = torch.permute(tmp, (0, 1, 4, 2, 5, 3))
        out = torch.reshape(
            tmp,
            (
                b,
                c // (self.block_size_h * self.block_size_w),
                h * self.block_size_h,
                w * self.block_size_w,
            ),
        )
        return out


class DepthToSpaceDCRMode(torch.nn.Module):
    """Depthtospace op implementation in DCR mode"""

    # This class is created because Pytorch as of now doesn't have option
    # to run DCR mode in PixelShuffle op.
    def __init__(self, block_size: int):
        super().__init__()
        self.block_size = block_size

    def forward(self, x: torch.Tensor) -> Any:
        """
        Forward-pass routine for DepthToSpace op in DCR mode
        """
        b, c, h, w = x.shape
        blocksize = self.block_size
        tmp = torch.reshape(x, (b, blocksize, blocksize, c // (blocksize**2), h, w))
        tmp = torch.permute(tmp, (0, 3, 4, 1, 5, 2))
        out = torch.reshape(tmp, (b, c // (blocksize**2), h * blocksize, w * blocksize))
        return out


class ScatterND(torch.nn.Module):
    """ScatterND op implementation"""

    def __init__(self, reduction: int = 0):
        super().__init__()
        self.reduction = reduction

    def forward(
        self, data: torch.Tensor, indices: torch.Tensor, updates: torch.Tensor
    ) -> torch.Tensor:
        """
        Forward-pass routine for ScatterND op
        """
        output = torch.clone(data)

        if self.reduction == 1:
            f = torch.add
        elif self.reduction == 2:
            f = torch.mul
        else:
            f = None

        indices = indices.type(torch.int64)
        idx_list = indices.split(split_size=1, dim=-1)
        if f:
            output[idx_list] = f(
                output[idx_list], updates.reshape(output[idx_list].shape)
            )
        else:
            output[idx_list] = updates.reshape(output[idx_list].shape)
        return output


class RoiAlign(torch.nn.Module):
    """Custom module for ONNX RoiAlign"""

    def __init__(
        self,
        output_size: Union[int, Tuple[int, int]],
        spatial_scale: float,
        sampling_ratio: int,
    ):
        super().__init__()
        self.output_size = output_size
        self.spatial_scale = spatial_scale
        self.sampling_ratio = sampling_ratio

    def forward(
        self, inp: torch.Tensor, roi: torch.Tensor, batch_indices: torch.Tensor
    ) -> torch.Tensor:
        """
        Forward-pass routine for RoiAlign
        """
        roi = torch.cat(
            (torch.reshape(batch_indices, (batch_indices.shape[0], 1)), roi), dim=1
        )
        return torchvision.ops.roi_align(
            inp, roi, self.output_size, self.spatial_scale, self.sampling_ratio
        )


class NonMaxSuppression(torch.nn.Module):
    """
    Implementation of NMS Op in the form of nn.Module
    """

    def __init__(
        self,
        iou_threshold: float,
        score_threshold: float,
        max_output_boxes_per_class: int,
    ):
        super().__init__()
        self.iou_threshold = iou_threshold
        self.score_threshold = score_threshold
        self.max_output_boxes_per_class = max_output_boxes_per_class

    @staticmethod
    def _modify_y1x1y2x2_to_x1y1x2y2(boxes):
        return boxes[:, torch.tensor([1, 0, 3, 2])]

    def forward(self, *args) -> torch.Tensor:
        """
        Forward-pass routine for NMS op
        """
        batches_boxes = args[0]
        batch_scores = args[1]

        res = []
        for index, (boxes, scores) in enumerate(zip(batches_boxes, batch_scores)):
            for class_index, classes_score in enumerate(scores):
                nms_output = self.perform_nms_per_class(boxes, classes_score)
                res_per_class = []
                for val in nms_output:
                    res_per_class.append([index, class_index, val.detach()])
                res_per_class = res_per_class[: self.max_output_boxes_per_class]
                res.extend(res_per_class)

        res = torch.tensor(res, dtype=torch.int64, device=args[0].device)
        out = torch.zeros(
            batch_scores.shape[0]
            * batch_scores.shape[1]
            * self.max_output_boxes_per_class,
            3,
            dtype=torch.int64,
            device=args[0].device,
        )
        indices = torch.arange(
            0, len(res) * 3, dtype=torch.int64, device=args[0].device
        )
        out.put_(indices, res)
        return out

    def perform_nms_per_class(
        self, boxes: torch.Tensor, classes_score: torch.Tensor
    ) -> torch.Tensor:
        """
        Performs NMS per class
        :param boxes: boxes on which NMS should be performed
        :param classes_score: corresponding class scores for the boxes
        :return: returns box indices filtered out by NMS
        """
        filtered_score_ind = (classes_score > self.score_threshold).nonzero()[:, 0]
        filtered_boxes = boxes[filtered_score_ind]
        filtered_classes_score = classes_score[filtered_score_ind]
        res_ = torchvision.ops.nms(
            self._modify_y1x1y2x2_to_x1y1x2y2(filtered_boxes),
            filtered_classes_score,
            self.iou_threshold,
        )
        return filtered_score_ind[res_]


class GatherNd(torch.nn.Module):
    """GatherNd op implementation"""

    # This class is created because Pytorch as of now doesn't have support for this OP
    def __init__(self, batch_dim: int):
        super().__init__()
        self.batch_dims = batch_dim

    def forward(self, data: torch.Tensor, indices: torch.Tensor) -> torch.Tensor:
        """
        Forward-pass routine for GatherNd op
        """
        if self.batch_dims == 0:
            return self._gather_nd(data, indices)

        data_rank = len(data.shape)

        assert indices.shape[-1] <= data_rank

        batch_dims_shape = []

        batch_dims_size = 1

        for i in range(self.batch_dims):
            batch_dims_shape.append(indices.shape[i])
            batch_dims_size *= indices.shape[i]

        output_shape = (
            batch_dims_shape + list(indices.shape)[self.batch_dims : -1]
            if (indices.shape[-1] == data_rank - self.batch_dims)
            else batch_dims_shape
            + list(indices.shape)[self.batch_dims : -1]
            + list(data.shape)[self.batch_dims + indices.shape[-1] :]
        )

        if torch.jit.is_tracing():
            return torch.zeros(*output_shape, device=data.device)

        output_data_buffer = []

        reshaped_indices = indices.reshape(batch_dims_size, -1, indices.shape[-1])

        reshaped_data = data.reshape((batch_dims_size,) + data.shape[self.batch_dims :])

        for batch_dim in range(reshaped_indices.shape[0]):
            for outer_dim in range(reshaped_indices.shape[1]):
                gather_index = tuple(reshaped_indices[batch_dim][outer_dim])
                output_data_buffer.append(reshaped_data[(batch_dim, *gather_index)])

        if output_data_buffer[0].dim() == 0:
            return torch.tensor(output_data_buffer, device=data.device).reshape(
                output_shape
            )
        return torch.cat(output_data_buffer).reshape(output_shape)

    @staticmethod
    def _gather_nd(data: torch.Tensor, indices: torch.Tensor) -> torch.Tensor:
        """
        GatherNd operation for batch_dim=0 case

        :param data: Tensor to gather values
        :param indices: Index tensor to be used to gather values
        :return: Tensor after GatherNd operation
        """
        data_rank, m = len(data.shape), indices.shape[-1]
        assert m <= data_rank, (
            f"m: {m} should be less than or equal to data_rank: {data_rank}"
        )

        total_samples = indices.shape[:-1].numel()
        output_shape = indices.shape[:-1] + data.shape[m:]
        reshaped_indices = torch.split(
            tensor=indices.reshape(total_samples, m).transpose(0, 1),
            split_size_or_sections=1,
        )

        return data[reshaped_indices].reshape(output_shape).contiguous()


class ScatterElements(torch.nn.Module):
    """ScatterElements op implementation"""

    def __init__(self, dim: int, reduce: str = None):
        super().__init__()

        self.dim = dim
        self.reduce = reduce

    def forward(
        self,
        x: Union[torch.Tensor, list],
        index: Union[torch.Tensor, list],
        src: Union[torch.Tensor, list],
    ):
        """
        Forward-pass routine for ScatterElements op
        """
        if isinstance(index, list):
            index = torch.tensor(index, dtype=torch.int64)
        if isinstance(src, list):
            src = torch.tensor(src)
        if isinstance(x, list):
            x = torch.tensor(x, dtype=src.dtype)

        if self.reduce:
            if isinstance(src, torch.Tensor):
                return x.scatter_reduce(self.dim, index, src, self.reduce)
            # If src is a single float value
            return x.scatter(self.dim, index, src, reduce=self.reduce)

        return x.scatter(self.dim, index, src)


class OneHot(torch.nn.Module):
    """Custom module for ONNX OneHot"""

    def __init__(
        self,
        num_classes: int,
        off_value: Union[int, float],
        on_value: Union[int, float],
    ):
        super().__init__()
        self.num_classes = num_classes
        self.off_value = off_value
        self.on_value = on_value

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        """
        Forward-pass routine for OneHot
        """
        out = torch.nn.functional.one_hot(inputs, self.num_classes)
        if self.off_value != 0 or self.on_value != 1:
            out = out * (self.on_value - self.off_value) + self.off_value
        return out


class Expand(torch.nn.Module):
    """Custom module for a Expand op"""

    def forward(self, tensor: torch.Tensor, *args) -> torch.Tensor:
        """
        Forward-pass routine for Expand op
        """
        return tensor.expand(*args)


class DynamicLinear(torch.nn.Module):
    """Custom module for Dynamic Linear / FullyConnected Op"""

    def forward(
        self, x: torch.Tensor, weight: torch.Tensor, bias: torch.Tensor = None
    ) -> torch.Tensor:
        """
        Forward-pass routine for Dynamic Linear Op
        """
        return torch.nn.functional.linear(x, weight, bias)


# TODO: Can be removed once AIMET supports torch >= 2.4
class RmsNorm(torch.nn.Module):
    """Custom module for RmsNorm"""

    def __init__(self, input_shape: list, axes: list, epsilon: float):
        super().__init__()
        self.epsilon = epsilon
        self.axes = axes
        normalized_shape = tuple(input_shape[i] for i in axes)
        self.weight = torch.nn.Parameter(torch.ones(normalized_shape))
        self.bias = torch.nn.Parameter(torch.zeros(normalized_shape))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass for RmsNorm
        """
        input_dtype = x.dtype
        x = x.to(dtype=torch.float32, copy=True)
        squared_mean = torch.mean(x * x, dim=self.axes, keepdim=True)
        rms = torch.sqrt(squared_mean + self.epsilon)
        res = (torch.div(x, rms) * self.weight + self.bias).to(dtype=input_dtype)
        return res


class HadamardRotation(torch.nn.Module):
    """Custom module for Hadamard Rotation"""

    scale: float

    def __init__(self, size: int, scale: Optional[float] = None):
        super().__init__()
        num_two_factors = 0
        remaining_factor = size
        while remaining_factor & 1 == 0:
            remaining_factor = remaining_factor >> 1
            num_two_factors += 1
        self.register_buffer(
            "hadamard",
            torch.tensor(
                scipy.linalg.hadamard(2**num_two_factors), dtype=torch.float32
            ),
        )
        if scale:
            self.scale = scale
        else:
            hadamard_rank = self.hadamard.shape[0]
            self.scale = 1 / math.sqrt(hadamard_rank)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        hadamard_rank = self.hadamard.shape[0]
        n_groups = x.shape[-1] // hadamard_rank
        x_reshape = x.reshape(*x.shape[:-1], n_groups, hadamard_rank)
        return (F.linear(x_reshape, self.hadamard) * self.scale).reshape(x.shape)


class NullRequant(Reshape):
    """Custom module for nullrequant"""

    # pylint:disable=arguments-differ, missing-function-docstring, redefined-builtin
    def forward(self, input: torch.Tensor, shape: List) -> torch.Tensor:
        if torch.jit.is_tracing():
            # Avoid graph optimization in `torch.onnx.utils._optimize_graph`
            # for multiple Reshape ops when sim.export()
            return super().forward(input, shape)
        return super().forward(input, input.shape)


_spconv_custom_module_names = (
    "CustomSparseConv3d",
    "CustomSparseConv3d_WithIndicesFeatures",
    "CustomSparseConv3DLayer",
    "SparseTensorWrapper",
    "CustomScatterDense",
    "ScatterDense",
)


def _lazy_import_spconv():
    # pylint: disable=import-outside-toplevel
    from aimet_torch._base.nn.modules import _spconv

    globals().update(
        {
            cls_name: getattr(_spconv, cls_name)
            for cls_name in _spconv_custom_module_names
        }
    )


def __getattr__(name: str):
    if name in _spconv_custom_module_names:
        _lazy_import_spconv()

    try:
        return globals()[name]
    except KeyError as e:
        msg = f"module '{__name__}' has no attribute '{name}'"
        raise AttributeError(msg) from e
