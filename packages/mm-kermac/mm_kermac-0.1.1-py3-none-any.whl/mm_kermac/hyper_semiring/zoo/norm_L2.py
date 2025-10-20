# SPDX-FileCopyrightText: 2025 MetaMachines LLC
#
# SPDX-License-Identifier: MIT

from mm_kermac import Stack, PtxInstruction
from mm_kermac.hyper_semiring import HyperSemiringKernel

import torch

class NormL2:
    def __init__(self):
        self.hyper_semiring = \
            HyperSemiringKernel(
                multiply_lambda=\
                    lambda reg_a, reg_b, _: [
                        reg_a,
                        reg_b,
                        PtxInstruction.sub_ftz_f32,           # diff = reg_b - reg_a [diff]
                        Stack.f32.dup,                        # [diff, diff]
                        PtxInstruction.mul_ftz_f32            # [diff * diff]
                    ],
                accumulate_lambda=\
                    lambda reg_diff, reg_c, _: [
                        reg_diff,
                        reg_c,
                        PtxInstruction.add_ftz_f32
                    ],
                epilogue_lambda=\
                    lambda reg_e, _: [
                        reg_e,
                        PtxInstruction.sqrt_approx_ftz_f32
                    ]
            )
        
    def __call__(
        self,
        x : torch.Tensor,
        z : torch.Tensor,
        out : torch.Tensor = None,
        try_to_align : bool = False,
        debug = False
    ):
        return self.hyper_semiring(
            a = x,
            b = z,
            out = out,
            hyper_dict=None,
            try_to_align = try_to_align,
            debug = debug
        )
