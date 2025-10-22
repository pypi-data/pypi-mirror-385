#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#
from pypgx.api.mllib._input_property_config import InputPropertyConfig


class ContinuousFeatureConfig(InputPropertyConfig):
    """Configuration class for handling continuous input properties."""

    _java_class = "oracle.pgx.config.mllib.intputconfig.ContinuousFeatureConfig"

    def __init__(self, java_config, params) -> None:
        super().__init__(java_config, params)
        self._config = java_config
        self.params = params

    def __repr__(self) -> str:
        attributes = []
        for param in self.params:
            if param != "self":
                attributes.append("%s: %s" % (param, self.params[param]))
        return "%s(%s)" % (self.__class__.__name__, ", ".join(attributes))

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._config.equals(other._config)
