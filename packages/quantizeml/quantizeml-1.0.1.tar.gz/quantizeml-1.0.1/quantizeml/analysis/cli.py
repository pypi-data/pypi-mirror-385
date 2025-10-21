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
quantizeml analysis main command-line interface.
"""

from .. import load_model
from .kernel_distribution import plot_kernel_distribution
from .quantization_error_api import (measure_layer_quantization_error,
                                     measure_cumulative_quantization_error,
                                     measure_weight_quantization_error)
from .tools import print_metric_table


def check_quantization_error_arguments(parser, args):
    if args.mode != "weight" and args.float_model is None:
        parser.error(f"-fm/--float_model argument is required when mode={args.mode}.")


def main(parsers, args):
    """ CLI entry point.

    Contains an argument parser with specific arguments to analysis a model.
    Complete arguments lists available using the -h or --help argument.

    """
    model = load_model(args.model)
    if args.analysis_action == "kernel_distribution":
        plot_kernel_distribution(model, logdir=args.logdir)
    elif args.analysis_action == "quantization_error":
        check_quantization_error_arguments(parsers[1], args)
        if args.mode == "cumulative":
            fmodel = load_model(args.float_model)
            summary = measure_cumulative_quantization_error(fmodel,
                                                            model,
                                                            batch_size=args.batch_size,
                                                            target_layer=args.target_layer)
        elif args.mode == "single":
            fmodel = load_model(args.float_model)
            summary = measure_layer_quantization_error(fmodel,
                                                       model,
                                                       batch_size=args.batch_size,
                                                       target_layer=args.target_layer)
        else:
            summary = measure_weight_quantization_error(model, target_layer=args.target_layer)
        model_name = model.name if hasattr(model, "name") else model.graph.name
        print_metric_table(summary, model_name=model_name)
    else:
        raise RuntimeError(f'unknown action: {args.action}')
