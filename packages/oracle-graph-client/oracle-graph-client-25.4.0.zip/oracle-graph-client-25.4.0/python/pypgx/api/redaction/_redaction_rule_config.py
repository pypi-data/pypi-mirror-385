#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils.error_handling import java_handler
from typing import List


class PgxRedactionRuleConfig:
    """A class representing redaction rule configurations."""

    _java_class = 'oracle.pgx.config.PgxRedactionRuleConfig'

    def __init__(self, java_redaction_rule_config) -> None:
        self._redaction_rule_config = java_redaction_rule_config

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._redaction_rule_config.equals(other._redaction_rule_config)

    @property
    def label(self) -> str:
        """Getter for label property.

        :returns: Label string
        :rtype: str
        """
        return java_handler(self._redaction_rule_config.getLabel, [])

    @property
    def properties(self) -> List[str]:
        """Getter for properties.

        :returns: list of properties
        :rtype: List[str]
        """
        java_list = java_handler(self._redaction_rule_config.getProperties, [])
        return [java_list.get(i) for i in range(java_list.size())]

    @property
    def redact_edge(self) -> str:
        """Getter for redact_edge property.

        :returns: redact_edge string
        :rtype: str
        """
        return java_handler(self._redaction_rule_config.getRedactEdge, [])

    @property
    def rule_name(self) -> str:
        """Getter for rule_name property.

        :returns: rule_name string
        :rtype: str
        """
        return java_handler(self._redaction_rule_config.getRuleName, [])

    @property
    def rule_trigger(self) -> str:
        """Getter for rule_trigger property.

        :returns: rule_trigger string
        :rtype: str
        """
        return java_handler(self._redaction_rule_config.getRuleTrigger, [])

    @property
    def with_visible_properties(self) -> List[str]:
        """Getter for visible properties.

        :returns: Returns the list of visible properties
        :rtype: List[str]
        """
        java_list = java_handler(self._redaction_rule_config.getWithVisibleProperties, [])
        return [java_list.get(i) for i in range(java_list.size())]

    @property
    def __hash__(self) -> int:
        """Getter for hash of the object.

        :returns: Hash string
        :rtype: int
        """
        return java_handler(self._redaction_rule_config.hashCode, [])

    @property
    def is_empty(self) -> bool:
        """Getter for is_empty property.

        :returns: if the ruleset is empty.
        :rtype: bool
        """
        return java_handler(self._redaction_rule_config.isEmpty, [])
