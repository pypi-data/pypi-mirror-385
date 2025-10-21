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
# pylint: disable=missing-docstring
from collections import namedtuple
from typing import Optional, Mapping
import torch


class _finfo(
    namedtuple("_finfo", ("exponent_bits", "mantissa_bits", "finite", "unsigned_zero"))
):
    def to_torch_dtype(self) -> Optional[torch.dtype]:
        return _finfo_to_torch_dtype.get(self)

    @classmethod
    def from_torch_dtype(cls, dtype: torch.dtype) -> "_finfo":
        try:
            return _torch_dtype_to_finfo[dtype]
        except KeyError as e:
            msg = " ".join(
                [
                    f"Expected dtype to be one of {list(_torch_dtype_to_finfo.keys())};",
                    f"got {dtype}",
                ]
            )
            raise ValueError(msg) from e

    def to_str(self) -> str:
        torch_dtype = self.to_torch_dtype()

        if torch_dtype:
            _, typename = str(torch_dtype).split(".")
            return typename

        e, m, fn, uz = self
        fn = "fn" if fn else ""
        uz = "uz" if uz else ""

        return f"float{e + m + 1}_e{e}m{m}{fn}{uz}"

    def is_float16(self) -> bool:
        return self == _float16

    def is_bfloat16(self) -> bool:
        return self == _bfloat16

    @property
    def max(self) -> float:
        torch_dtype = self.to_torch_dtype()

        if torch_dtype:
            return torch.finfo(torch_dtype).max

        if not self.finite and not self.unsigned_zero:
            return self._ieee_float_max_representable_value()

        raise RuntimeError(f"Maximum representable value of {self.to_str()} is unkown")

    def _ieee_float_max_representable_value(self):
        exponent_bits, mantissa_bits, _, _ = self
        exponent_max = 2**exponent_bits - 1
        exponent_bias = exponent_max // 2
        return (2 - 2**-mantissa_bits) * 2 ** (exponent_max - exponent_bias - 1)


_float16 = _finfo(exponent_bits=5, mantissa_bits=10, finite=False, unsigned_zero=False)
_bfloat16 = _finfo(exponent_bits=8, mantissa_bits=7, finite=False, unsigned_zero=False)

_finfo_to_torch_dtype: Mapping[_finfo, torch.dtype] = {
    _float16: torch.float16,
    _bfloat16: torch.bfloat16,
}

if hasattr(torch, "float8_e4m3fn"):
    _float8_e4m3fn = _finfo(
        exponent_bits=4, mantissa_bits=3, finite=True, unsigned_zero=False
    )
    _finfo_to_torch_dtype.update({_float8_e4m3fn: torch.float8_e4m3fn})

if hasattr(torch, "float8_e4m3fnuz"):
    _float8_e4m3fnuz = _finfo(
        exponent_bits=4, mantissa_bits=3, finite=True, unsigned_zero=True
    )
    _finfo_to_torch_dtype.update({_float8_e4m3fnuz: torch.float8_e4m3fnuz})

if hasattr(torch, "float8_e5m2"):
    _float8_e5m2 = _finfo(
        exponent_bits=5, mantissa_bits=2, finite=False, unsigned_zero=False
    )
    _finfo_to_torch_dtype.update({_float8_e5m2: torch.float8_e5m2})

if hasattr(torch, "float8_e5m2fnuz"):
    _float8_e5m2fnuz = _finfo(
        exponent_bits=5, mantissa_bits=2, finite=True, unsigned_zero=True
    )
    _finfo_to_torch_dtype.update({_float8_e5m2fnuz: torch.float8_e5m2fnuz})


_torch_dtype_to_finfo: Mapping[torch.dtype, _finfo] = {
    torch_dtype: finfo for finfo, torch_dtype in _finfo_to_torch_dtype.items()
}
