#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx.api.mllib._graphwise_embedding_config import GraphWiseEmbeddingConfig
from pypgx.api.mllib._graphwise_pred_layer_config import GraphWisePredictionLayerConfig


class GraphWiseDominantLayerConfig(GraphWiseEmbeddingConfig):
    """GraphWise dominant layer configuration."""

    _java_class = 'oracle.pgx.config.mllib.GraphWiseDominantLayerConfig'

    def __init__(self, java_config, params) -> None:
        self._config = java_config
        self.params = params

    def get_alpha(self) -> float:
        """Return alpha.

        :return: alpha of the decoder layer
        :rtype: float
        """
        if 'alpha' not in self.params:
            java_alpha = self._config.getAlpha()
            self.params['alpha'] = java_alpha
        return self.params['alpha']

    def set_alpha(self, alpha: float):
        """Set the alpha parameter

        :param alpha: The alpha parameter to set.
        :type alpha: float
        """
        self._config.setAlpha(alpha)
        self.params['alpha'] = alpha

    def get_decoder_layer_configs(self) -> GraphWisePredictionLayerConfig:
        """Get the configuration objects for the decoder layers.

        :return: configuration of the decoder layer
        :rtype: GraphWisePredictionLayerConfig
        """
        if 'decoder_layer_configs' not in self.params:
            self.params['decoder_layer_configs'] = None
        return self.params['decoder_layer_configs']

    def set_decoder_layer_configs(self, decoder_layer_configs: GraphWisePredictionLayerConfig):
        """Set the configuration objects for the decoder layers.

        :param decoder_layer_configs: configuration of the decoder layer
        :rtype: GraphWisePredictionLayerConfig
        """
        self._config.setDecoderLayerConfigs(decoder_layer_configs)
        self.params['decoder_layer_configs'] = decoder_layer_configs

    def get_embedding_type(self) -> str:
        """Return the embedding type used by this config

        :return: embedding type
        :rtype: str
        """
        if 'embedding_type' not in self.params:
            self.params['embedding_type'] = 'DOMINANT'
        return self.params['embedding_type']

    def _get_config(self):
        return self._config

    def __repr__(self) -> str:
        attributes = []
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
        return self._config.equals(other._config)
