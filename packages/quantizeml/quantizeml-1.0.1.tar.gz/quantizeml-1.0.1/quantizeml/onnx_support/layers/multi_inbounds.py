#!/usr/bin/env python
# ******************************************************************************
# Copyright 2023 Brainchip Holdings Ltd.
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
__all__ = ["QuantizedAdd", "get_qadd", "QuantizedConcat", "get_qconcat"]

import numpy as np

from onnx import TensorProto as TP, NodeProto
from onnx.helper import make_node

from .base_layer import OnnxLayer, register_node_format
from .subgraph_ops import cast_tensors_to, get_scale_out_ops, get_input_shift_ops
from .subgraph_ops.activation import get_activation_ops
from .set_weights import set_range_max_on_qnode
from ..graph_tools import TENSOR_SHAPE, get_tensor_shape, get_activation
from ..quantization.core import align_to, downshift
from ..graph_tools import get_field


def get_qadd(nodes, graph, tensor_ranges):
    # Both inputs should not be constants
    weight_names = [x.name for x in graph.initializer]
    if nodes[0].input[0] in weight_names or nodes[0].input[1] in weight_names:
        raise ValueError("Unsupported Add: inputs should be tensors.")

    add_node = nodes[0]
    add_name = add_node.name

    act_node = get_activation(nodes) or NodeProto()
    qadd = QuantizedAdd(name=add_name, activation=act_node.op_type)

    # Set calibration ranges
    set_range_max_on_qnode(qadd, tensor_ranges[nodes[-1].output[0]])
    return qadd


def get_qconcat(nodes, **kwargs):
    concat_node = nodes[0]
    concat_name = concat_node.name
    concat_axis = get_field(concat_node, "axis")
    return QuantizedConcat(name=concat_name, axis=concat_axis)


@register_node_format(requires_fp_inputs=True)
class QuantizedAdd(OnnxLayer):
    """Intermediate representation of Add() as an exportable node.

    Args:
        activation (str, optional): activation type to be applied. Defaults to "".
        name (str, optional): the node name. Defaults to ''.
    """

    def __init__(self, activation="", name=''):
        super().__init__("QuantizedAdd", name=name)

        # Save properties need to serialize operation name
        self.serialize_attr["activation"] = activation

        # Declare weights
        self._add_weight("range_max", 1.0)

    @property
    def op_type(self):
        # Overriding op_type as ReLU comes after Scaling
        op_name = self.base_name
        if self.serialize_attr["scale"]:
            op_name += "Scaled"
        if self.serialize_attr["activation"]:
            op_name += "ReLU"
        return op_name

    def __build__(self, a_input_ts, b_input_ts, downscale=True):
        assert a_input_ts.dtype == b_input_ts.dtype == np.int8
        assert a_input_ts.shape == b_input_ts.shape

        # The chain of operations is modified if downscale is needed
        self.serialize_attr["scale"] = downscale

        # Compute output shape
        output_type = "int8" if downscale else "int32"
        output_ts = TENSOR_SHAPE(a_input_ts.shape, np.dtype(output_type))
        return output_ts

    def __quantize__(self, a_qinput, b_qinput, /, **kwargs):
        def _round_pot(x):
            return 2.0**np.round(np.log2(x))

        x1_scale = a_qinput.weights["scale"]
        x2_scale = b_qinput.weights["scale"]
        # This quantization is feasible if and only if input scales are power-of-two
        np.testing.assert_array_equal(
            x1_scale, _round_pot(x1_scale),
            f"Required a power-of-two scale for node {a_qinput.name} (op_type={a_qinput.op_type})")

        np.testing.assert_array_equal(
            x2_scale, _round_pot(x2_scale),
            f"Required a power-of-two scale for node {b_qinput.name} (op_type={b_qinput.op_type})")

        # Prepare tensors list with unique names
        prefix = self.name + "_"

        # Transpose scales to align with channels
        output_shape = get_tensor_shape(self.output)

        # We expected input scales are a power-of-two. Take i_scale as a max of both scales
        out_scale = np.maximum(x1_scale, x2_scale)

        # Shift to apply for each input will be
        N = len(output_shape)
        weights_dict = {prefix + "x1_shift": align_to((out_scale / x1_scale).astype("int32"), N),
                        prefix + "x2_shift": align_to((out_scale / x2_scale).astype("int32"), N)}

        if "Scaled" in self.op_type:
            # Now consider calibrated output range
            range_max = self.weights["range_max"]
            s_out, out_scale = downshift(range_max, out_scale, bitwidth=8)
            weights_dict.update({prefix + "S_out": align_to(s_out, N)})

        # Return quantized weights and output scale
        return weights_dict, out_scale

    @staticmethod
    def build_subgraph(op_type):
        # Cast inputs and shift to float.
        nodes, t_names = cast_tensors_to(["X", "Y", "Xs", "Ys"])

        # Align inputs with input shift
        nodes += get_input_shift_ops(t_names[0], t_names[2], "Xshifted")
        nodes += get_input_shift_ops(t_names[1], t_names[3], "Yshifted")

        # Perform addition
        nodes.append(make_node("Add", inputs=["Xshifted", "Yshifted"], outputs=["Zi"]))

        # Apply final output shift (optional)
        if "Scaled" in op_type:
            nodes += get_scale_out_ops("Zi", "Zscaled", scale_name="")
            nodes.append(make_node("Cast", ["Zscaled"], ["Z"], to=TP.INT8))
        else:
            nodes.append(make_node("Cast", ["Zi"], ["Z"], to=TP.INT32))

        # Activation (optional)
        if "ReLU" in op_type:
            # rename previous output
            nodes[-1].output[0] = "Z_no_act"
            nodes += get_activation_ops(nodes[-1].output[0], "Z")

        return nodes


class QuantizedConcat(OnnxLayer):
    """Intermediate representation of Concatenate() as an exportable node.

    Args:
        name (str, optional): the node name. Defaults to ''.
    """

    def __init__(self, axis,  name=''):
        if axis != 1:
            raise NotImplementedError("Axis != 1 in Concat is not supported yet.")
        super().__init__("QuantizedConcat", axis=axis, name=name)

    def __build__(self, a_input_ts, b_input_ts, downscale=False):
        # return the concatenated shape
        b, c, w, h = a_input_ts.shape
        concat_output_shape = (b, a_input_ts.shape[1] + b_input_ts.shape[1], w, h)
        output_ts = TENSOR_SHAPE(concat_output_shape, a_input_ts.dtype)
        return output_ts

    def __quantize__(self, a_qinput, b_qinput, /, **kwargs):
        # get scale and broadcast to input shape in case of per tensor
        x1_scale = a_qinput.weights["scale"]
        x1_shape = get_tensor_shape(a_qinput.output)
        x1_scale = x1_scale * np.ones(x1_shape[1])
        x2_scale = b_qinput.weights["scale"]
        x2_shape = get_tensor_shape(b_qinput.output)
        x2_scale = x2_scale * np.ones(x2_shape[1])
        # concatenate scales
        out_scale = np.concatenate((x1_scale, x2_scale))
        return {}, out_scale

    @staticmethod
    def build_subgraph(op_type):
        # Perform concatenation
        return [make_node("Concat", inputs=["X", "Y"], outputs=["Zi"], axis=1)]
