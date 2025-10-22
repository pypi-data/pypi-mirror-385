#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils.error_handling import java_handler


class InputPropertyConfig:
    """Configuration class for handling input properties using one hot encoding method."""

    _java_class = "oracle.pgx.config.mllib.inputconfig.InputPropertyConfig"

    def __init__(self, java_config, params) -> None:
        self._config = java_config
        self.params = params

    @property
    def property_name(self) -> str:
        """Get the name of the feature that the configuration is used for.

        :return: name of the feature that the configuration is used for
        """
        return java_handler(self._config.getPropertyName, [])

    @property
    def categorical(self) -> bool:
        """Get whether the feature is categorical.

        :return: whether the feature is categorical
        """
        return java_handler(self._config.getCategorical, [])

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
