#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#
from typing import List, Optional, Union

from pypgx.api.mllib._graphwise_conv_layer_config import (
    GraphWiseConvLayerConfig,
    GraphWiseAttentionLayerConfig,
)
from pypgx.api.frames import PgxFrame
from pypgx.api.mllib._input_property_config import InputPropertyConfig
from pypgx._utils.error_handling import java_handler
from pypgx._utils.error_messages import MODEL_NOT_FITTED
from pypgx.api.mllib._model import Model
from pypgx.api.mllib._edgewise_model_config import EdgeWiseModelConfig
from pypgx.api.mllib._edge_combination_method import (
    EdgeCombinationMethod,
    ConcatEdgeCombinationMethod,
    ProductEdgeCombinationMethod,
)
from pypgx.api.mllib._mllib_conversion import _java_conv_layer_configs_to_python_conv_layer_configs


class EdgeWiseModel(Model):
    """EdgeWise model object.

    This is a base class for :class:`SupervisedEdgeWiseModel`.
    """

    _java_class = 'oracle.pgx.api.mllib.EdgeWiseModel'

    def __init__(self, java_edgewise_model, params=None) -> None:
        if params is None:
            params = {}
        self._model = java_edgewise_model
        super().__init__(self._model)
        self.params = params
        self._update_is_fitted()

    def _update_is_fitted(self) -> None:
        """Determine whether the model is fitted.

        This updates the internal state.

        :return: None
        """
        # Determining whether the model has been fitted is relevant especially for
        # models that are being loaded from a file.
        self._is_fitted = self._model.isFitted()
        self.loss = self._model.getTrainingLoss()
        self.vertex_input_feature_dim = self._model.getInputFeatureDim()
        self.edge_input_feature_dim = self._model.getEdgeInputFeatureDim()

    def _check_is_fitted(self) -> None:
        """Make sure the model is fitted.

        :return: None
        :raise: RuntimeError if the model is not fitted
        """
        self._update_is_fitted()
        if not self._is_fitted:
            raise RuntimeError(MODEL_NOT_FITTED)

    def get_num_epochs(self) -> int:
        """Get the number of epochs to train the model

        :return: number of epochs to train the model
        :rtype: int
        """
        if 'num_epochs' not in self.params:
            self.params['num_epochs'] = self._model.getNumEpochs()
        return self.params['num_epochs']

    def get_learning_rate(self) -> float:
        """Get the initial learning rate

        :return: initial learning rate
        :rtype: float
        """
        if 'learning_rate' not in self.params:
            self.params['learning_rate'] = self._model.getLearningRate()
        return self.params['learning_rate']

    def get_batch_size(self) -> int:
        """Get the batch size

        :return: batch size
        :rtype: int
        """
        if 'batch_size' not in self.params:
            self.params['batch_size'] = self._model.getBatchSize()
        return self.params['batch_size']

    def get_layer_size(self) -> int:
        """Get the dimension of the embeddings

        :return: embedding dimension
        :rtype: int
        """
        if 'layer_size' not in self.params:
            self.params['layer_size'] = self._model.getEmbeddingDim()
        return self.params['layer_size']

    def get_seed(self) -> int:
        """Get the random seed

        :return: random seed
        :rtype: int
        """
        if 'seed' not in self.params:
            self.params['seed'] = self._model.getSeed()
        return self.params['seed']

    def get_edge_combination_method(self) -> EdgeCombinationMethod:
        """Get the edge combination method used to compute the edge embedding

        :return: edge combination method
        :rtype: EdgeCombinationMethod
        """
        if 'edge_combination_method' not in self.params:
            java_edge_combination_method = self._model.getEdgeCombinationMethod()
            params = {
                'use_source_vertex': java_edge_combination_method.isUseSourceVertex(),
                'use_destination_vertex': java_edge_combination_method.isUseDestinationVertex(),
                'use_edge': java_edge_combination_method.isUseEdge(),
            }
            method = java_edge_combination_method.getAggregationType().name()
            if method == "CONCATENATION":
                self.params['edge_combination_method'] = ConcatEdgeCombinationMethod(**params)
            elif method == "PRODUCT":
                self.params['edge_combination_method'] = ProductEdgeCombinationMethod(**params)
            else:
                raise ValueError

        return self.params['edge_combination_method']

    def get_conv_layer_config(
        self
    ) -> List[Union[GraphWiseConvLayerConfig, GraphWiseAttentionLayerConfig]]:
        """Get the configuration objects for the convolutional layers

        :return: configurations
        """
        if 'conv_layer_config' not in self.params:
            java_conv_layer_configs = java_handler(self._model.getConvLayerConfigs, [])
            conv_layer_configs = _java_conv_layer_configs_to_python_conv_layer_configs(
                java_conv_layer_configs
            )
            self.params['conv_layer_config'] = conv_layer_configs
        return self.params['conv_layer_config']

    def get_vertex_input_property_configs(self) -> List[InputPropertyConfig]:
        """Get the configuration objects for vertex input properties

        :return: configurations
        """
        if 'vertex_input_property_configs' not in self.params:
            self.params['vertex_input_property_configs'] = None
        return self.params['vertex_input_property_configs']

    def get_edge_input_property_configs(self) -> List[InputPropertyConfig]:
        """Get the configuration objects for edge input properties"""
        if 'edge_input_property_configs' not in self.params:
            self.params['edge_input_property_configs'] = None
        return self.params['edge_input_property_configs']

    def get_config(self) -> EdgeWiseModelConfig:
        """Return the GraphWiseModelConfig object

        :return: the config
        :rtype: GraphWiseModelConfig
        """
        java_config = java_handler(self._model.getConfig, [])
        return EdgeWiseModelConfig(java_config)

    def get_vertex_input_property_names(self) -> Optional[List[str]]:
        """Get the vertices input feature names

        :return: vertices input feature names
        :rtype: list(str)
        """
        if 'vertex_input_property_names' not in self.params:
            self.params['vertex_input_property_names'] = None
        return self.params['vertex_input_property_names']

    def get_edge_input_property_names(self) -> Optional[List[str]]:
        """Get the edges input feature names

        :return: edges input feature names
        :rtype: list(str)
        """
        if 'edge_input_property_names' not in self.params:
            self.params['edge_input_property_names'] = None
        return self.params['edge_input_property_names']

    def is_fitted(self) -> bool:
        """Check if the model is fitted

        :return: `True` if the model is fitted, `False` otherwise
        :rtype: bool
        """
        self._update_is_fitted()
        return self._is_fitted

    def get_training_loss(self) -> float:
        """Get the final training loss

        :return: training loss
        :rtype: float
        """
        self._check_is_fitted()
        return self.loss

    def get_training_log(self) -> PgxFrame:
        """Get the log of validation during the training.

        :return: training log
        :rtype: PgxFrame
        """
        java_frame = self._model.getTrainingLog()
        return PgxFrame(java_frame)

    def get_vertex_input_feature_dim(self) -> int:
        """Get the input feature dimension, that is, the dimension of all the input vertex
        properties when concatenated

        :return: input feature dimension
        :rtype: int
        """
        self._check_is_fitted()
        return self.vertex_input_feature_dim

    def get_edge_input_feature_dim(self) -> int:
        """Get the edges input feature dimension, that is, the dimension of all the input edge
        properties when concatenated

        :return: edges input feature dimension
        :rtype: int
        """
        self._check_is_fitted()
        return self.edge_input_feature_dim

    def __repr__(self) -> str:
        attributes = []
        self._update_is_fitted()
        attributes.append('fitted: %s' % self._is_fitted)
        if self._is_fitted:
            attributes.append('loss: %.5f' % self.loss)
        for param in self.params:
            if param != 'self':
                attributes.append('%s: %s' % (param, self.params[param]))
        return '%s(%s)' % (self.__class__.__name__, ', '.join(attributes))

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._model.equals(other._model)
