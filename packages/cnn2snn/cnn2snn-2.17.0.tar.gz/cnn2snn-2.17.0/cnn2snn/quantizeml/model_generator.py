#!/usr/bin/env python
# ******************************************************************************
# Copyright 2022 Brainchip Holdings Ltd.
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
"""Parsing functions to generate an Akida model from a Keras model quantized with quantizeml api.
"""

from quantizeml.models import record_quantization_variables
from akida import Model
from onnx import ModelProto

from .input_data import convert_input
from .block_converters_generator import (generate_block_converters,
                                         _V1_INPUT_PATTERN_CONVERTERS,
                                         _V2_INPUT_PATTERN_CONVERTERS)
from .onnx_conversion import generate_onnx_model


def _raise_block_error(block_converter, exception):
    """ Raise error due to non convertible layers block"""
    block_layers_name = ""
    block_layers_type = ""
    for layer in block_converter._block:
        block_layers_name += f"'{layer.name}', "
        block_layers_type += f"{layer.__class__.__name__}, "
    raise type(exception)(f"Layers {block_layers_name[:-2]}: unsupported type "
                          f"[{block_layers_type[:-2]}]: {exception}") from exception


def generate_model(model):
    """Generates an Akida model.

    This function creates an Akida model by iterating through the layers of the
    quantized model. For each layer, the corresponding akida layer is created and
    added to the Akida model.

    Args:
        model (:obj:`keras.Model` or :obj:`onnx.ModelProto`): a model to convert.

    Returns:
        :obj:`akida.Model`: the generated Akida model.
    """
    if isinstance(model, ModelProto):
        return generate_onnx_model(model)
    return generate_qml_model(model)


def generate_qml_model(model):
    """Generates an Akida model based on a Keras quantizeml model.

    Args:
        model (:obj:`keras.Model`): a model to convert.

    Returns:
        :obj:`akida.Model`: the generated Akida model.
    """
    # Check if input model is convertible and extract its layers blocks
    blocks = generate_block_converters(model)
    # First store necessary variables for conversion
    record_quantization_variables(model)
    model_ak = Model()

    # Input blocks are handled with their associated BlockConverter
    INPUT_PATTERNS = (tuple(_V1_INPUT_PATTERN_CONVERTERS.values()) +
                      tuple(_V2_INPUT_PATTERN_CONVERTERS.values()))
    if isinstance(blocks[0], INPUT_PATTERNS):
        blocks[0].convert(model_ak)
        blocks.pop(0)
    else:
        # Convert the keras InputLayer into an InputData layer
        convert_input(model_ak, model)

    for block in blocks:
        # The next check converts the layers block to its corresponding Akida layer
        try:
            block.convert(model_ak)
        except Exception as e:
            _raise_block_error(block, e)
    return model_ak
