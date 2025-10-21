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
Transformation to split a layer with an activation into two layers:
A first layer with the weigths and a second layer with the activation.
"""


__all__ = ["split_layers_with_activations"]

from .insert_layer import insert_in_config
from .transforms_utils import get_layer_index
from ..utils import apply_weights_to_model, requires_tf_keras_model
from ... import layers

import tf_keras as keras


@requires_tf_keras_model
def split_layers_with_activations(model):
    """
    Splits layers with an activation different to 'linear' into two separate layers:
    one without activation and one with the activation layer.

    Args:
        model (keras.Model): The Keras model to be modified (sequential or functional).

    Returns:
        Model: The updated Keras model with activations split into separate layers.
    """

    config = model.get_config()
    for layer in model.layers:
        if isinstance(layer, (keras.layers.Activation, layers.Activation)):
            continue
        if (activation := getattr(layer, 'activation', None)) and activation.__name__ != 'linear':
            # Modify the first layer
            index = get_layer_index(config['layers'], layer.name)
            config['layers'][index]['config']['activation'] = 'linear'
            # Create the new layer
            config_no_activation = layer.get_config()
            activation_layer = keras.layers.Activation(activation.__name__,
                                                       name=config_no_activation['name'] + '_activ')
            # Insert the second layer (only ReLu) into the configuration
            insert_in_config(model, layer.name, activation_layer, config)
    # update the model
    new_model = model.from_config(config)
    # Load original weights
    variables_dict = {var.name: var for var in model.variables}
    apply_weights_to_model(new_model, variables_dict, False)
    return new_model
