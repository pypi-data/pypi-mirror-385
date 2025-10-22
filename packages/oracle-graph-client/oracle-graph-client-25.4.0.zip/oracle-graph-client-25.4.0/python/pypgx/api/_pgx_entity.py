#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils.error_handling import java_handler
from pypgx._utils.error_messages import ABSTRACT_METHOD, INVALID_OPTION, PROPERTY_NOT_FOUND
from pypgx._utils.pgx_types import direction_types

from typing import Any, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    # Don't import at runtime, to avoid circular imports.
    from pypgx.api._pgx_graph import PgxGraph
    from pypgx.api._property import EdgeProperty, PgxProperty, VertexProperty


class PgxEntity:
    """An abstraction of vertex and edge."""

    _java_class = 'oracle.pgx.api.PgxEntity'

    def __init__(self, graph: "PgxGraph", java_entity) -> None:
        self._entity = java_entity
        self.graph = graph

    @property
    def type(self) -> str:
        """Get the entity type."""
        return self._entity.getType().toString()

    @property
    def id(self):
        """Get the entity id."""
        return java_handler(
            self._entity.getId,
            [],
            expected_pgx_exception="java.lang.UnsupportedOperationException",
        )

    def set_property(self, property_name: str, value: Any) -> None:
        """Set an entity property.

        :param property_name: Property name
        :param value: New value
        """

        # We set the property via the PgxProperty object because only that object knows what Java
        # type 'value' needs to be converted to (integer vs. long, double vs. float).
        prop = self._get_graph_property(property_name)
        if prop is None:
            raise LookupError(PROPERTY_NOT_FOUND.format(prop=property_name))
        prop.set(self, value)

    def get_property(self, property_name: str) -> Any:
        """Get a property by name.

        :param property_name: Property name
        """

        # We get the property via the PgxProperty object because only that object knows what Java
        # type this property value is coming from (need to distinguish boolean vs. integer).
        # Workaround for https://github.com/kivy/pyjnius/issues/602, see also GM-28290.
        prop = self._get_graph_property(property_name)
        if prop is None:
            raise LookupError(PROPERTY_NOT_FOUND.format(prop=property_name))
        return prop.get(self)

    def _get_graph_property(self, property_name: str) -> Optional["PgxProperty"]:
        """Get a PgxProperty for this entity's graph by name, or return None if none exists."""
        raise NotImplementedError(ABSTRACT_METHOD)

    def __repr__(self) -> str:
        return java_handler(self._entity.toString, [])

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> int:
        return hash((str(self), str(self.graph.name)))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return bool(self._entity.equals(other._entity))


class PgxVertex(PgxEntity):
    """A vertex of a :class:`PgxGraph`."""

    _java_class = 'oracle.pgx.api.PgxVertex'

    def __init__(self, graph: "PgxGraph", java_vertex) -> None:
        super().__init__(graph, java_vertex)
        self._vertex = java_vertex

    @property
    def out_degree(self) -> int:
        """Get the out degree of the vertex."""
        return self._vertex.getOutDegree()

    @property
    def in_degree(self) -> int:
        """Get the in degree of the vertex."""
        return self._vertex.getInDegree()

    @property
    def degree(self) -> int:
        """Get the degree of the vertex."""
        return java_handler(self._vertex.getDegree, [])

    @property
    def labels(self) -> List[str]:
        """Get the vertex labels."""
        return list(java_handler(self._vertex.getLabels, []))

    @property
    def out_neighbors(self) -> List["PgxVertex"]:
        """Return all outgoing neighbors of this vertex, i.e., all nodes this vertex has an edge to.

        If the graph is a multi-graph and if the vertex has multiple edges to a vertex 'A',
        then 'A' will appear multiple times in the result, i.e., once per edge to 'A'.
        This method does not guarantee any ordering in the result. This method never returns null.
        """
        java_out_neighbors = self._vertex.getOutNeighbors()
        out_neighbors = []
        for neighbor in java_out_neighbors:
            out_neighbors.append(PgxVertex(self.graph, neighbor))
        return out_neighbors

    @property
    def in_neighbors(self) -> List["PgxVertex"]:
        """Return all incoming neighbors of this vertex: all vertices with an edge to this vertex.

        If the graph is a multi-graph and if a vertex 'A' has multiple edges to this vertex,
        then 'A' will appear multiple times in the result, i.e. once per edge from 'A' to this
        vertex. This method does not guarantee any ordering in the result.
        """
        java_in_neighbors = self._vertex.getInNeighbors()
        in_neighbors = []
        for neighbor in java_in_neighbors:
            in_neighbors.append(PgxVertex(self.graph, neighbor))
        return in_neighbors

    def get_neighbors(self, direction: str, remove_duplicates: bool = False) -> List["PgxVertex"]:
        """Return all neighbors of this vertex: all vertices with an edge to or from this vertex.

        :param direction: One of ("outgoing","incoming","both")
        :param remove_duplicates:  If removeDuplicates is set to true,
             the resulting collection does not contain any duplicates. Otherwise,
             if this vertex is connected 'N' times to a vertex 'X',
             vertex 'X' also appears 'N' times in the results.
             This method does not guarantee any ordering in the result.
             This method never returns null.
        """
        if direction not in direction_types:
            raise ValueError(
                INVALID_OPTION.format(var='direction', opts=list(direction_types.keys()))
            )
        java_neighbors = java_handler(
            self._vertex.getNeighbors, [direction_types[direction], remove_duplicates]
        )
        neighbors = []
        for neighbor in java_neighbors:
            neighbors.append(PgxVertex(self.graph, neighbor))
        return neighbors

    @property
    def out_edges(self) -> List["PgxEdge"]:
        """Return a list of outgoing edges."""
        java_out_edges = self._vertex.getOutEdges()
        out_edges = []
        for edge in java_out_edges:
            out_edges.append(PgxEdge(self.graph, edge))
        return out_edges

    @property
    def in_edges(self) -> List["PgxEdge"]:
        """Return a list of ingoing edges."""
        java_in_edges = self._vertex.getInEdges()
        in_edges = []
        for edge in java_in_edges:
            in_edges.append(PgxEdge(self.graph, edge))
        return in_edges

    def _get_graph_property(self, property_name: str) -> Optional["VertexProperty"]:
        return self.graph.get_vertex_property(property_name)


class PgxEdge(PgxEntity):
    """An edge of a :class:`PgxGraph`."""

    _java_class = 'oracle.pgx.api.PgxEdge'

    def __init__(self, graph: "PgxGraph", java_edge) -> None:
        super().__init__(graph, java_edge)
        self._edge = java_edge

    @property
    def source(self) -> PgxVertex:
        """Get the source vertex of the edge."""
        return PgxVertex(self.graph, self._edge.getSource())

    @property
    def destination(self) -> PgxVertex:
        """Get the destination vertex of the edge."""
        return PgxVertex(self.graph, self._edge.getDestination())

    @property
    def vertices(self) -> Tuple[PgxVertex, PgxVertex]:
        """Return the source and the destination vertex."""
        return (self.source, self.destination)

    @property
    def label(self) -> str:
        """Return the edge label."""
        return java_handler(self._edge.getLabel, [])

    def _get_graph_property(self, property_name: str) -> Optional["EdgeProperty"]:
        return self.graph.get_edge_property(property_name)
