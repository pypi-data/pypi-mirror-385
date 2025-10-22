#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils.error_messages import INVALID_OPTION
from pypgx._utils import conversion
from pypgx._utils.pgx_types import DISCRIMINATOR_FUNCTIONS, READOUT_FUNCTIONS
from pypgx.api.mllib._corruption_function import PermutationCorruption
from pypgx.api.mllib._graphwise_embedding_config import GraphWiseEmbeddingConfig


class GraphWiseDgiLayerConfig(GraphWiseEmbeddingConfig):
    """GraphWise dgi layer configuration."""

    _java_class = 'oracle.pgx.config.mllib.GraphWiseDgiLayerConfig'

    def __init__(self, java_config, params) -> None:
        self._config = java_config
        self.params = params

    def get_corruption_function(self) -> PermutationCorruption:
        """Return the corruption function"""
        if 'corruption_function' not in self.params:
            java_corruption_function = self._config.getCorruptionFunction()
            self.params['corruption_function'] = PermutationCorruption(java_corruption_function)
        return self.params['corruption_function']

    def set_corruption_function(self, corruption_function):
        """Set the corruption function

        :param corruption_function: the corruption function.
               Supported currently: :class:`PermutationCorruption`
        :type corruption_function: CorruptionFunction
        """
        self.params['corruption_function'] = corruption_function
        self._config.setCorruptionFunction(corruption_function._corruption_function)

    def get_discriminator(self) -> str:
        """Return the discriminator"""
        if 'discriminator' not in self.params:
            self.params['discriminator'] = conversion.enum_to_python_str(
                self._config.getDiscriminator()
            )
        return self.params['discriminator']

    def set_discriminator(self, discriminator: str) -> None:
        """Set the discriminator

        :param discriminator: The discriminator function.
               Supported currently: 'bilinear'
        :type discriminator: str
        """
        if discriminator not in DISCRIMINATOR_FUNCTIONS.keys():
            raise ValueError(
                INVALID_OPTION.format(
                    var='discriminator',
                    opts=', '.join(DISCRIMINATOR_FUNCTIONS.keys())
                )
            )
        self._config.setDiscriminator(DISCRIMINATOR_FUNCTIONS[discriminator])
        self.params['discriminator'] = DISCRIMINATOR_FUNCTIONS[discriminator]

    def get_readout_function(self) -> str:
        """Return the readout function"""
        if 'readout_function' not in self.params:
            self.params['readout_function'] = conversion.enum_to_python_str(
                self._config.getReadoutFunction()
            )
        return self.params['readout_function']

    def set_readout_function(self, readout_function: str) -> None:
        """Set the readout function

        :param readout_function: The readout function.
               Supported currently: 'mean'
        :type readout_function: str
        """
        if readout_function not in READOUT_FUNCTIONS.keys():
            raise ValueError(
                INVALID_OPTION.format(
                    var='readout_function',
                    opts=', '.join(READOUT_FUNCTIONS.keys())
                )
            )
        self._config.setReadoutFunction(READOUT_FUNCTIONS[readout_function])
        self.params['readout_function'] = READOUT_FUNCTIONS[readout_function]

    def get_embedding_type(self) -> str:
        """Return the embedding type used by this config"""
        if 'embedding_type' not in self.params:
            self.params['embedding_type'] = 'DGI'
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
