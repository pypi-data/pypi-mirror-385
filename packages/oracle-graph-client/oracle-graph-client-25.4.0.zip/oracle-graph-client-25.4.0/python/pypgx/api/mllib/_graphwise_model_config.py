#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from typing import Dict, List, Optional, Union

from pypgx._utils import conversion
from pypgx._utils.error_handling import java_handler
from pypgx.api.mllib._graphwise_conv_layer_config import (
    GraphWiseAttentionLayerConfig,
    GraphWiseConvLayerConfig,
)
from pypgx.api.mllib._graphwise_validation_config import GraphWiseValidationConfig
from pypgx.api.mllib._input_property_config import InputPropertyConfig
from pypgx.api.mllib._mllib_conversion import (
    _java_input_property_list_to_python_configs,
    _java_conv_layer_configs_to_python_conv_layer_configs,
)


class GraphWiseModelConfig:
    """Graphwise Model Configuration class"""

    _java_class = "oracle.pgx.config.mllib.GraphWiseModelConfig"

    def __init__(self, java_graphwise_model_config) -> None:
        self._config = java_graphwise_model_config

    @property
    def shuffle(self) -> bool:
        """Whether or not shuffling is enabled."""
        return self._config.isShuffle()

    @property
    def input_feature_dim(self) -> int:
        """Get the input feature dimension."""
        return self._config.getInputFeatureDim()

    @property
    def edge_input_feature_dim(self) -> int:
        """Get the edge input feature dimension."""
        return self._config.getEdgeInputFeatureDim()

    @property
    def is_fitted(self) -> bool:
        """Whether or not the model is fitted."""
        return self._config.isFitted()

    @property
    def fitted(self) -> bool:
        """Whether or not the model is fitted."""
        return self.is_fitted

    @property
    def training_loss(self) -> float:
        """Get the training loss."""
        return self._config.getTrainingLoss()

    @property
    def batch_size(self) -> int:
        """Get the batch size."""
        return self._config.getBatchSize()

    @property
    def num_epochs(self) -> int:
        """Get the number of epochs."""
        return self._config.getNumEpochs()

    @property
    def learning_rate(self) -> float:
        """Get the learning rate."""
        return self._config.getLearningRate()

    @property
    def weight_decay(self) -> float:
        """Get the weight decay."""
        return self._config.getWeightDecay()

    @property
    def embedding_dim(self) -> int:
        """Get the embedding dimension."""
        return self._config.getEmbeddingDim()

    @property
    def seed(self) -> int:
        """Get the seed."""
        return self._config.getSeed()

    @property
    def conv_layer_configs(
        self,
    ) -> List[Union[GraphWiseConvLayerConfig, GraphWiseAttentionLayerConfig]]:
        """Get the conv layer configs."""
        return self.get_conv_layer_configs()

    @property
    def validation_config(self) -> GraphWiseValidationConfig:
        """Get the validation config."""
        return self.get_validation_config()

    @property
    def vertex_input_property_configs(self) -> Dict[str, InputPropertyConfig]:
        """Get the vertex input property configs."""
        java_vertex_input_property_configs = java_handler(
            self._config.getVertexInputPropertyConfigs, []
        )
        return _java_input_property_list_to_python_configs(java_vertex_input_property_configs)

    @property
    def edge_input_property_configs(self) -> Dict[str, InputPropertyConfig]:
        """Get the edge input property configs."""
        java_edge_input_property_configs = java_handler(
            self._config.getEdgeInputPropertyConfigs, []
        )
        return _java_input_property_list_to_python_configs(java_edge_input_property_configs)

    @property
    def vertex_input_property_names(self) -> Optional[List[str]]:
        """Get the vertex input property names."""
        names = self._config.getVertexInputPropertyNames()
        if not names:
            return None
        return names.toArray()

    @property
    def edge_input_property_names(self) -> Optional[List[str]]:
        """Get the edge input property names."""
        names = self._config.getEdgeInputPropertyNames()
        if not names:
            return None
        return names.toArray()

    @property
    def standardize(self) -> bool:
        """Whether or not standardization is enabled."""
        return self._config.isStandardize()

    @property
    def normalize(self) -> bool:
        """Whether or not normalization is enabled."""
        return self._config.isNormalize()

    @property
    def backend(self) -> str:
        """Get the backend."""
        return conversion.enum_to_python_str(self._config.getBackend())

    @property
    def enable_accelerator(self) -> str:
        """Get whether to use the accelerator if available."""
        return self._config.isEnableAccelerator()

    def get_conv_layer_configs(
        self,
    ) -> List[Union[GraphWiseConvLayerConfig, GraphWiseAttentionLayerConfig]]:
        """Return a list of conv layer configs"""
        java_conv_layer_configs = java_handler(self._config.getConvLayerConfigs, [])
        return _java_conv_layer_configs_to_python_conv_layer_configs(java_conv_layer_configs)

    def get_validation_config(self) -> GraphWiseValidationConfig:
        """Return the validation config"""
        java_validation_config = self._config.getValidationConfig()
        params = {
            "evaluation_frequency": java_validation_config.getEvaluationFrequency(),
            "evaluation_frequency_scale": conversion.enum_to_python_str(
                java_validation_config.getEvaluationFrequencyScale()
            ),
        }
        return GraphWiseValidationConfig(java_validation_config, params)

    def set_batch_size(self, batch_size: int) -> None:
        """Set the batch size

        :param batch_size: batch size
        :type batch_size: int
        """
        java_handler(self._config.setBatchSize, [batch_size])

    def set_num_epochs(self, num_epochs: int) -> None:
        """Set the number of epochs

        :param num_epochs: number of epochs
        :type num_epochs: int
        """
        java_handler(self._config.setNumEpochs, [num_epochs])

    def set_learning_rate(self, learning_rate: float) -> None:
        """Set the learning rate

        :param learning_rate: initial learning rate
        :type learning_rate: int
        """
        java_handler(self._config.setLearningRate, [learning_rate])

    def set_weight_decay(self, weight_decay: float) -> None:
        """Set the weight decay

        :param weight_decay: weight decay
        :type weight_decay: float
        """
        java_handler(self._config.setWeightDecay, [weight_decay])

    def set_embedding_dim(self, embedding_dim: int) -> None:
        """Set the embedding dimension

        :param embedding_dim: embedding dimension
        :type embedding_dim: int
        """
        java_handler(self._config.setEmbeddingDim, [embedding_dim])

    def set_seed(self, seed: int) -> None:
        """Set the seed

        :param seed: seed
        :type seed: int
        """
        java_handler(self._config.setSeed, [seed])

    def set_fitted(self, fitted: bool) -> None:
        """Set the fitted flag

        :param fitted: fitted flag
        :type fitted: bool
        """
        java_handler(self._config.setFitted, [fitted])

    def set_shuffle(self, shuffle: bool) -> None:
        """Set the shuffling flag

        :param shuffle: shuffling flag
        :type shuffle: bool
        """
        java_handler(self._config.setShuffle, [shuffle])

    def set_training_loss(self, training_loss: float) -> None:
        """Set the training loss

        :param training_loss: training loss
        :type training_loss: float
        """
        java_handler(self._config.setTrainingLoss, [training_loss])

    def set_input_feature_dim(self, input_feature_dim: int) -> None:
        """Set the input feature dimension

        :param input_feature_dim: input feature dimension
        :type input_feature_dim: int
        """
        java_handler(self._config.setInputFeatureDim, [input_feature_dim])

    def set_edge_input_feature_dim(self, edge_input_feature_dim: int) -> None:
        """Set the edge input feature dimension

        :param edge_input_feature_dim: edge input feature dimension
        :type edge_input_feature_dim: int
        """
        java_handler(self._config.setEdgeInputFeatureDim, [edge_input_feature_dim])

    def set_standardize(self, standardize: bool) -> None:
        """Set the standardize flag

        :param standardize: standardize flag
        :type standardize: bool
        """
        java_handler(self._config.setStandardize, [standardize])

    def set_normalize(self, normalize: bool) -> None:
        """Whether or not normalization is enabled."""
        java_handler(self._config.setNormalize, [normalize])

    def set_enable_accelerator(self, enable_accelerator: bool) -> None:
        """Set whether to use the accelerator if available

        :param shuffle: enable accelerator flag
        :type shuffle: bool
        """
        java_handler(self._config.setEnableAccelerator, [enable_accelerator])
