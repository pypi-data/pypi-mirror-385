#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from collections.abc import Sequence
from itertools import islice

from jnius import autoclass
from jnius.jnius import JavaClass

from pypgx.api._pgx_id import PgxId
from pypgx.api._pgx_context_manager import PgxContextManager
from pypgx.api._pgx_entity import PgxEdge, PgxVertex, PgxEntity
from pypgx._utils.error_handling import java_handler
from pypgx._utils.error_messages import (
    ABSTRACT_METHOD,
    COMPARE_VECTOR,
    INVALID_OPTION,
    WRONG_SIZE_PROPERTY,
)
from pypgx._utils import conversion
from pypgx._utils.pgx_types import property_types
from pypgx._utils.pyjnius_helper import PyjniusHelper
from pypgx.api._pgx_map import PgxMap
from typing import Any, Iterator, List, Optional, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    # Don't import at runtime, to avoid circular imports.
    from pypgx.api._pgx_graph import PgxGraph


JavaPgxVect = autoclass("oracle.pgx.api.PgxVect")


class PgxProperty(PgxContextManager):
    """A property of a `PgxGraph`.

    .. note: This is a base class of :class:`VertexProperty` and :class:`EdgeProperty`,
       and is not instantiated on its own.
    """

    _java_class = 'oracle.pgx.api.Property'

    def __init__(self, graph: "PgxGraph", java_prop) -> None:
        self._prop = java_prop
        self.graph = graph

    @property
    def name(self) -> str:
        """Name of this property."""
        return self._prop.getName()

    @property
    def entity_type(self) -> str:
        """Entity type of this property."""
        return self._prop.getEntityType().toString()

    @property
    def type(self) -> str:
        """Return the type of this property."""
        return self._prop.getType().toString()

    @property
    def is_transient(self) -> bool:
        """Whether this property is transient."""
        return bool(self._prop.isTransient())

    @property
    def dimension(self) -> int:
        """Return the dimension of this property."""
        return self._prop.getDimension()

    @property
    def size(self) -> int:
        """Return the number of elements in this property."""
        return self._prop.size()

    @property
    def is_vector_property(self) -> bool:
        """Whether this property is a vector property."""
        return bool(self._prop.isVectorProperty())

    @property
    def is_published(self) -> bool:
        """Check if this property is published.

        :return: `True` if this property is published, `False` otherwise.
        :rtype: bool
        """
        return bool(self._prop.isPublished())

    def publish(self) -> None:
        """Publish the property into a shared graph so it can be shared between sessions.

        :return: None
        """
        java_handler(self._prop.publish, [])

    def rename(self, name: str) -> None:
        """Rename this property.

        :param name: New name
        :return: None
        """
        java_handler(self._prop.rename, [name])

    def clone(self, name: Optional[str] = None) -> "PgxProperty":
        """Create a copy of this property.

        :param name: name of copy to be created. If `None`, guaranteed unique name will be
            generated.
        :return: property result
        :rtype: this class
        """
        cloned_prop = java_handler(self._prop.clone, [name])
        return self.__class__(self.graph, cloned_prop)

    def get_top_k_values(self, k: int) -> List[Tuple[PgxEntity, Any]]:
        """Get the top k vertex/edge value pairs according to their value.

        :param k: How many top values to retrieve, must be in the range between 0 and number of
            nodes/edges (inclusive)
        :return: list of `k` key-value tuples where the keys vertices/edges and the values are
            property values, sorted in ascending order
        :rtype: list of tuple(PgxVertex or PgxEdge, Any)

        """
        if self.is_vector_property:
            raise RuntimeError(COMPARE_VECTOR)

        top_k = java_handler(self._prop.getTopKValues, [k])
        it = top_k.iterator()
        return list(
            (
                conversion.entity_to_python(item.getKey(), self.graph),
                conversion.property_to_python(item.getValue(), self.type, self.graph),
            )
            for item in it
        )

    def get_bottom_k_values(self, k: int) -> List[Tuple[PgxEntity, Any]]:
        """Get the bottom k vertex/edge value pairs according to their value.

        :param k: How many top values to retrieve, must be in the range between 0 and number of
            nodes/edges (inclusive)
        """
        if self.is_vector_property:
            raise RuntimeError(COMPARE_VECTOR)

        bottom_k = java_handler(self._prop.getBottomKValues, [k])
        it = bottom_k.iterator()
        return list(
            (
                conversion.entity_to_python(item.getKey(), self.graph),
                conversion.property_to_python(item.getValue(), self.type, self.graph),
            )
            for item in it
        )

    def get_values(self) -> List[Tuple[PgxEntity, Any]]:
        """Get the values of this property as a list.

        :return: a list of key-value tuples, where each key is a vertex and each key is the value
            assigned to that vertex
        :rtype: list of tuple(PgxVertex, set of str)
        """
        return list(self)

    def set_values(self, values: PgxMap) -> None:
        """Set the labels values.

        :param values: pgxmap with ids and values
        :type values: PgxMap
        """
        values_keys = values.keys()
        for key in values_keys:
            self.set(key, values.get(key))

    def get(self, key: Union[PgxEntity, int, str]) -> Any:
        """Get a property value.

        :param key: The key (vertex/edge) whose property to get
        """
        java_key = self._get_java_pgx_entity(key)
        java_value = java_handler(PyjniusHelper.getFromPropertyByKey, [self._prop, java_key])
        return conversion.property_to_python(java_value, self.type, self.graph)

    def set(self, key: Union[PgxEntity, int, str], value: Any) -> None:
        """Set a property value.

        :param key: The key (vertex/edge) whose property to set
        :param value: The property value
        """
        java_key = self._get_java_pgx_entity(key)
        if self.is_vector_property:
            java_value = self._to_java_pgx_vect(value)
        else:
            java_value = conversion.property_to_java(value, self.type)
        java_handler(self._prop.set, [java_key, java_value])

    def fill(self, value: Any) -> None:
        """Fill this property with a given value.

        :param value: The value
        """
        if self.is_vector_property:
            java_value = self._to_java_pgx_vect(value)
        else:
            java_value = conversion.property_to_java(value, self.type)
        java_handler(self._prop.fill, [java_value])

    def expand(self) -> Union["PgxProperty", List["PgxProperty"]]:
        """If this is a vector property, expands this property into a list of scalar properties of
        same type.

        The first property will contain the first element of the vector, the second property the
        second element and so on.
        """
        if self.is_vector_property:
            expanded = java_handler(self._prop.expand, [])
            expanded_list = []
            for p in expanded:
                expanded_list.append(self.__class__(self.graph, p))
            return expanded_list
        else:
            return self

    def close(self) -> None:
        """Free resources on the server taken up by this Property.

        :return: None
        """
        java_handler(self._prop.close, [])

    def get_property_id(self) -> PgxId:
        """Get an internal identifier for this property.

        Only meant for internal usage.

        :return: the internal identifier of this property
        """
        return PgxId(self._prop.getPropertyId())

    def wrap(self, property_value: Any, property_type: str) -> Any:
        """Take a property value and wraps it pgx entities if applicable

        :param property_value: property value
        :param property_type: A valid property type.
        """
        if property_type not in property_types.keys():
            raise ValueError(
                INVALID_OPTION.format(var='property_type', opts=list(property_types.keys()))
            )
        if isinstance(property_value, (int, str)) and property_type == 'vertex':
            item = java_handler(self.graph._graph.getVertex, [property_value])
            return PgxVertex(self.graph, item)
        elif isinstance(property_value, (int, str)) and property_type == 'edge':
            item = java_handler(self.graph._graph.getEdge, [property_value])
            return PgxEdge(self.graph, item)
        else:
            return property_value

    def destroy(self) -> None:
        """Free resources on the server taken up by this Property.

        :return: None
        """
        java_handler(self._prop.destroy, [])

    def __iter__(self) -> Iterator[Tuple[PgxEntity, Any]]:
        it = self._prop.getValues().iterator()
        return (
            (
                conversion.entity_to_python(item.getKey(), self.graph),
                conversion.property_to_python(item.getValue(), self.type, self.graph),
            )
            for item in it
        )

    def __getitem__(self, key: Union[slice, PgxEntity, int, str]) -> Any:
        if isinstance(key, slice):
            it = self._prop.getValues().iterator()
            return list(
                (
                    conversion.entity_to_python(item.getKey(), self.graph),
                    conversion.property_to_python(item.getValue(), self.type, self.graph),
                )
                for item in islice(it, key.start, key.stop, key.step)
            )
        else:
            return self.get(key)

    def __setitem__(self, key: Union[PgxEntity, int, str], value: Any) -> None:
        self.set(key, value)

    def __len__(self) -> int:
        return self.size

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
        return bool(self._prop.equals(other._prop))

    def _get_java_pgx_entity(self, key: Union[PgxEntity, int, str]) -> JavaClass:
        """Get a Java PgxEdge or PgxVertex by ID or by Python PgxEdge/PgxVertex."""
        raise NotImplementedError(ABSTRACT_METHOD)

    def _to_java_pgx_vect(self, value: Any) -> JavaClass:
        """Convert a value or sequence of values to a Java PgxVect."""

        if isinstance(value, Sequence) and not isinstance(value, str):
            if len(value) != self.dimension:
                msg = WRONG_SIZE_PROPERTY.format(size=self.dimension, got=len(value))
                raise ValueError(msg)
            value_as_list = [conversion.property_to_java(v, self.type) for v in value]
        else:
            value = conversion.property_to_java(value, self.type)
            value_as_list = [value] * self.dimension
        return JavaPgxVect(value_as_list, property_types[self.type])


class VertexProperty(PgxProperty):
    """A vertex property of a :class:`PgxGraph`."""

    _java_class = 'oracle.pgx.api.VertexProperty'

    @staticmethod
    def _from_java(java_prop):
        # need to import here to avoid import loop
        from pypgx.api._pgx_session import PgxSession
        from pypgx.api._pgx_graph import PgxGraph

        java_graph = java_handler(java_prop.getGraph, [])
        java_session = java_handler(java_graph.getSession, [])
        graph = PgxGraph(PgxSession(java_session), java_graph)
        return VertexProperty(graph, java_prop)

    def _get_java_pgx_entity(self, key: Union[PgxEntity, int, str]) -> JavaClass:
        if isinstance(key, PgxEntity):
            return key._entity
        return java_handler(self.graph._graph.getVertex, [key])


class EdgeProperty(PgxProperty):
    """An edge property of a :class:`PgxGraph`."""

    _java_class = 'oracle.pgx.api.EdgeProperty'

    def _get_java_pgx_entity(self, key: Union[PgxEntity, int, str]) -> JavaClass:
        if isinstance(key, PgxEntity):
            return key._entity
        return java_handler(self.graph._graph.getEdge, [key])


class VertexLabels(VertexProperty):
    """Class for storing labels for vertices.

    A vertex can have multiple labels. In effect this is a :class:`VertexProperty`
    where a set of strings is associated to each vertex.
    """

    _java_class = 'oracle.pgx.api.VertexLabels'


class EdgeLabel(EdgeProperty):
    """Class for storing a label type edge property."""

    _java_class = 'oracle.pgx.api.EdgeLabel'
