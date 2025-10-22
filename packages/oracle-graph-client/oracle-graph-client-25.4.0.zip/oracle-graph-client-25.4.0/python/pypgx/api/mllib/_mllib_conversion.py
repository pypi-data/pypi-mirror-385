#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#
from typing import Dict, List, Union
from jnius import cast

from pypgx._utils import conversion
from pypgx.api.mllib._input_property_config import InputPropertyConfig
from pypgx.api.mllib._one_hot_encoding_config import OneHotEncodingConfig
from pypgx.api.mllib._embedding_table_config import EmbeddingTableConfig
from pypgx.api.mllib._continuous_property_config import ContinuousFeatureConfig
from pypgx.api.mllib._graphwise_conv_layer_config import (
    GraphWiseAttentionLayerConfig,
    GraphWiseConvLayerConfig,
)
from pypgx._utils.error_messages import INVALID_OPTION


def _java_input_property_list_to_python_configs(java_input_property_configs_map) -> \
        Dict[str, InputPropertyConfig]:
    input_property_configs: Dict[str, InputPropertyConfig] = {}
    for prop_name, java_config in conversion.map_to_python(java_input_property_configs_map).items():
        if java_config.getCategorical():
            config = cast(
                'oracle.pgx.config.mllib.inputconfig.CategoricalPropertyConfig', java_config
            )
            embedding_type = conversion.enum_to_python_str(config.getCategoricalEmbeddingType())
            if embedding_type == "one_hot_encoding":
                config = cast('oracle.pgx.config.mllib.inputconfig.OneHotEncodingConfig', config)
                input_property_configs[prop_name] = OneHotEncodingConfig(config, {})
            elif embedding_type == "embedding_table":
                config = cast('oracle.pgx.config.mllib.inputconfig.EmbeddingTableConfig', config)
                input_property_configs[prop_name] = EmbeddingTableConfig(config, {})
            else:
                raise ValueError("Type of the InputPropertyConfig not recognized")
        else:
            config = cast(
                'oracle.pgx.config.mllib.inputconfig.ContinuousPropertyConfig', java_config
            )
            input_property_configs[prop_name] = ContinuousFeatureConfig(config, {})
    return input_property_configs


def _java_conv_layer_configs_to_python_conv_layer_configs(
    java_conv_layer_configs
) -> List[Union[GraphWiseConvLayerConfig, GraphWiseAttentionLayerConfig]]:
    conv_layer_configs: List[Union[GraphWiseConvLayerConfig, GraphWiseAttentionLayerConfig]] = []
    for java_config in java_conv_layer_configs:
        layer_type = conversion.enum_to_python_str(java_config.getConvLayerType())
        params = {
            "num_sampled_neighbors": java_config.getNumSampledNeighbors(),
            "activation_fn": conversion.enum_to_python_str(java_config.getActivationFunction()),
            "weight_init_scheme": conversion.enum_to_python_str(java_config.getWeightInitScheme()),
            "vertex_to_vertex_connection": java_config.getVertexToVertexConnection(),
            "edge_to_vertex_connection": java_config.getEdgeToVertexConnection(),
            "vertex_to_edge_connection": java_config.getVertexToEdgeConnection(),
            "edge_to_edge_connection": java_config.getEdgeToEdgeConnection(),
            "dropout_rate": java_config.getDropoutRate(),
        }
        if layer_type == "conv":
            config = cast(
                'oracle.pgx.config.mllib.GraphWiseConvLayerConfig', java_config
            )
            params.update({
                "neighbor_weight_property_name": config.getNeighborWeightPropertyName(),
            })
            conv_layer_configs.append(GraphWiseConvLayerConfig(config, params))
        elif layer_type == "gat_conv":
            config = cast(
                'oracle.pgx.config.mllib.GraphWiseAttentionLayerConfig', java_config
            )
            params.update({
                "num_heads": config.getNumHeads(),
                "head_aggregation": conversion.enum_to_python_str(config.getHeadAggregation()),
            })
            conv_layer_configs.append(GraphWiseAttentionLayerConfig(config, params))
        else:
            raise ValueError(
                INVALID_OPTION.format(
                    var='conv_layer_config',
                    opts='GraphWiseConvLayerConfig, GraphWiseAttentionLayerConfig'
                )
            )
    return conv_layer_configs
