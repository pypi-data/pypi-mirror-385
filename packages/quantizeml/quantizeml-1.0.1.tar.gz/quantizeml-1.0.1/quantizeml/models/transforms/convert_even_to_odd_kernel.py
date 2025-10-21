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
"""
Sanitize to convert kernel sizes from even to odd in convolutional layers.
"""

__all__ = ['convert_even_to_odd_kernel']

import tf_keras as keras
import numpy as np

from ..utils import apply_weights_to_model, requires_tf_keras_model
from .transforms_utils import get_layer_index, get_layers_by_type


@requires_tf_keras_model
def convert_even_to_odd_kernel(model):
    """Adjusts kernel sizes from even to odd for convolutional layers.

    Args:
        model (keras.Model): a model

    Returns:
        keras.Model: the sanitized model.
    """
    target_layers = _find_target_layers(model)

    # When there are no valid candidates, return the original model
    if len(target_layers) == 0:
        return model

    updated_model = _convert_even_to_odd_kernel(model, target_layers)
    return updated_model


def _convert_even_to_odd_kernel(model, target_layers):
    config = model.get_config()
    layers = config["layers"]

    variables_dict = {var.name: var for var in model.variables}

    for layer in target_layers:
        kernel_size = layer.kernel_size[0]
        layer_index = get_layer_index(layers, layer.name)

        updated_kernel = _update_weights(layer)
        layers[layer_index]['config']['kernel_size'] = (kernel_size + 1, kernel_size + 1)

        # Update weights in the variables dict
        variables_dict[layer.weights[0].name] = updated_kernel

    updated_model = model.from_config(config)
    apply_weights_to_model(updated_model, variables_dict)

    return updated_model


def _find_target_layers(model):
    def _is_valid_attributes(layer):
        stride = layer.strides[0]
        kernel_size = layer.kernel_size[0]
        padding = layer.padding

        if isinstance(layer, keras.layers.DepthwiseConv2D):
            inbound = None
        else:
            inbound = layer._inbound_nodes[0].inbound_layers
            while inbound:
                if not isinstance(inbound, keras.layers.Rescaling):
                    break
                inbound = inbound._inbound_nodes[0].inbound_layers

        # Additional input_conv checks: this is missing input type (input_conv is signed only,
        # but sanitizers do not have this information)
        if (isinstance(layer, keras.layers.Conv2D) and isinstance(inbound, keras.layers.InputLayer)
                and layer.input_shape[-1] in [1, 3]):
            return (stride in [1, 2] and (kernel_size == 2 or kernel_size == 6)
                    and padding == "same")
        else:
            stride_1_cond = stride == 1 and kernel_size in (2, 4, 6)
            stride_2_cond = stride == 2 and kernel_size == 2
            return ((stride_1_cond or stride_2_cond) and padding == "same")

    layers = get_layers_by_type(model, (keras.layers.Conv2D, keras.layers.DepthwiseConv2D))
    return [layer for layer in layers if _is_valid_attributes(layer)]


def _compute_slice_offsets(layer):
    stride = layer.strides[0]
    height, width = layer.input_shape[1:3]
    kernel_size = layer.kernel_size[0]

    assert stride in [1, 2], f"Unsupported stride={stride}."
    if stride == 1:
        col_start = 1
        row_start = 1
    elif stride == 2:
        col_start = height % 2
        row_start = width % 2

    col_end = col_start + kernel_size
    row_end = row_start + kernel_size

    return col_start, row_start, col_end, row_end


def _update_weights(layer):
    kernel = layer.get_weights()[0]

    # Increase kernel size by 1 and construct new_weigths
    kernel_size = layer.kernel_size[0]
    new_shape = (kernel_size + 1, kernel_size + 1, *kernel.shape[2:])
    updated_kernel = np.zeros(new_shape, dtype=kernel.dtype)

    # Compute placement of the original kernel in the new kernel
    col_start, row_start, col_end, row_end = _compute_slice_offsets(layer)
    updated_kernel[col_start:col_end, row_start:row_end] = kernel

    return updated_kernel
