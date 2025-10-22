#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#
from pypgx.api._graph_builder import EdgeBuilder, GraphBuilder, VertexBuilder
from pypgx.api._pgx_graph import PgxGraph
from pypgx._utils.error_handling import java_handler
from pypgx._utils.error_messages import INVALID_OPTION, UNHASHABLE_TYPE
from pypgx._utils.pgx_types import (
    on_add_existing_element_types,
    on_invalid_change_types,
    on_required_conversion_types
)
from pypgx._utils import conversion
from typing import Union, TYPE_CHECKING, NoReturn

if TYPE_CHECKING:
    # Don't import at runtime, to avoid circular imports.
    from pypgx.api._pgx_session import PgxSession


class GraphChangeSet(GraphBuilder):
    """Class which stores changes of a particular graph.

    .. versionchanged:: 22.3
        The parameter names of the ``add_edge()`` method are now ``src``, ``dst``,
        and ``edge_id``, like in the superclass ``GraphBuilder``.

    .. versionchanged:: 22.4
        Like in the superclass ``GraphBuilder``, the parameter names are now as follows:

        * ``add_vertex()`` method parameters: ``vertex``.
        * ``reset_edge()`` method parameters: ``edge``.

    """

    _java_class = 'oracle.pgx.api.GraphChangeSet'

    def __init__(
        self, session: "PgxSession", java_graph_change_set, id_type: str = 'integer'
    ) -> None:
        """Construct a new change set.

        :param session: A 'PgxSession' object.
        :param java_graph_change_set: An instance of the corresponding java
            'GraphChangeSet' interface.
        :param id_type: A string describing the type of the ids. Optional.
            Defaults to 'integer'.
        """
        super().__init__(session, java_graph_change_set, id_type)
        self.session = session
        self.id_type = id_type
        self._change_set = java_graph_change_set

    def build_new_snapshot(self) -> "PgxGraph":
        """Build a new snapshot of the graph out of this GraphChangeSet.

        The resulting PgxGraph is a new snapshot of the PgxGraph object this was created from.

        :returns: A new object of type 'PgxGraph'
        """
        pgx_graph_java = java_handler(self._change_set.buildNewSnapshot, [])
        return PgxGraph(self.session, pgx_graph_java)

    def remove_edge(self, edge_id: int) -> "GraphChangeSet":
        """Remove an edge from the graph.

        :param edge_id: The edge id of the edge to remove.
        :returns: self
        """
        java_handler(self._change_set.removeEdge, [edge_id])
        return self

    def remove_vertex(self, vertex_id: Union[int, str]) -> "GraphChangeSet":
        """Remove a vertex from the graph.

        :param vertex_id: The vertex id of the vertex to remove.
        :returns: self
        """
        java_vertex = conversion.vertex_id_to_java(vertex_id, self.id_type)
        java_handler(self._change_set.removeVertex, [java_vertex])
        return self

    def set_add_existing_edge_policy(self, add_existing_edge_policy: str) -> "GraphChangeSet":
        """Set the policy on what to do when an edge is added that already exists

        :param add_existing_edge_policy: the new policy
        :return: this graph builder
        """
        if add_existing_edge_policy in on_add_existing_element_types:
            java_policy = on_add_existing_element_types[add_existing_edge_policy]
        else:
            raise ValueError(
                INVALID_OPTION.format(var='type', opts=[*on_add_existing_element_types])
            )

        java_handler(self._change_set.setAddExistingEdgePolicy, [java_policy])
        return self

    def set_add_existing_vertex_policy(self, add_existing_vertex_policy: str) -> "GraphChangeSet":
        """Set the policy on what to do when a vertex is added that already exists

        :param add_existing_vertex_policy: the new policy
        :return: this graph builder
        """
        if add_existing_vertex_policy in on_add_existing_element_types:
            java_policy = on_add_existing_element_types[add_existing_vertex_policy]
        else:
            raise ValueError(
                INVALID_OPTION.format(var='type', opts=[*on_add_existing_element_types])
            )

        java_handler(self._change_set.setAddExistingVertexPolicy, [java_policy])
        return self

    def set_invalid_change_policy(self, invalid_change_policy: str) -> "GraphChangeSet":
        """Set the policy on what to do when an invalid action is added

        :param invalid_change_policy: the new policy
        :return: this graph builder
        """
        if invalid_change_policy in on_invalid_change_types:
            java_policy = on_invalid_change_types[invalid_change_policy]
        else:
            raise ValueError(
                INVALID_OPTION.format(var='type', opts=[*on_invalid_change_types])
            )

        java_handler(self._change_set.setInvalidChangePolicy, [java_policy])
        return self

    def set_required_conversion_policy(self, required_conversion_policy: str) -> "GraphChangeSet":
        """Set the policy on what to do when an invalid type is encountered

        :param required_conversion_policy: the new policy
        :return: this graph builder
        """
        if required_conversion_policy in on_required_conversion_types:
            java_policy = on_required_conversion_types[required_conversion_policy]
        else:
            raise ValueError(
                INVALID_OPTION.format(var='type', opts=[*on_required_conversion_types])
            )

        java_handler(self._change_set.setRequiredConversionPolicy, [java_policy])
        return self

    def update_edge(self, edge_id: int) -> "EdgeModifier":
        """Return an 'EdgeModifier' with which you can update edge properties and the edge label.

        :param edge_id: The edge id of the edge to be updated
        :returns: An 'EdgeModifier'
        """
        java_edge_modifier = java_handler(self._change_set.updateEdge, [edge_id])
        return EdgeModifier(self.session, java_edge_modifier, self.id_type)

    def update_vertex(self, vertex_id: Union[int, str]) -> "VertexModifier":
        """Return a 'VertexModifier' with which you can update vertex properties.

        :param vertex_id: The vertex id of the vertex to be updated
        :returns: A 'VertexModifier'
        """
        java_vertex = conversion.vertex_id_to_java(vertex_id, self.id_type)
        java_vertex_modifier = java_handler(self._change_set.updateVertex, [java_vertex])
        return VertexModifier(self.session, java_vertex_modifier, self.id_type)

    def __repr__(self) -> str:
        s = self._change_set.toString()
        changes = s[s.find('with added') :]
        return "{}(session id: {}, {})".format(self.__class__.__name__, self.session.id, changes)

    def __hash__(self) -> NoReturn:
        raise TypeError(UNHASHABLE_TYPE.format(type_name=self.__class__))


class VertexModifier(GraphChangeSet, VertexBuilder):
    """A class to modify existing vertices of a graph."""

    _java_class = 'oracle.pgx.api.VertexModifier'

    def __init__(
        self, session: "PgxSession", java_vertex_modifier, id_type: str = 'integer'
    ) -> None:
        """Construct a new vertex modifier.

        :param session: The current 'PgxSession' object.
        :param java_vertex_modifier: An instance of the corresponding java
            'VertexModifier' interface.
        :param id_type: A string describing the type of the ids. Optional.
            Defaults to 'integer'.
        """
        GraphChangeSet.__init__(self, session, java_vertex_modifier, id_type)
        VertexBuilder.__init__(self, session, java_vertex_modifier, id_type)
        self.session = session
        self.id_type = id_type
        self._vertex_modifier = java_vertex_modifier

    def get_id(self) -> int:
        """Get the id of the element (vertex or edge) this builder belongs to.

        :returns: The id of this builder.
        """
        v_id = java_handler(self._vertex_modifier.getId, [])
        return v_id

    def remove_label(self, label: str) -> "VertexModifier":
        """Remove the given label from the vertex.

        :param label: The label to remove.
        :returns: self
        """
        java_handler(self._vertex_modifier.removeLabel, [label])
        return self

    def __hash__(self) -> NoReturn:
        raise TypeError(UNHASHABLE_TYPE.format(type_name=self.__class__))


class EdgeModifier(GraphChangeSet, EdgeBuilder):
    """A class to modify existing edges of a graph."""

    _java_class = 'oracle.pgx.api.EdgeModifier'

    def __init__(self, session: "PgxSession", java_edge_modifier, id_type: str = 'integer') -> None:
        """Construct a new edge modifier.

        :param session: The current 'PgxSession' object.
        :param java_edge_modifier: An instance of the corresponding java
            'EdgeModifier' interface.
        :param id_type: A string describing the type of the ids. Optional.
            Defaults to 'integer'.
        """
        GraphChangeSet.__init__(self, session, java_edge_modifier, id_type)
        EdgeBuilder.__init__(self, session, java_edge_modifier, id_type)
        self.session = session
        self.id_type = id_type
        self._edge_modifier = java_edge_modifier

    def __hash__(self) -> NoReturn:
        raise TypeError(UNHASHABLE_TYPE.format(type_name=self.__class__))
