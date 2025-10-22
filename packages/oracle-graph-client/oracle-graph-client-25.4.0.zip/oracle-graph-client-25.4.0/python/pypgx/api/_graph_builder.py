#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#


import warnings
from typing import cast, Any, Optional, Union, TYPE_CHECKING, NoReturn

from pypgx.api._pgx_graph import PgxGraph
from pypgx._utils.error_handling import java_handler
from pypgx._utils import conversion, pgx_types
from pypgx._utils.error_messages import INVALID_OPTION, UNHASHABLE_TYPE
from pypgx._utils.pgx_types import (
    id_generation_strategies,
    graph_builder_config_fields,
)


if TYPE_CHECKING:
    # Don't import at runtime, to avoid circular imports.
    from pypgx.api._pgx_session import PgxSession


class GraphBuilder:
    """A graph builder for constructing a :class:`PgxGraph`."""

    _java_class = 'oracle.pgx.api.GraphBuilder'

    def __init__(self, session: "PgxSession", java_graph_builder, id_type: str) -> None:
        self._builder = java_graph_builder
        self.session = session
        self.id_type = id_type

    def set_data_source_version(self, version: str) -> None:
        """
        Set the version information for the built graph or snapshot.

        :param version:
        """
        java_handler(self._builder.setDataSourceVersion, [version])

    def add_vertex(self, vertex: Optional[Union[str, int]] = None) -> "VertexBuilder":
        """Add the vertex with the given id to the graph builder.

        If the vertex doesn't exist it is added, if it exists a builder for that vertex is
        returned Throws an UnsupportedOperationException if vertex ID generation strategy is set
        to IdGenerationStrategy.AUTO_GENERATED.

        :param vertex: The ID of the new vertex
        :returns: A vertexBuilder instance
        """
        if vertex is None:
            vb = java_handler(self._builder.addVertex, [])
        else:
            java_vertex = conversion.vertex_id_to_java(vertex, self.id_type)
            vb = java_handler(self._builder.addVertex, [java_vertex])
        return VertexBuilder(self.session, vb, self.id_type)

    def reset_vertex(self, vertex: Union["VertexBuilder", str, int]):
        """Reset any change for the given vertex.

        :param vertex: The id or the vertexBuilder object to reset
        :returns: self
        """
        if isinstance(vertex, VertexBuilder):
            casted_vertex = vertex._builder.getId()
            vertex = cast(Union[str, int], casted_vertex)

        java_vertex = conversion.vertex_id_to_java(vertex, self.id_type)
        java_handler(self._builder.resetVertex, [java_vertex])
        return self

    def reset_edge(self, edge: Union["EdgeBuilder", str, int]):
        """Reset any change for the given edge.

        :param edge: The id or the EdgeBuilder object to reset
        :returns: self
        """
        if isinstance(edge, EdgeBuilder):
            edge = edge._builder.getId()

        java_handler(self._builder.resetEdge, [edge])
        return self

    def add_edge(
        self,
        src: Union["VertexBuilder", str, int],
        dst: Union["VertexBuilder", str, int],
        edge_id: Optional[int] = None,
    ) -> "EdgeBuilder":
        """
        Add an edge with the given edge ID and the given source and destination vertices.

        :param src: Source VertexBuilder or ID
        :param dst: Destination VertexBuilder or ID
        :param edge_id: the ID of the new edge
        :returns: An 'EdgeBuilder' instance containing the added edge.
        """
        if isinstance(src, VertexBuilder):
            java_src = src._builder
        else:
            java_src = conversion.property_to_java(src, self.id_type)

        if isinstance(dst, VertexBuilder):
            java_dst = dst._builder
        else:
            java_dst = conversion.property_to_java(dst, self.id_type)

        args = [edge_id, java_src, java_dst] if edge_id is not None else [java_src, java_dst]
        eb = java_handler(self._builder.addEdge, args)
        return EdgeBuilder(self.session, eb, self.id_type)

    def build(self, name: Optional[str] = None) -> PgxGraph:
        """
        :param name: The new name of the graph. If None, a name is generated.
        :return: PgxGraph object
        """
        graph = java_handler(self._builder.build, [name])
        return PgxGraph(self.session, graph)

    def set_config_parameter(
        self,
        parameter: str,
        value: Union[bool, str]
    ) -> None:
        """
        Set the given configuration parameter to the given value

        :param parameter: the config parameter to set
        :param value:     the new value for the config parameter
        """
        warnings.warn(
            "`set_config_parameter` is deprecated since 25.1, use specific setter methods instead,",
            DeprecationWarning
        )
        if parameter in graph_builder_config_fields:
            java_parameter = graph_builder_config_fields[parameter]
        else:
            raise ValueError(
                INVALID_OPTION.format(
                    var='parameter', opts=list(graph_builder_config_fields.keys())
                )
            )

        if isinstance(value, bool):
            java_value = pgx_types.Boolean(value)
        elif value in id_generation_strategies:
            java_value = id_generation_strategies[value]
        else:
            raise ValueError(
                INVALID_OPTION.format(
                    var='value',
                    opts=list(["True", "False"] + [*id_generation_strategies])
                )
            )

        java_handler(self._builder.setConfigParameter, [java_parameter, java_value])

    def get_config_parameter(self, parameter: str) -> Union[bool, str]:
        """
        Retrieve the value for the given config parameter

        :param parameter: the config parameter to get the value for
        :return: the value for the given config parameter
        """
        if parameter in graph_builder_config_fields:
            java_parameter = graph_builder_config_fields[parameter]
        else:
            raise ValueError(
                INVALID_OPTION.format(var='parameter',
                                      opts=[*graph_builder_config_fields])
            )

        java_value = java_handler(self._builder.getConfigParameter, [java_parameter])

        value : Union[bool, str]
        if isinstance(java_value, int):
            value = bool(java_value)
        else:
            value = next(k for k, v in id_generation_strategies.items() if v == java_value)
        return value

    def set_retain_edge_ids(self, retain_edge_ids: bool) -> "GraphBuilder":
        """
        Control whether to retain the vertex ids provided in this graph builder are to be
        retained in the final graph.
        If True retain the vertex ids, if False use internally generated edge ids.

        :param retain_edge_ids: Whether or not to retain edge ids
        :return: self
        """
        java_handler(self._builder.setRetainEdgeIds, [retain_edge_ids])
        return self

    def set_retain_vertex_ids(self, retain_vertex_ids: bool) -> "GraphBuilder":
        """
        Control whether to retain the vertex ids provided in this graph builder are to be
        retained in the final graph.
        If True retain the vertex ids, if False use internally generated vertex ids of type Integer.

        :param retain_vertex_ids: Whether or not to retain vertex ids
        :return: self
        """
        java_handler(self._builder.setRetainVertexIds, [retain_vertex_ids])
        return self

    def set_retain_ids(self, retain_ids: bool) -> "GraphBuilder":
        """
        Control for both vertex and edge ids whether to retain them in the final graph.

        :param retain_ids: Whether or not to retain vertex and edge ids
        :return: self
        """
        java_handler(self._builder.setRetainIds, [retain_ids])
        return self

    def set_vertex_id_generation_strategy(
        self,
        vertex_id_generation_strategy: str
    ) -> "GraphBuilder":
        """
        Define the ID generation strategy the GraphBuilder should use for vertices.
        :param vertex_id_generation_strategy: Id generation strategy
        :return: self
        """
        java_handler(self._builder.setVertexIdGenerationStrategy, [vertex_id_generation_strategy])
        return self

    def set_edge_id_generation_strategy(self, edge_id_generation_strategy: str) -> "GraphBuilder":
        """
        Define the ID generation strategy the GraphBuilder should use for edges.
        :param edge_id_generation_strategy: Id generation strategy
        :return: self
        """
        java_handler(self._builder.setEdgeIdGenerationStrategy, [edge_id_generation_strategy])
        return self

    def partitioned_vertex_ids(self, partitioned_ids: bool) -> "GraphBuilder":
        """
        Specify if the final graph should use partitioned ids for vertices.
        Partitioned Ids can be used only in the context of building a
        partitioned graph, and only if the original Ids are retained
        :param partitioned_ids: whether or not to use partitioned ids
        for vertices in the final graph
        :return: self
        """
        java_handler(self._builder.partitionedVertexIds, [partitioned_ids])
        return self

    def partitioned_edge_ids(self, partitioned_ids: bool) -> "GraphBuilder":
        """
        Specify if the final graph should use partitioned ids for edges.
        Partitioned Ids can be used only in the context of building a
        partitioned graph, and only if the original Ids are retained
        :param partitioned_ids: whether or not to use partitioned ids
        for edges in the final graph
        :return: self
        """
        java_handler(self._builder.partitionedEdgeIds, [partitioned_ids])
        return self

    def __repr__(self) -> str:
        return "{}(session id: {})".format(self.__class__.__name__, self.session.id)

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> NoReturn:
        raise TypeError(UNHASHABLE_TYPE.format(type_name=self.__class__))


class VertexBuilder(GraphBuilder):
    """A vertex builder for defining vertices added with the :class:`GraphBuilder`."""

    _java_class = 'oracle.pgx.api.VertexBuilder'

    def __init__(self, session: "PgxSession", java_vertex_builder, id_type: str) -> None:
        super().__init__(session, java_vertex_builder, id_type)
        self._builder = java_vertex_builder

    def set_property(self, key: str, value: Any) -> "VertexBuilder":
        """Set the property value of this vertex with the given key to the given value.

        The first time this method is called, the type of *value* defines the type of the property.

        .. versionchanged:: 22.3
            If the type of *value* is Python's ``int``, the resulting property
            now always has PGX's property type ``long`` (64 bits).

        :param key: The property key
        :param value: The value of the vertex property
        :returns: The VertexProperty object
        """
        value = conversion.anything_to_java(value)
        java_handler(self._builder.setProperty, [key, value])
        return self

    def add_label(self, label: str) -> "VertexBuilder":
        """Add the given label to this vertex.

        :param label: The label to be added.
        :returns: The VertexProperty object
        """
        java_handler(self._builder.addLabel, [label])
        return self

    def is_ignored(self) -> bool:
        """Whether this vertex builder ignores method calls (True) or if it performs calls
        as usual (False). Some issues, such as incompatible changes in a ChangeSet, can
        be configured to be ignored. In that case, additional method calls on the returned vertex
        builder object will be ignored.
        """
        return java_handler(self._builder.isIgnored, [])

    @property
    def id(self) -> Union[str, int]:
        """Get the id of the element (vertex or edge) this builder belongs to."""
        return self._builder.getId()

    def __hash__(self) -> NoReturn:
        raise TypeError(UNHASHABLE_TYPE.format(type_name=self.__class__))


class EdgeBuilder(GraphBuilder):
    """An edge builder for defining edges added with the :class:`GraphBuilder`."""

    _java_class = 'oracle.pgx.api.EdgeBuilder'

    def __init__(self, session: "PgxSession", java_edge_builder, id_type: str) -> None:
        super().__init__(session, java_edge_builder, id_type)
        self._builder = java_edge_builder

    def set_property(self, key: str, value: Any) -> "EdgeBuilder":
        """Set the property value of this edge with the given key to the given value.

        The first time this method is called, the type of *value* defines the type of the property.

        .. versionchanged:: 22.3
            If the type of *value* is Python's ``int``, the resulting property
            now always has PGX's property type ``long`` (64 bits).

        :param key: The property key
        :param value: The value of the vertex property
        :returns: The EdgeBuilder object
        """
        value = conversion.anything_to_java(value)
        java_handler(self._builder.setProperty, [key, value])
        return self

    def set_label(self, label: str) -> "EdgeBuilder":
        """Set the new value of the label.

        :param label: The new value of the label
        :returns: The EdgeBuilder object
        """
        java_handler(self._builder.setLabel, [label])
        return self

    def is_ignored(self) -> bool:
        """Whether this edge builder ignores method calls (True) or if it performs calls
        as usual (False. Some issues, such as incompatible changes in a ChangeSet, can
        be configured to be ignored. In that case, additional method calls on the returned edge
        builder object will be ignored.
        """
        return java_handler(self._builder.isIgnored, [])

    @property
    def id(self) -> int:
        """Get the id of the element (vertex or edge) this builder belongs to."""
        return self._builder.getId()

    def __hash__(self) -> NoReturn:
        raise TypeError(UNHASHABLE_TYPE.format(type_name=self.__class__))
