#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from typing import Any
from pypgx._utils.error_handling import java_handler


class GraphWiseValidationConfig:
    """GraphWise validation configuration."""

    _java_class = 'oracle.pgx.config.mllib.GraphWiseValidationConfig'

    def __init__(self, java_config, params) -> None:
        self._config = java_config
        self.params = params

    @property
    def evaluation_frequency(self) -> int:
        """Get the evaluation frequency.

        :return: evaluation frequency
        """
        return java_handler(self._config.getEvaluationFrequency, [])

    @property
    def evaluation_frequency_scale(self) -> Any:
        """Get the evaluation frequency scale.

        :return: evaluation frequency scale (options: "epoch" or "step")
        """
        return java_handler(self._config.getEvaluationFrequencyScale, [])

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
