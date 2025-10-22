#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#
from typing import Any, TYPE_CHECKING

from pypgx.api._pgx_context_manager import PgxContextManager
from pypgx._utils.error_handling import java_handler
from pypgx._utils import conversion

if TYPE_CHECKING:
    # Don't import at runtime, to avoid circular imports.
    from pypgx.api._pgx_graph import PgxGraph


class Scalar(PgxContextManager):
    """A scalar value."""

    _java_class = 'oracle.pgx.api.Scalar'

    def __init__(self, graph: "PgxGraph", java_scalar) -> None:
        self._scalar = java_scalar
        self.graph = graph

    @property
    def name(self) -> str:
        """Name of the scalar.

        :return: The name of the scalar.
        :rtype: str
        """
        return self._scalar.getName()

    @property
    def type(self) -> str:
        """Type of the scalar.

        :return: The type of the scalar.
        :rtype: str
        """
        return self._scalar.getType().toString()

    def set(self, value: Any) -> None:
        """Set the scalar value.

        :param value: Value to be assigned.
        :type value: Any
        """
        if isinstance(value, (int, str)) and self.type == 'vertex':
            java_value = java_handler(self.graph._graph.getVertex, [value])
        elif isinstance(value, (int, str)) and self.type == 'edge':
            java_value = java_handler(self.graph._graph.getEdge, [value])
        else:
            java_value = conversion.property_to_java(value, self.type)
        java_handler(self._scalar.set, [java_value])

    def get(self) -> Any:
        """Get scalar value.

        :return: The scalar value.
        :rtype: Any
        """
        value = java_handler(self._scalar.get, [])
        return conversion.property_to_python(value, self.type, self.graph)

    def destroy(self) -> None:
        """Free resources on the server taken up by this Scalar."""
        java_handler(self._scalar.destroy, [])

    def get_dimension(self) -> int:
        """Get the scalar's dimension.

        :return: The scalar's dimension.
        :rtype: int
        """
        return java_handler(self._scalar.getDimension, [])

    def __repr__(self) -> str:
        return "{}(name: {}, type: {}, graph: {})".format(
            self.__class__.__name__, self.name, self.type, self.graph.name
        )

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> int:
        return hash((str(self), str(self.graph.name)))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return bool(self._scalar.equals(other._scalar))
