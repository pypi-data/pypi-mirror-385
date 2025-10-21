# -*- mode: python -*-
# =============================================================================
#  @@-COPYRIGHT-START-@@
#
#  Copyright (c) 2023-2024, Qualcomm Innovation Center, Inc. All rights reserved.
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

"""Cross Layer Equalization

Some terminology for this code.
CLS set: Set of layers (2 or 3) that can be used for cross-layer scaling
Layer groups: Groups of layers that are immediately connected and can be decomposed further into CLS sets
"""

from abc import ABC, abstractmethod
from typing import List, Union, Tuple, Dict
from enum import Enum
import numpy as np

from aimet_common.utils import AimetLogger
from aimet_common.connected_graph.connectedgraph_utils import get_all_input_ops

logger = AimetLogger.get_area_logger(AimetLogger.LogAreas.Quant)


ScaleFactor = Union[np.ndarray, Tuple[np.ndarray]]


class ClsLayerType(Enum):
    """Enum class to represent CLS layer types"""

    Unsupported = 0
    Conv = 1  # Overloaded for conv and ConvTranspose
    DepthwiseConv = 2


class ClsSetInfo:
    """
    This class hold information about the layers in a CLS set, along with corresponding scaling factors
    and other information like if there is a ReLU activation function between the CLS set layers
    """

    class ClsSetLayerPairInfo:
        """
        Models a pair of layers that were scaled using CLS. And related information.
        """

        def __init__(
            self,
            layer1,
            layer2,
            scale_factor: np.ndarray,
            relu_activation_between_layers: bool,
        ):
            """
            :param layer1: Layer whose bias is folded
            :param layer2: Layer to which bias of previous layer's bias is folded
            :param scale_factor: Scale Factor found from Cross Layer Scaling to scale BN parameters
            :param relu_activation_between_layers: If the activation between layer1 and layer2 is Relu
            """
            self.layer1 = layer1
            self.layer2 = layer2
            self.scale_factor = scale_factor
            self.relu_activation_between_layers = relu_activation_between_layers

    def __init__(
        self, cls_pair_1: ClsSetLayerPairInfo, cls_pair_2: ClsSetLayerPairInfo = None
    ):
        """
        Constructor takes 2 pairs if Depth-wise separable layer is being folded

        :param cls_pair_1: Pair between two conv or conv and depth-wise conv
        :param cls_pair_2: Pair between depth-wise conv and point-wise conv
        """
        if cls_pair_2:
            self.cls_pair_info_list = [cls_pair_1, cls_pair_2]
        else:
            self.cls_pair_info_list = [cls_pair_1]


class GraphSearchUtils:
    """
    Code to search a model graph to find nodes to use for cross-layer-scaling and high-bias-fold
    """

    def __init__(
        self,
        connected_graph,
        ordered_modules_list,
        cls_supported_layer_types,
        cls_supported_activation_types,
    ):
        self._connected_graph = connected_graph
        self._ordered_module_list = ordered_modules_list
        self._cls_supported_layer_types = cls_supported_layer_types
        self._cls_supported_activation_types = cls_supported_activation_types

    def find_layer_groups_to_scale(self) -> List[List]:
        """
        :return: List of groups of layers. Each group can be independently equalized
        """

        # Find the input node(s) in the graph
        input_nodes = get_all_input_ops(self._connected_graph)

        layer_groups = []
        for op in input_nodes:
            self.find_downstream_layer_groups_to_scale(op, layer_groups)

        # Sort the layer groups in order of occurrence in the model
        ordered_layer_groups = []
        for module_name, _ in self._ordered_module_list:
            for layer_group in layer_groups:
                if layer_group[0].dotted_name == module_name:
                    ordered_layer_groups.append(layer_group)

        return ordered_layer_groups

    @staticmethod
    def convert_layer_group_to_cls_sets(layer_group):
        """
        Helper function to convert a layer group to a list of cls sets
        :param layer_group: Given layer group to generate cls sets
        :return: List of cls sets

        Supported layer combinations for CLS are:
        1. Conv + Conv
        2. DepthwiseConv + Conv
        3. Conv + DepthwiseConv + Conv

        Can be rewritten as,
        Conv
            -> Conv
            -> DepthwiseConv
                -> Conv
        DepthwiseConv
            -> Conv

        If a combination is partially supported, the cls_set is completely omitted and restarted from the next
        supported layer
        For example: Consider Conv + DepthwiseConv + Depthwise(unsupported)
        - Since Depthwise(unsupported) is the last layer encountered, we need to omit all the three layers and restart
        the cls sets from the next supported layer.

        """

        # pylint: disable=too-many-branches
        def convert_to_cls_layer_type(layer):
            """
            Given the layer, check if its supported in CLS
            :param layer: layer to check
            :return: Tuple of ClsLayerType and the layer
            """
            weight_param_shape = [
                param
                for param, param_type in layer.parameters.values()
                if param_type == "weight"
            ][0].shape

            if layer.groups == 1:
                layer_type = ClsLayerType.Conv
            elif (
                layer.groups == weight_param_shape[0]
                and weight_param_shape[0] == weight_param_shape[1] * layer.groups
            ):
                # depthwiseConv layer with depth multiplier = 1
                layer_type = ClsLayerType.DepthwiseConv
            else:
                layer_type = ClsLayerType.Unsupported

            return layer_type, layer

        def get_next_layer():
            """
            :return: Tuple of ClsLayerType and the next layer in layer_group
            """
            if not layer_group:
                return ClsLayerType.Unsupported, None
            layer = layer_group.pop(0)
            return convert_to_cls_layer_type(layer)

        cls_sets = []

        first_layer_to_scale = (ClsLayerType.Unsupported, None)
        while layer_group:
            while layer_group and first_layer_to_scale[0] is ClsLayerType.Unsupported:
                first_layer_to_scale = get_next_layer()
                if first_layer_to_scale[0] is ClsLayerType.Unsupported:
                    logger.info(
                        "Layer %s is not supported. Ignoring for cls",
                        first_layer_to_scale[1],
                    )

            second_layer_to_scale = get_next_layer()
            if first_layer_to_scale[0] == ClsLayerType.Conv:
                if second_layer_to_scale[0] == ClsLayerType.Conv:
                    cls_sets.append((first_layer_to_scale[1], second_layer_to_scale[1]))
                    first_layer_to_scale = second_layer_to_scale
                elif second_layer_to_scale[0] == ClsLayerType.DepthwiseConv:
                    if layer_group:
                        # do not pop third layer yet, determine its type and then pop it
                        third_layer_to_scale = convert_to_cls_layer_type(layer_group[0])
                        if third_layer_to_scale[0] == ClsLayerType.Conv:
                            cls_sets.append(
                                (
                                    first_layer_to_scale[1],
                                    second_layer_to_scale[1],
                                    third_layer_to_scale[1],
                                )
                            )
                            # adding third_layer_to_scale for the next round of CLS set determination
                            first_layer_to_scale = get_next_layer()
                        else:
                            # unsupported combination encountered
                            first_layer_to_scale = second_layer_to_scale
                else:
                    logger.info(
                        "Layer %s is not supported. Ignoring for cls",
                        second_layer_to_scale[1],
                    )
                    first_layer_to_scale = (ClsLayerType.Unsupported, None)
            elif first_layer_to_scale[0] == ClsLayerType.DepthwiseConv:
                if second_layer_to_scale[0] == ClsLayerType.Conv:
                    cls_sets.append((first_layer_to_scale[1], second_layer_to_scale[1]))
                first_layer_to_scale = second_layer_to_scale
            else:
                logger.info(
                    "Layer %s is not supported. Ignoring for cls",
                    first_layer_to_scale[1],
                )
                first_layer_to_scale = second_layer_to_scale

        return cls_sets

    def find_downstream_layer_groups_to_scale(self, op, layer_groups: List):
        """
        Iterative function to find cls layer groups downstream from a given op
        :param op: Starting op to search from
        :param layer_groups: Running list of layer groups
        """
        visited_nodes = set()

        ops_and_groups_to_traverse = [(op, [])]
        while ops_and_groups_to_traverse:
            curr_op, current_group = ops_and_groups_to_traverse.pop(0)

            if curr_op in visited_nodes:
                if (len(current_group) > 1) and (current_group not in layer_groups):
                    layer_groups.append(current_group)
                continue

            visited_nodes.add(curr_op)

            # If current node is CLE-able, add to the current group
            if curr_op.get_module() and curr_op.type in self._cls_supported_layer_types:
                current_group.append(curr_op)

            # Terminating condition for current group:
            # 1. Op does not have a module (not quantizable)
            # 2. Op type is not a supported type for CLE
            # 3. Op output is used by multiple consumers (start of a branch)
            # 4. Op has no output ops (leaf op)
            if (
                not curr_op.get_module()
                or not curr_op.type
                in self._cls_supported_layer_types
                + self._cls_supported_activation_types
                or len(curr_op.output_ops) > 1
                or len(curr_op.output_ops) == 0
            ):
                if (len(current_group) > 1) and (current_group not in layer_groups):
                    layer_groups.append(current_group)

                for consumer in curr_op.output_ops:
                    ops_and_groups_to_traverse.insert(0, (consumer, []))

            else:
                assert len(curr_op.output_ops) == 1
                ops_and_groups_to_traverse.insert(
                    0, (curr_op.output_ops[0], current_group)
                )

    def does_module_have_relu_activation(self, module) -> bool:
        """
        Finds if a given module has a ReLU activation
        :param module: Module to find activation for
        :return: True if module has a relu activation
        """

        for op in self._connected_graph.get_all_ops().values():
            if op.name == module.dotted_name and len(op.output_ops) == 1:
                return op.output_ops[0].type in self._cls_supported_activation_types

        return False

    def is_relu_activation_present_in_cls_sets(self, cls_sets: List) -> List[Tuple]:
        """
        :param cls_sets: CLS sets to find relu activations in
        :return: Tuple of booleans representing if activation is Relu (True) or not (False)
        """

        is_relu_activation_in_cls_sets = []
        for cls_set in cls_sets:
            # We need to check activation functions for all layers but the last one in the set
            # Because we are only interested in checking activation functions between the layers we will scale
            cls_set = cls_set[:-1]

            is_relu_activation_in_cls_set = ()
            for module in cls_set:
                is_relu_activation_in_cls_set += (
                    self.does_module_have_relu_activation(module),
                )

            if len(is_relu_activation_in_cls_set) == 1:
                is_relu_activation_in_cls_set = is_relu_activation_in_cls_set[0]

            is_relu_activation_in_cls_sets.append(is_relu_activation_in_cls_set)

        return is_relu_activation_in_cls_sets


class CrossLayerScaling(ABC):
    """
    Code to apply the cross-layer-scaling technique to a model
    """

    def scale_cls_sets(self, cls_sets: List) -> List:
        """
        Scale multiple CLS sets

        :param cls_sets: List of CLS sets
        :return: Scaling factors calculated and applied for each CLS set in order
        """
        scale_factor_list = []
        for cls_set in cls_sets:
            scale_factor = self.scale_cls_set(cls_set)
            scale_factor_list.append(scale_factor)
        return scale_factor_list

    def scale_cls_set(self, cls_set) -> ScaleFactor:
        """
        Scale a CLS set
        :param cls_set: Either a pair or regular conv layers or a triplet of depthwise separable layers
        :return: Scaling factor calculated and applied
        """
        if len(cls_set) == 3:
            scale_factor = self.scale_cls_set_with_depthwise_layers(cls_set)
        else:
            scale_factor = self.scale_cls_set_with_conv_layers(cls_set)

        return scale_factor

    @abstractmethod
    def scale_cls_set_with_conv_layers(self, cls_set) -> np.ndarray:
        """
        API to invoke equalize layer params (update for weights and bias is in place)

        :param cls_set: Consecutive Conv layers Tuple whose weights and biases need to be equalized
        :return: Scaling factor S_12 for each conv layer pair: numpy array
        """

    @abstractmethod
    def scale_cls_set_with_depthwise_layers(
        self, cls_set
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        API to invoke equalize layer params for depth wise separable layers(update for weights and bias is in place)

        :param cls_set: Consecutive Conv layers whose weights and biases need to be equalized.
                        Second Conv layer is a depth-wise conv and third conv layer is point-wise conv
        :return: Scaling factors S_12 and S_23 : numpy arrays
        """

    @staticmethod
    def create_cls_set_info_list(
        cls_sets: List, scale_factors: List[ScaleFactor], is_relu_activation_in_cls_sets
    ):
        """
        Binds information from there separate lists into one [ClsInfoSet] data-structure
        :param cls_sets: List of CLS sets
        :param scale_factors: Scale-factors for each cls-set
        :param is_relu_activation_in_cls_sets: Information if there is relu activation in each cls-set
        :return: List of ClsSetInfo
        """
        cls_set_info_list = []
        assert (
            len(cls_sets) == len(scale_factors) == len(is_relu_activation_in_cls_sets)
        )

        for index, cls_set in enumerate(cls_sets):
            if isinstance(scale_factors[index], tuple):
                # If we are dealing with a triplet of layers, then we should have 2 scale factors and 2 relu flags
                # Assert that this is true
                assert len(cls_set) == 3
                assert (
                    len(scale_factors[index])
                    == len(is_relu_activation_in_cls_sets[index])
                    == 2
                )

                cls_pair_1 = ClsSetInfo.ClsSetLayerPairInfo(
                    cls_set[0],
                    cls_set[1],
                    scale_factors[index][0],
                    is_relu_activation_in_cls_sets[index][0],
                )
                cls_pair_2 = ClsSetInfo.ClsSetLayerPairInfo(
                    cls_set[1],
                    cls_set[2],
                    scale_factors[index][1],
                    is_relu_activation_in_cls_sets[index][1],
                )

                cls_set_info = ClsSetInfo(cls_pair_1, cls_pair_2)

            else:
                cls_pair = ClsSetInfo.ClsSetLayerPairInfo(
                    cls_set[0],
                    cls_set[1],
                    scale_factors[index],
                    is_relu_activation_in_cls_sets[index],
                )

                cls_set_info = ClsSetInfo(cls_pair)

            cls_set_info_list.append(cls_set_info)

        return cls_set_info_list


class ClsImpl(ABC):
    """
    The Implementation interface declares methods common to both MO (c++) and python versions of CLS algorithm.
    """

    @abstractmethod
    def scale_cls_set_with_depthwise_layers(
        self, cls_set
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        API to invoke equalize layer params for depth wise separable layers(update for weights and bias is in place)

        :param cls_set: Consecutive Conv layers whose weights and biases need to be equalized.
                        Second Conv layer is a depth-wise conv and third conv layer is point-wise conv
        :return: Scaling factors S_12 and S_23 : numpy arrays
        """

    @abstractmethod
    def scale_cls_set_with_conv_layers(self, cls_set) -> np.ndarray:
        """
        API to invoke equalize layer params for regular conv layers (update for weights and bias is in place)

        :param cls_set: Consecutive Conv layers Tuple whose weights and biases need to be equalized
        :return: Scaling factor S_12 for each conv layer pair: numpy array
        """

    @staticmethod
    def compute_scaling_params_for_depthwise_conv(
        weight_0: np.ndarray, weight_1: np.ndarray, weight_2: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute scaling parameters for depth-wise separable layer.

        :param weight_0:
        :param weight_1:
        :param weight_2:
        :return: Scaling factors S_12 and S_23 : numpy arrays
        """
        max_0 = np.max(np.abs(weight_0), axis=(1, 2, 3))
        max_1 = np.max(np.abs(weight_1), axis=(1, 2, 3))
        max_2 = np.max(np.abs(weight_2), axis=(0, 2, 3))
        s_12 = max_0 / np.power(max_0 * max_1 * max_2, 1.0 / 3)
        s_23 = np.power(max_0 * max_1 * max_2, 1.0 / 3) / max_2

        # Avoid divide by zero, NaN or Inf by using a value that does no scaling. i.e., 1.
        s_12 = np.nan_to_num(s_12, nan=1.0, posinf=1.0)
        s_23 = np.nan_to_num(s_23, nan=1.0, posinf=1.0)
        s_12[s_12 == 0.0] = 1.0
        s_23[s_23 == 0.0] = 1.0

        return s_12, s_23

    @staticmethod
    def compute_scaling_params_for_conv(
        weight_0: np.ndarray, weight_1: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute scaling parameters for conv layer.
        :param weight_0:
        :param weight_1:
        :return:
        """
        max_0 = np.max(np.abs(weight_0), axis=(1, 2, 3))
        max_1 = np.max(np.abs(weight_1), axis=(0, 2, 3))
        scale_factor = max_0 / np.power(max_0 * max_1, 1.0 / 2)

        # Avoid divide by zero, NaN or Inf by using a value that does no scaling. i.e., 1.
        scale_factor = np.nan_to_num(scale_factor, nan=1.0, posinf=1.0)
        scale_factor[scale_factor == 0.0] = 1.0

        return scale_factor

    @staticmethod
    def fold_scaling_params_for_depthwise_conv(
        weight_0: np.ndarray,
        weight_1: np.ndarray,
        weight_2: np.ndarray,
        bias_0: np.ndarray,
        bias_1: np.ndarray,
        s_12: np.ndarray,
        s_23: np.ndarray,
    ):
        """
        Fold scaling parameters into weight matrices and biases.

        :param weight_0:
        :param weight_1:
        :param weight_2:
        :param bias_0:
        :param bias_1:
        :param s_12:
        :param s_23:
        """
        weight_0 = weight_0 * (1.0 / s_12[:, None, None, None])
        weight_1 = (
            weight_1 * s_12[:, None, None, None] * (1.0 / s_23[:, None, None, None])
        )
        weight_2 = weight_2 * s_23[None, :, None, None]
        if bias_0 is not None:
            bias_0 = bias_0 * (1.0 / s_12)
        if bias_1 is not None:
            bias_1 = bias_1 * (1.0 / s_23)

        return weight_0, weight_1, weight_2, bias_0, bias_1

    @staticmethod
    def fold_scaling_params_for_conv(
        weight_0: np.ndarray,
        weight_1: np.ndarray,
        bias_0: Union[np.ndarray, None],
        scale_factor: np.ndarray,
    ):
        """
        Fold scaling parameters into weight matrices and biases.
        :param weight_0:
        :param weight_1:
        :param bias_0:
        :param scale_factor:
        :return:
        """
        weight_0 = weight_0 * (1.0 / scale_factor[:, None, None, None])
        weight_1 = weight_1 * scale_factor[None, :, None, None]
        if bias_0 is not None:
            bias_0 = bias_0 * (1.0 / scale_factor)

        return weight_0, weight_1, bias_0


class HbfImpl(ABC):
    """
    The Implementation interface declares methods common to both MO (c++) and python versions of HBF algorithm.
    """

    @abstractmethod
    def bias_fold(self, cls_pair_info: ClsSetInfo.ClsSetLayerPairInfo, bn_layers: Dict):
        """
        Bias fold implementation.

        :param cls_pair_info: Layer pairs that were scaled using CLS and related information.
        :param bn_layers: Dictionary with Key being Conv/Linear layer and value being corresponding folded BN layer.
        """

    @staticmethod
    def _absorb_bias(
        activation_is_relu, beta, gamma, weight, bias_curr_layer, bias_prev_layer
    ) -> Tuple[np.ndarray, np.ndarray]:
        """

        :param activation_is_relu:
        :param beta:
        :param gamma:
        :param weight:
        :param bias_curr_layer:
        :param bias_prev_layer:
        """
        if not activation_is_relu:
            # No activation function, absorb whole bias
            absorb_bias = beta
        else:
            # Only absorb bias part that is more than 'min_std' standard deviations
            absorb_bias = np.maximum(0, beta - 3 * np.abs(gamma))

        # Calculate correction term for next layer
        weight_matrix = weight.sum(3).sum(2)
        if weight_matrix.shape[1] == 1:
            weight_matrix = weight_matrix.reshape(weight_matrix.shape[0])
            bias_correction = np.multiply(weight_matrix, absorb_bias)
        else:
            bias_correction = np.matmul(weight_matrix, absorb_bias)

        # Update bias for previous and current layers.
        bias_prev_layer = bias_prev_layer - absorb_bias
        bias_curr_layer = bias_curr_layer + bias_correction
        return bias_prev_layer, bias_curr_layer
