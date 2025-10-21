#!/usr/bin/env python
# ******************************************************************************
# Copyright 2024 Brainchip Holdings Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************

__all__ = ["convert_matmul_to_gemm"]

import onnx_ir as ir
from onnxscript.rewriter._basics import MatchResult
from onnxscript.rewriter._rewrite_rule import RewriteRuleClassBase

from ..model import ONNXModel


def convert_matmul_to_gemm(model):
    """Converts Matmul node to a Gemm node.

    Args:
        model (ONNXModel): The ONNX model to be processed.
    """

    assert isinstance(model, ONNXModel)
    model.rewrite([_MatMulToGemm().rule()])


class _MatMulToGemm(RewriteRuleClassBase):
    def pattern(self, op, input_a, input_b):
        return op.MatMul(input_a, input_b)

    def rewrite(self, op, input_a, input_b):
        # Transpose weights as in quantizeml we force attribute transB=1
        transposed_weights = op.initializer(
            ir.tensor(input_b.const_value.numpy().T), name=input_b.name)
        return op.Gemm(input_a, transposed_weights, transB=1)

    def check(self, context, input_a, input_b, **_):
        del context  # Not used
        check_result = MatchResult()

        if input_a.shape is None or input_b.shape is None:
            return check_result.fail("Unknow input_a and/or input_b shapes")

        # Rank of input_a and input_b must be 2
        if len(input_a.shape) != 2 or len(input_b.shape) != 2:
            return check_result.fail("Rank of input_a and input_b must be 2")

        # Input_b must be a constant tensor
        if ir.convenience.get_const_tensor(input_b) is None:
            return check_result.fail("Input_b must be a constant tensor")

        return check_result
