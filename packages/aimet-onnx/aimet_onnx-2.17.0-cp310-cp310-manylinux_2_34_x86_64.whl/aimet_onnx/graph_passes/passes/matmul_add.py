# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# SPDX-License-Identifier: BSD-3-Clause

# pylint: disable=missing-module-docstring
from typing import Dict
import copy
from aimet_onnx.meta.connectedgraph import _get_matmul_add_bias_idx
from aimet_onnx.graph_passes.graph_pass import GraphPass
from aimet_onnx.graph_passes.pass_registry import register_pass
from aimet_onnx.meta.operations import Op
from aimet_onnx.meta.product import Product
from aimet_onnx.qc_quantize_op import QcQuantizeOp
from onnx import ModelProto, TensorProto
from onnx.external_data_helper import _get_all_tensors


@register_pass("MatmulAdd")
class MatmulAdd(GraphPass):
    """
    For Matmul + Add pattern, disable quantization for intermediate Matmul output and bias.

    Expected graph:
        Matmul -> Add

    """

    # pylint: disable=too-many-branches, too-many-return-statements
    def match_pattern(self, op: Op, model: ModelProto):
        """
        Match RMSNormalization pattern and collect ops to disable output quantizers
        """
        if op.type != "MatMul":
            return False

        if _get_matmul_add_bias_idx(op, model) is None:
            return False

        return True

    def apply_on_op(
        self, op: Op, model: ModelProto, op_quantizers: Dict[str, QcQuantizeOp]
    ):
        """
        Check for pattern match for given Matmul+Add op.
        If pattern matches, then disable quantization for intermediate outputs.

        Args:
            op (Op): Op to check for pattern match
            op_quantizers (Dict[str, QcQuantizeOp]): Global map of QcQuantizeOp
        """
        if not self.match_pattern(op, model):
            return

        matmul_output: Product = op.outputs[0]
        bias_op: Op = op.output_ops[0]
        bias_idx = 1 - bias_op.inputs.index(matmul_output)
        bias_product: Product = bias_op.inputs[bias_idx]

        weight: TensorProto = next(
            param
            for param, param_type in op.parameters.values()
            if param_type == "weight"
        )
        bias_tensor: TensorProto = next(
            tensor
            for tensor in _get_all_tensors(model)
            if tensor.name == bias_product.name
        )
        bias_product.set_as_param(bias_op, bias_tensor)
        bias_op.add_param(bias_product.name, bias_product, "bias")

        matmul_output_qtzr = op_quantizers[matmul_output.name]
        bias_qtzr = op_quantizers[bias_product.name]
        weight_qtzr = op_quantizers[weight.name]

        # Disable intermediate output quantization and bias quantization
        matmul_output_qtzr.enabled = False
        bias_qtzr.enabled = False

        # Let bias quantizers follow the same granularity as weight quantizer
        bias_qtzr.tensor_quantizer_params = copy.deepcopy(
            weight_qtzr.tensor_quantizer_params
        )
        bias_qtzr.enable_per_channel_quantization(
            weight_qtzr.quant_info.usePerChannelMode
        )
