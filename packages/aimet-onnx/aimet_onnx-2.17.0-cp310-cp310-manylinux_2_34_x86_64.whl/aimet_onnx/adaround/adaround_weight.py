# -*- mode: python -*-
# =============================================================================
#  @@-COPYRIGHT-START-@@
#
#  Copyright (c) 2023, Qualcomm Innovation Center, Inc. All rights reserved.
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
# pylint: skip-file

"""Top level API for Adaptive Rounding - Post-Training Quantization (PTQ)"""

import copy
import tempfile
from typing import Dict, List, Collection
from tqdm import tqdm
import numpy as np

# Import AIMET specific modules
from aimet_common.utils import AimetLogger
from aimet_onnx.adaround.adaround_tensor_quantizer import AdaroundTensorQuantizer
from aimet_onnx.quantsim import QuantizationSimModel
from aimet_onnx.meta.utils import get_module_act_func_pair
from aimet_onnx import utils
from aimet_onnx.adaround.adaround_optimizer import AdaroundOptimizer
from aimet_onnx.adaround.utils import (
    ModelData,
    ModuleInfo,
    read_attributes_for_op,
    AdaroundSupportedModules,
)

logger = AimetLogger.get_area_logger(AimetLogger.LogAreas.Quant)


class Adaround:
    """
    Weight-rounding mechanism for Post Training Quantization (PTQ)
    """

    @classmethod
    def apply_adaround(
        cls,
        sim: QuantizationSimModel,
        inputs: Collection[Dict[str, np.ndarray]],
        num_iterations: int = 10000,
        node_names_to_optimize: List[str] = None,
    ):
        """
        Optimizes the rounding direction of weights in the QuantizationSimModel to reduce quantization error.

        After applying AdaRound to a QuantizationSimModel object, the quantization encodings will be frozen
        for optimized weights and the sim model will contain updated weight tensors.

        Args:
            sim (QuantizationSimModel): QuantizationSimModel instance to optimize
            inputs (Collection[Dict[str, np.ndarray]]): The set of input samples to use during optimization.
            num_iterations (int): Number of optimization steps to take for each layer. Recommended value is
                10K for weight bitwidths >= 8-bits, 15K for weight bitwidths < 8 bits.
            node_names_to_optimize: List of node names to optimize. If None, all the nodes(under supported types) will be optimized

        """
        # pylint: disable=too-many-locals, protected-access
        sim._compute_param_encodings(overwrite=False)

        module_act_func_pair = get_module_act_func_pair(sim.connected_graph)

        fp32_model = copy.deepcopy(sim.model.model)
        fp32_model = QuantizationSimModel.remove_quantizers(fp32_model)

        with (
            utils.disable_quantizers(sim, set(sim.activation_names))
            and tempfile.TemporaryDirectory() as tmp_dir
        ):
            # Cache model input data to temporary directory
            cached_dataset = utils.CachedDataset(inputs, len(inputs), tmp_dir)

            param_to_tensor_quantizer_dict = (
                Adaround._create_param_to_tensor_quantizer_dict(sim)
            )
            model_data = ModelData(sim)
            quantized_layer_to_input_tensor_name = (
                Adaround._get_quantized_layer_input_tensor_name(sim)
            )
            # AdaRound must be applied to modules in the order of occurrence
            for module in tqdm(sim.connected_graph.ordered_ops):
                name = module.name
                module_info = model_data.module_to_info[name]

                if node_names_to_optimize and module.name not in node_names_to_optimize:
                    continue

                if (
                    cls._is_supported_layer_type(module_info)
                    and param_to_tensor_quantizer_dict[
                        module_info.params["weight"].name
                    ]._enabled
                ):
                    # Get module's next following activation function
                    act_func = module_act_func_pair.get(name)
                    quantized_input_name = quantized_layer_to_input_tensor_name[name]
                    logger.info(
                        "Started Optimizing weight rounding of module: %s", name
                    )
                    AdaroundOptimizer.adaround_module(
                        module_info,
                        quantized_input_name,
                        sim,
                        fp32_model,
                        act_func,
                        cached_dataset,
                        num_iterations,
                        param_to_tensor_quantizer_dict,
                    )
                    # Freeze quantizer's encodings
                    weight_name = module_info.params["weight"].name
                    sim.qc_quantize_op_dict[weight_name].freeze_encodings()

        # Re-build session since weights have been updated
        sim._rebuild_session()

    @classmethod
    def _is_supported_layer_type(cls, module_info: ModuleInfo):
        if not module_info.type in AdaroundSupportedModules:
            return False

        if not "weight" in module_info.params:
            return False

        if (
            module_info.type in ("Conv", "ConvTranspose")
            and len(module_info.params["weight"].shape) != 4
        ):
            # Only 2d conv/convtranspose is supported
            return False

        attributes = read_attributes_for_op(module_info)
        if "pads" in attributes:
            if len(attributes["pads"]) > 4:
                logger.info(
                    "Skipping the Convolution layer because padding size greater than 4 is not supported for optimization"
                )
                return False

        return True

    @staticmethod
    def _create_param_to_tensor_quantizer_dict(
        quant_sim: QuantizationSimModel,
    ) -> Dict[str, AdaroundTensorQuantizer]:
        """
        Create Adaround tensor quantizers for weight tensor

        :param quant_sim: Quant sim
        :return: Dict of param name to AdaroundTensorQuantizer
        """
        param_to_tq_dict = {}
        for param_name in quant_sim.param_names:
            quantizer = quant_sim.qc_quantize_op_dict[param_name]
            ch_axis = -1
            if quantizer.quant_info.usePerChannelMode:
                ch_axis = quantizer.quant_info.channelAxis
            adaround_quantizer = AdaroundTensorQuantizer(
                quantizer.bitwidth,
                quantizer.enabled,
                quantizer.encodings,
                ch_axis,
            )
            param_to_tq_dict[param_name] = adaround_quantizer

        return param_to_tq_dict

    @staticmethod
    def _get_quantized_layer_input_tensor_name(sim):
        quantized_layer_to_input_tensor_name = {}
        for node in sim.model.model.graph.node:
            if node.op_type in AdaroundSupportedModules:
                quantized_layer_to_input_tensor_name[node.name] = node.input[0]
        return quantized_layer_to_input_tensor_name


apply_adaround = Adaround.apply_adaround
