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
# pylint: disable=redefined-builtin
"""Affine encoding definition"""

from typing import Tuple, Optional, Dict, Any, overload, Union, List
from itertools import chain, repeat
import math
import torch
from torch._C._nn import _parse_to as parse_to_args

from aimet_common.defs import EncodingType
from aimet_common.quantsim import VALID_ENCODING_VERSIONS
from aimet_torch.v2.utils import docstring
from aimet_torch.v2.quantization.base import EncodingBase
from aimet_torch.v2.quantization.affine.backends import (
    quantize,
    dequantize,
    _derive_qmin_qmax,
)
from ._utils import _GridMixin, _register_signature


__all__ = ["AffineEncoding", "VectorEncoding", "GroupedBlockEncoding"]


class AffineEncoding(EncodingBase, _GridMixin):
    """
    Encoding object for affine quantization
    """

    _init_signatures = []

    @overload
    @_register_signature(_init_signatures)
    def __init__(
        self,
        scale: torch.Tensor,
        offset: torch.Tensor,
        qmin: int,
        qmax: int,
        symmetry=False,
        block_size: Optional[Tuple[int, ...]] = None,
        zero_point_shift: Optional[float] = None,
    ): ...

    @overload
    @_register_signature(_init_signatures)
    def __init__(
        self,
        scale: torch.Tensor,
        offset: torch.Tensor,
        bitwidth: int,
        signed=False,
        symmetry=False,
        block_size: Optional[Tuple[int, ...]] = None,
        zero_point_shift: Optional[float] = None,
    ): ...

    def __init__(self, scale: torch.Tensor, offset: torch.Tensor, *args, **kwargs):  # pylint: disable=too-many-locals
        self._scale = scale
        self._offset = offset
        full_args = (scale, offset, *args)

        # Pad positional args with None's such that len(args) == 5
        args = tuple(chain(args, repeat(None, 5 - len(args))))
        arg0 = kwargs.pop("qmin", kwargs.pop("bitwidth", args[0]))
        arg1 = kwargs.pop("qmax", kwargs.pop("signed", args[1]))
        symmetry = kwargs.pop("symmetry", args[2])
        if symmetry is None:
            symmetry = False
        block_size = kwargs.pop("block_size", args[3])
        zero_point_shift = kwargs.pop("zero_point_shift", args[4])

        if arg1 is None or isinstance(arg1, bool):
            # (arg0, arg1) == (bitwidth, signed)
            bitwidth, signed = arg0, bool(arg1)
            if (bitwidth is None) or (signed is None):
                raise self._arg_parsing_error(full_args, kwargs)
            qmin, qmax = _derive_qmin_qmax(bitwidth=bitwidth, signed=signed)
        else:
            # (arg0, arg1) == (qmin, qmax)
            qmin, qmax = arg0, arg1
            if (qmin is None) or (qmax is None):
                raise self._arg_parsing_error(full_args, kwargs)

        assert qmin is not None
        assert qmax is not None

        if kwargs:
            cls = type(self).__qualname__
            unexpected_keys = ", ".join(kwargs.keys())
            raise TypeError(
                f"{cls}.__init__ got unexpected keyword argument: {unexpected_keys}"
            )

        if qmin >= qmax:
            raise ValueError(
                f"qmax should be strictly larger than qmin. Got qmax={qmax}, qmin={qmin}"
            )

        self.qmin = qmin
        self.qmax = qmax
        self._symmetry = symmetry
        self._block_size = block_size
        self._zero_point_shift = zero_point_shift or 0.0
        if self._zero_point_shift not in [0.0, 0.5]:
            raise ValueError(
                f"zero_point_shift should be 0.0 or 0.5. Got {self._zero_point_shift}"
            )

    @property
    def mapping(self) -> str:
        """
        Returns the mapping method for this encoding
        """
        return "affine"

    @property
    def granularity(self) -> str:
        """
        Returns the granularity of the quantizer encoding
        """
        if self.scale.dim() == 0:
            return "pertensor"
        if self.block_size is not None:
            return "blockwise"
        non_singleton_dims = tuple(dim for dim in self.scale.shape if dim > 1)
        if len(non_singleton_dims) <= 1:
            return "perchannel"
        return "unknown"

    @property
    def scale(self) -> torch.Tensor:
        """
        Returns the scale of the quantizer encoding
        """
        return self._scale

    @property
    def offset(self) -> torch.Tensor:
        """
        Returns the offset of the quantizer encoding
        """
        return self._offset

    @property
    def num_steps(self) -> int:
        """
        Returns the number of steps of the quantizer encoding
        """
        return self.qmax - self.qmin

    @property
    def min(self) -> torch.Tensor:
        """
        Returns the min value of the quantizer encoding
        """
        return (self.offset + self.qmin) * self.scale

    @property
    def max(self) -> torch.Tensor:
        """
        Returns the max value of the quantizer encoding
        """
        return (self.offset + self.qmax) * self.scale

    @property
    def symmetry(self) -> bool:
        """
        Returns the symmetry mode of the quantizer encoding
        """
        return self._symmetry

    @property
    @docstring(_GridMixin._get_bitwidth.__doc__)
    def bitwidth(self) -> int:  # pylint: disable=missing-function-docstring
        return self._get_bitwidth()

    @bitwidth.setter
    def bitwidth(self, bitwidth: int):
        self._set_bitwidth(bitwidth)

    @property
    @docstring(_GridMixin._get_signed.__doc__)
    def signed(self) -> bool:  # pylint: disable=missing-function-docstring
        return self._get_signed()

    @signed.setter
    def signed(self, signed: bool):
        self._set_signed(signed)

    @property
    def dtype(self) -> torch.dtype:
        """
        Returns the dtype of the quantizer encoding
        """
        if 0 <= self.qmin < self.qmax < 2**8:
            return torch.uint8

        if -(2**7) <= self.qmin < self.qmax < 2**7:
            return torch.int8

        if -(2**15) <= self.qmin < self.qmax < 2**15:
            return torch.int16

        return torch.int32

    def _get_export_dtype(self) -> str:  # pylint: disable=too-many-return-statements
        nbits = math.ceil(math.log2(self.qmax - self.qmin + 1))
        signed = self.qmin < 0 <= self.qmax

        if signed:
            dtype_str = f"int{nbits}"
        else:
            dtype_str = f"uint{nbits}"

        return dtype_str

    @property
    def block_size(self) -> Optional[Tuple[int, ...]]:
        """
        Returns the block sizes of the quantizer encoding
        """
        return self._block_size

    @property
    def zero_point_shift(self) -> float:
        """
        Shifts tensor by a factor of scale before performing quantize/dequantize
        """
        return self._zero_point_shift

    def to(self, *args, **kwargs):
        """
        Changes dtype of data in quantizer encoding or device where the data is.
        Behaves similar to torch.Tensor.to
        """
        to_args = parse_to_args(*args, **kwargs)
        device, dtype, _, _ = to_args
        dtype = dtype if dtype else self._scale.dtype
        device = device if device else self._scale.device
        if dtype is self._scale.dtype and device is self._scale.device:
            return self

        if not dtype.is_floating_point:
            raise RuntimeError(
                f"Cannot change encoding data dtype to {dtype}, "
                "only floating point data types are supported"
            )

        scale = self._scale.to(dtype=dtype, device=device)
        offset = self._offset.to(dtype=dtype, device=device)
        properties = self._get_additional_properties()
        return type(self)(
            scale, offset, self.qmin, self.qmax, self._symmetry, **properties
        )

    def quantize(self, input: torch.Tensor) -> torch.Tensor:
        scale = self.scale
        offset = self.offset
        qmin = self.qmin
        qmax = self.qmax
        block_size = self.block_size
        if self.zero_point_shift != 0.0:
            raise RuntimeError(
                "Nonzero quant shift not supported in AffineEncoding quantize"
            )

        # Subclasses of torch.Tensor with custom __torch_function__ (in our case, QuantizedTensorBase)
        # is known to introduce substantial CPU overhead.
        # Cast types of the inputs to plain torch.Tensor for faster execution.
        return quantize(
            input.as_subclass(torch.Tensor),
            scale.to(input.dtype).as_subclass(torch.Tensor),
            offset.to(input.dtype).as_subclass(torch.Tensor),
            qmin,
            qmax,
            block_size=block_size,
        )

    def dequantize(self, input: torch.Tensor) -> torch.Tensor:
        scale = self.scale
        offset = self.offset
        block_size = self.block_size
        if self.zero_point_shift != 0.0:
            raise RuntimeError(
                "Nonzero quant shift not supported in AffineEncoding dequantize"
            )

        # Subclasses of torch.Tensor with custom __torch_function__ (in our case, QuantizedTensorBase)
        # is known to introduce substantial CPU overhead.
        # Cast types of the inputs to plain torch.Tensor for faster execution.
        return dequantize(
            input.as_subclass(torch.Tensor),
            scale.to(input.dtype).as_subclass(torch.Tensor),
            offset.to(input.dtype).as_subclass(torch.Tensor),
            block_size=block_size,
        )

    def _to_legacy_format(self):
        min = self.min.flatten()
        max = self.max.flatten()
        scale = self.scale.flatten()

        # Legacy behavior is to shift offset by qmin
        offset = self.offset.flatten() + self.qmin

        return [
            {
                "min": float(min_),
                "max": float(max_),
                "scale": float(scale_),
                "offset": int(offset_),
                "bitwidth": self.bitwidth,
                "dtype": "int",
                "is_symmetric": str(self.symmetry),
            }
            for min_, max_, scale_, offset_ in zip(min, max, scale, offset)
        ]

    def _get_additional_properties(self) -> Dict[str, Any]:
        return {}

    def _get_channel_axis(self) -> Optional[int]:
        try:
            channel_axis = next(
                iter(axis for axis, dim in enumerate(self.scale.shape) if dim > 1)
            )
        except StopIteration:
            # Per-channel encoding that happens to have only one output channel
            # In this case, fall back to per-tensor encoding since we aren't fully
            # sure about the channel axis
            channel_axis = None
        return channel_axis

    def _get_block_axis(self) -> Optional[int]:
        # NOTE: DO NOT USE THIS FUNCTION except for QNN encoding export.
        #       This function assumes block axis can only be either axis 0 or axis 1.
        #       This assumption holds in practical cases, but does not cover all theoretically
        #       possible cases.
        if self.block_size is None:
            raise RuntimeError

        for axis, blk in enumerate(self.block_size[:2]):
            if blk != 1:
                return axis

        return None

    def to_qnn_encoding_dict(self, encoding_version=None) -> Union[List, Dict]:  # pylint: disable=too-many-branches, too-many-statements
        """
        Converts encoding object into QNN encoding
        """
        if encoding_version == "0.6.1":
            return self._to_legacy_format()

        if encoding_version == "1.0.0":
            encoding_dict = {
                "dtype": "INT",
                "bw": self.bitwidth,
                "is_sym": self.symmetry,
                "scale": self.scale.flatten().tolist(),
            }

            # Compute signed offset if necessary
            offset = self.offset
            if self.signed:
                offset = offset - 2 ** (self.bitwidth - 1)
            encoding_dict["offset"] = offset.to(torch.int).flatten().tolist()
            if self.zero_point_shift != 0.0:
                assert self.zero_point_shift == 0.5
                assert self.symmetry
                encoding_dict["zero_point_shift"] = [self.zero_point_shift] * len(
                    encoding_dict["offset"]
                )

            assert self.granularity != "unknown"
            if self.granularity == "pertensor":
                encoding_dict["enc_type"] = EncodingType.PER_TENSOR.name
            elif self.granularity == "perchannel":
                encoding_dict["enc_type"] = EncodingType.PER_CHANNEL.name
            else:
                encoding_dict["enc_type"] = EncodingType.PER_BLOCK.name
                encoding_dict["block_size"] = self.block_size[self._get_block_axis()]
                if encoding_dict["block_size"] == -1:
                    raise NotImplementedError(
                        "Exporting encodings to 1.0.0 format with block size -1 is not "
                        "supported yet. Export using sim.export() instead."
                    )
            return encoding_dict

        if encoding_version == "2.0.0":
            if self._zero_point_shift != 0.0:
                raise RuntimeError(
                    "Nonzero quant shift not supported in AffineEncoding to_qnn_encoding_dict"
                )
            output_dtype = self._get_export_dtype()

            y_scale = self.scale
            if self.symmetry:
                centroid = self._get_centroid()
                y_zero_point = torch.full_like(y_scale, centroid, dtype=torch.int32)
            else:
                y_zero_point = -self.offset.to(torch.int32)

            channel_axis = None
            block_axis = None
            block_size = None

            if self.granularity == "pertensor":
                pass
            elif self.granularity == "perchannel":
                channel_axis = self._get_channel_axis()
            elif self.granularity == "blockwise":
                # NOTE: This sometimes fail
                block_axis = self._get_block_axis()
            else:
                raise NotImplementedError

            if block_axis is not None:
                axis = block_axis
                block_size = self.block_size[block_axis]
            elif channel_axis is not None:
                axis = channel_axis
                y_scale = y_scale.flatten()
                y_zero_point = y_zero_point.flatten()
            else:
                axis = None
                y_scale = y_scale.squeeze()
                y_zero_point = y_zero_point.squeeze()

            y_scale = y_scale.tolist()
            y_zero_point = (
                None if torch.all(y_zero_point == 0) else y_zero_point.tolist()
            )

            ret = {
                "output_dtype": output_dtype,
                "y_scale": y_scale,
            }
            if y_zero_point is not None:
                ret.update({"y_zero_point": y_zero_point})
            if axis is not None:
                ret.update({"axis": axis})
            if block_size is not None:
                ret.update({"block_size": block_size})

            return ret

        raise AssertionError(
            f"Export encoding version {encoding_version} not supported."
            f"Expected one of: {VALID_ENCODING_VERSIONS}"
        )


class VectorEncoding(AffineEncoding):
    """
    Encoding object for vector quantization
    """

    def __init__(
        self,
        scale: torch.Tensor,
        offset: torch.Tensor,
        bitwidth: int,
        signed=False,
        symmetry=False,
        block_size: Optional[Tuple[int, ...]] = None,
        **kwargs,
    ):
        super().__init__(scale, offset, bitwidth, signed, symmetry, block_size)
        self.rows_per_block = kwargs["rows_per_block"]
        self.cols_per_block = kwargs["cols_per_block"]
        self.vector_dim = kwargs["vector_dim"]
        self.vector_stride = kwargs["vector_stride"]
        self.index_bw = kwargs["index_bw"]

    def _to_legacy_format(self):
        encoding = super()._to_legacy_format()
        for e in encoding:
            e.update(
                rows_per_block=self.rows_per_block,
                cols_per_block=self.cols_per_block,
                vector_dim=self.vector_dim,
                vector_stride=self.vector_stride,
                index_bw=self.index_bw,
            )
        return encoding

    def _get_additional_properties(self) -> Dict[str, Any]:
        return {
            "rows_per_block": self.rows_per_block,
            "cols_per_block": self.cols_per_block,
            "vector_dim": self.vector_dim,
            "vector_stride": self.vector_stride,
            "index_bw": self.index_bw,
        }

    def to_qnn_encoding_dict(self, encoding_version=None):
        encodings = super().to_qnn_encoding_dict(encoding_version)
        if encoding_version == "1.0.0":
            encodings.update(
                rows_per_block=self.rows_per_block,
                cols_per_block=self.cols_per_block,
                vector_dim=self.vector_dim,
                vector_stride=self.vector_stride,
                index_bw=self.index_bw,
            )
            encodings["enc_type"] = EncodingType.VECTOR.name
        return encodings


# pylint: disable=too-many-arguments
class GroupedBlockEncoding(AffineEncoding):
    """
    Encoding object for grouped block quantization
    """

    def __init__(
        self,
        scale: torch.Tensor,
        offset: torch.Tensor,
        bitwidth: int,
        signed=False,
        symmetry=False,
        block_size: Optional[Tuple[int, ...]] = None,
        block_grouping: Optional[Tuple[int, ...]] = None,
        decompressed_bw: Optional[int] = None,
        per_channel_scale: Optional[torch.Tensor] = None,
        **kwargs,
    ):
        super().__init__(
            scale, offset, bitwidth, signed, symmetry, block_size, **kwargs
        )
        self.block_grouping = block_grouping
        self.decompressed_bw = decompressed_bw
        self.per_channel_scale = per_channel_scale

    @property
    def per_block_int_scale(self):
        """
        Returns per-block integer scale which constructs blockwise scale
        when multiplied with per-channel float scale.

        scale = per_block_int_scale * per_channel_scale
        """
        return quantize(
            self.scale,
            scale=self.per_channel_scale,
            offset=torch.zeros_like(self.per_channel_scale),
            qmin=1,
            qmax=2 ** (self.decompressed_bw - self.bitwidth),
            block_size=self.block_grouping,
        )

    def to_qnn_encoding_dict(self, encoding_version=None) -> Union[List, Dict]:
        """
        Converts encoding object into QNN encoding
        """
        encoding_dict = super().to_qnn_encoding_dict(encoding_version)

        # Version 0.6.1 currently used for save_encodings_to_json
        if (
            all(group_size == 1 for group_size in self.block_grouping)
            or encoding_version == "0.6.1"
        ):
            # Equivalent to AffineEncoding
            pass
        elif encoding_version == "1.0.0":
            encoding_dict["bw"] = self.decompressed_bw
            encoding_dict["compressed_bw"] = self.bitwidth
            encoding_dict["scale"] = self.per_channel_scale.flatten().tolist()
            encoding_dict["offset"] = [
                -(2 ** (self.decompressed_bw - 1)) for _ in encoding_dict["scale"]
            ]
            encoding_dict["enc_type"] = EncodingType.LPBQ.name
            encoding_dict["per_block_int_scale"] = (
                self.per_block_int_scale.to(torch.int32).flatten().tolist()
            )
        elif encoding_version == "2.0.0":
            del encoding_dict["y_scale"]
            del encoding_dict["output_dtype"]

            compressed_bw = self.bitwidth
            y_zero_point = encoding_dict.pop("y_zero_point", None)

            if y_zero_point is not None and torch.any(torch.tensor(y_zero_point) != 0):
                raise RuntimeError(
                    f"LPBQ only supports symmetric quantization; got non-zero y_zero_point {y_zero_point}"
                )

            encoding_dict = {
                "per_block_int_scale": self.per_block_int_scale.to(
                    torch.int32
                ).tolist(),
                "per_channel_float_scale": self.per_channel_scale.tolist(),
                **encoding_dict,
                "output_dtype": f"int{compressed_bw}"
                if self.signed
                else f"uint{compressed_bw}",
            }

        return encoding_dict

    @classmethod
    def _from_affine_encoding(cls, encoding: AffineEncoding) -> "GroupedBlockEncoding":
        # pylint: disable=import-outside-toplevel, protected-access, cyclic-import
        from .quantizer import GroupedBlockQuantizeDequantize

        if isinstance(encoding, GroupedBlockEncoding):
            return encoding

        if not isinstance(encoding, AffineEncoding):
            raise ValueError(
                "Only AffineEncoding can be converted to GroupedBlockEncoding; "
                f"got {type(encoding)}"
            )

        if encoding.block_size is None:
            raise ValueError(
                "Only blockwise AffineEncodings can be converted to GroupedBlockEncoding; "
                f"got block_size={encoding.block_size}"
            )

        block_axis = encoding._get_block_axis()
        block_grouping = tuple(
            s_dim if axis == block_axis else 1
            for axis, s_dim in enumerate(encoding.scale.shape)
        )
        qtzr = GroupedBlockQuantizeDequantize(
            shape=encoding.scale.shape,
            bitwidth=encoding.bitwidth,
            symmetric=encoding.symmetry,
            decompressed_bw=encoding.bitwidth * 2,
            block_size=encoding.block_size,
            block_grouping=block_grouping,
        )
        with torch.no_grad():
            qtzr.min.copy_(encoding.min)
            qtzr.max.copy_(encoding.max)

        lpbq_scale = qtzr.get_scale()

        # If encoding.scale is equal to LPBQ scale, we can interpret it as LPBQ
        if torch.allclose(encoding.scale, lpbq_scale):
            return qtzr.get_encodings()

        raise ValueError("Failed to interpret encoding as GroupedBlockEncoding.")
