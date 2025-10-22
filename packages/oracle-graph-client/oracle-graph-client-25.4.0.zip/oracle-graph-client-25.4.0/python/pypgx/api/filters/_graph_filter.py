#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils.error_handling import java_handler
from pypgx._utils.error_messages import ARG_MUST_BE, INVALID_OPTION
from pypgx._utils.pgx_types import filter_types
from pypgx.api._pgx_id import PgxId
from pypgx.api._pgx_entity import PgxVertex
from jnius import autoclass, cast
from pypgx.api._pgql_result_set import PgqlResultSet
from pypgx.api._pgx_collection import PgxCollection, EdgeCollection, VertexCollection
from typing import Union


class GraphFilter:
    """A class to filter vertices and/or egdes of a graph."""

    _java_class = 'oracle.pgx.api.filter.GraphFilter'

    def __init__(self, java_filter) -> None:
        if not isinstance(java_filter, (VertexFilter, EdgeFilter, PathFindingFilter)):
            self._filter = java_filter
            self.filter_type = java_filter.getType().toString()

    def intersect(self, other: "GraphFilter") -> "GraphFilter":
        """Intersect this filter with another graph-filter object.

        :param other: The other graph-filter
        :type other: GraphFilter

        :raises TypeError: `other` argument must be a GraphFilter.
            It can be an instance of a subclass,
            such as VertexFilter or EdgeFilter.

        :returns: An object representing the filter intersection.
        :rtype: GraphFilter
        """
        if isinstance(other, GraphFilter):
            return GraphFilter(java_handler(self._filter.intersect, [other._filter]))
        else:
            raise TypeError(ARG_MUST_BE.format(arg='other', type=GraphFilter))

    def union(self, other: "GraphFilter") -> "GraphFilter":
        """Union this filter with another graph-filter object.

        :param other: The other graph-filter
        :type other: GraphFilter

        :raises TypeError: `other` argument must be a GraphFilter.
            It can be an instance of a subclass,
            such as VertexFilter or EdgeFilter.

        :returns: An object representing the filter union.
        :rtype: GraphFilter
        """
        if isinstance(other, GraphFilter):
            return GraphFilter(java_handler(self._filter.union, [other._filter]))
        else:
            raise TypeError(ARG_MUST_BE.format(arg='other', type=GraphFilter))

    def has_expression(self) -> bool:
        """Check if this GraphFilter object has an expression associated with it.

        :returns: Boolean indicating if the filter has an expression.
        :rtype: bool
        """
        return self._filter.hasExpression()

    def __repr__(self) -> str:
        return "{}".format(self._filter.toString())

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._filter.equals(other._filter)

    @staticmethod
    def from_type_and_expression(
        filter_type: str, filter_expression: str
    ) -> Union["VertexFilter", "EdgeFilter"]:
        """Instantiate a new filter using an expression and type.

        :param filter_expression: Filter expression.
        :type filter_expression: str
        :param filter_type: The filter type, can be either "vertex" or "edge".
        :type filter_type: str

        :raises TypeError: `filter_expression` must be a string.
        :raises ValueError: `vertex_filter` must be either "vertex" or "edge".

        :returns: The new filter.
        :rtype: Union[VertexFilter, EdgeFilter]
        """
        if not isinstance(filter_expression, str):
            raise TypeError(ARG_MUST_BE.format(arg='filter_expression', type=str.__name__))
        if filter_type == 'vertex':
            java_filter = java_handler(filter_types[filter_type], [filter_expression])
            return VertexFilter(java_filter)
        elif filter_type == 'edge':
            java_filter = java_handler(filter_types[filter_type], [filter_expression])
            return EdgeFilter(java_filter)
        else:
            raise ValueError(INVALID_OPTION.format(var='filter_type', opts="edge or vertex"))

    def is_result_set_filter(self) -> bool:
        """Check if the filter is acting on a result set.

        :returns: True if the filter is acting on a result set.
        :rtype: bool
        """
        return java_handler(self._filter.isResultSetFilter, [])

    def is_collection_filter(self) -> bool:
        """Check if the filter is using a collection.

        :returns: True if the filter is using a collection.
        :rtype: bool
        """
        return java_handler(self._filter.isCollectionFilter, [])

    def is_path_finding_filter(self) -> bool:
        """Check if the filter is a path finding filter.

        :returns: True if the filter is a path finding filter.
        :rtype: bool
        """
        return java_handler(self._filter.isPathFindingFilter, [])

    def is_binary_operation(self) -> bool:
        """Check if this :class:`GraphFilter` object represents a binary operation.

        :returns: True, if this GraphFilter object represents a binary operation.
        :rtype: bool
        """
        return java_handler(self._filter.isBinaryOperation, [])

    def get_filter_expression(self) -> str:
        """Fetch the filter expression of the current filter.

        :returns: Filter expression.
        :rtype: str
        """
        return java_handler(self._filter.getFilterExpression, [])

    def as_vertex_filter(self):  # noqa: D102
        raise NotImplementedError

    def as_edge_filter(self):  # noqa: D102
        raise NotImplementedError

    def as_graph_filter_with_expression(self):  # noqa: D102
        raise NotImplementedError

    def as_binary_graph_filter_operation(self):  # noqa: D102
        raise NotImplementedError


class VertexFilter(GraphFilter):
    """A filter based on an expression that is meant to be evaluated on each vertex of the graph."""

    _java_class = 'oracle.pgx.api.filter.VertexFilter'

    def __init__(self, filter_expr: str) -> None:
        if isinstance(filter_expr, str):
            java_filter = java_handler(filter_types['vertex'], [filter_expr])
            super().__init__(java_filter)
        else:
            super().__init__(filter_expr)

    @classmethod
    def from_expression(cls, filter_expression: str) -> "VertexFilter":
        """Instantiate a new vertex filter using an expression.

        :param filter_expression: The vertex-filter expression.
        :type filter_expression: str

        :raises TypeError: `filter_expression` must be a string.

        :returns: The new filter.
        :rtype: VertexFilter
        """
        if not isinstance(filter_expression, str):
            raise TypeError(ARG_MUST_BE.format(arg='filter_expression', type=str.__name__))
        return cls(filter_expression)

    @staticmethod
    def from_pgql_result_set(
        result_set: PgqlResultSet, column_name: str
    ) -> "ResultSetVertexFilter":
        """Instantiate a new result set vertex filter.

        :param result_set: The result set on which the filter acts.
        :type result_set: PgqlResultSet
        :param column_name: The column name to be fetched from the result set.
        :type column_name: str

        :raises TypeError: `result_set` must be a PgqlResultSet.
        :raises TypeError: `column_name` must be a string.

        :returns: The new filter.
        :rtype: ResultSetVertexFilter
        """
        if not isinstance(result_set, PgqlResultSet):
            raise TypeError(ARG_MUST_BE.format(arg='result_set', type=PgqlResultSet.__name__))
        if not isinstance(column_name, str):
            raise TypeError(ARG_MUST_BE.format(arg='column_name', type=str.__name__))
        java_result_set = result_set._pgql_result_set
        vertex_filter_class = filter_types['vertex']
        java_result_set_vertex_filter = java_handler(
            vertex_filter_class.fromPgqlResultSet, [java_result_set, column_name]
        )
        java_class = autoclass("oracle.pgx.api.filter.internal.ResultSetVertexFilter")
        java_result_set_vertex_filter = cast(java_class, java_result_set_vertex_filter)
        return ResultSetVertexFilter(java_result_set_vertex_filter)

    @staticmethod
    def from_collection(vertex_collection: VertexCollection) -> "VertexFilter":
        """Instantiate a new vertex collection vertex filter.

        :param vertex_collection: The collection on which the filter acts.
        :type vertex_collection: VertexCollection

        :raises TypeError: `vertex_collection` must be a VertexCollection.

        :returns: The new filter.
        :rtype: VertexCollectionFilter
        """
        if not isinstance(vertex_collection, PgxCollection):
            raise TypeError(
                ARG_MUST_BE.format(arg='vertex_collection', type=PgxCollection.__name__)
            )
        java_collection = vertex_collection._collection
        vertex_filter_class = filter_types['vertex']
        java_vertex_filter = java_handler(vertex_filter_class.fromCollection, [java_collection])
        java_class = autoclass('oracle.pgx.api.filter.internal.VertexCollectionFilter')
        java_vertex_filter = cast(java_class, java_vertex_filter)
        return VertexCollectionFilter(java_vertex_filter)


class EdgeFilter(GraphFilter):
    """A filter based on an expression that is meant to be evaluated on each edge of the graph."""

    _java_class = 'oracle.pgx.api.filter.EdgeFilter'

    def __init__(self, filter_expr: str) -> None:
        if isinstance(filter_expr, str):
            java_filter = java_handler(filter_types['edge'], [filter_expr])
            super().__init__(java_filter)
        else:
            super().__init__(filter_expr)

    @classmethod
    def from_expression(cls, filter_expression: str) -> "EdgeFilter":
        """Instantiate a new edge filter using an expression.

        :param filter_expression: The edge-filter expression.
        :type filter_expression: str

        :raises TypeError: `filter_expression` must be a VertexCollection.

        :returns: The new filter.
        :rtype: EdgeFilter
        """
        if not isinstance(filter_expression, str):
            raise TypeError(ARG_MUST_BE.format(arg='filter_expression', type=str.__name__))
        return cls(filter_expression)

    @staticmethod
    def from_pgql_result_set(result_set: PgqlResultSet, column_name: str) -> "ResultSetEdgeFilter":
        """Instantiate a new result set edge filter.

        :param result_set: The result set on which the filter acts.
        :type result_set: PgqlResultSet
        :param column_name: The column name to be fetched from the result set.
        :type column_name: str

        :raises TypeError: `result_set` must be a PgqlResultSet.
        :raises TypeError: `column_name` must be a string.

        :returns: the new filter
        :rtype: ResultSetEdgeFilter
        """
        if not isinstance(result_set, PgqlResultSet):
            raise TypeError(ARG_MUST_BE.format(arg='result_set', type=PgqlResultSet.__name__))
        if not isinstance(column_name, str):
            raise TypeError(ARG_MUST_BE.format(arg='column_name', type=str.__name__))
        java_result_set = result_set._pgql_result_set
        edge_filter_class = filter_types['edge']
        java_result_set_edge_filter = java_handler(
            edge_filter_class.fromPgqlResultSet, [java_result_set, column_name]
        )
        java_class = autoclass("oracle.pgx.api.filter.internal.ResultSetEdgeFilter")
        java_result_set_edge_filter = cast(java_class, java_result_set_edge_filter)
        return ResultSetEdgeFilter(java_result_set_edge_filter)

    @staticmethod
    def from_collection(edge_collection: EdgeCollection) -> "EdgeFilter":
        """Instantiate a new edge collection edge filter.

        :param edge_collection: The collection on which the filter acts.
        :type edge_collection: EdgeCollection

        :raises TypeError: `edge_collection` must be a EdgeCollection.

        :returns: The new edge filter.
        :rtype: EdgeFilter
        """
        if not isinstance(edge_collection, PgxCollection):
            raise TypeError(ARG_MUST_BE.format(arg='edge_collection', type=PgxCollection.__name__))
        java_collection = edge_collection._collection
        edge_filter_class = filter_types['edge']
        java_edge_filter = java_handler(edge_filter_class.fromCollection, [java_collection])
        java_class = autoclass('oracle.pgx.api.filter.internal.EdgeCollectionFilter')
        java_edge_filter = cast(java_class, java_edge_filter)
        return EdgeCollectionFilter(java_edge_filter)


class ResultSetVertexFilter(VertexFilter):
    """Represents a vertex filter used to create a vertex set out of the PGQL result set.

    This is a wrapper storing the column name that will be fetched from the result set
    and the result set id in addition to what is inside a :class:`VertexFilter`.
    """

    _java_class = 'oracle.pgx.api.filter.ResultSetVertexFilter'

    def __str__(self) -> str:
        return java_handler(self._filter.toString, [])

    def get_result_set_id(self) -> str:
        """Get the result set id.

        :returns: The result set id.
        :rtype: str
        """
        return java_handler(self._filter.getResultSetId, [])

    def get_column_name(self) -> str:
        """Get the column name.

        :returns: The column name.
        :rtype: str
        """
        return java_handler(self._filter.getColumnName, [])


class ResultSetEdgeFilter(EdgeFilter):
    """Represents an edge filter used to create a edge set out of the PGQL result set.

    This is a wrapper storing the column name that will be fetched from the result set
    and the result set id in addition to what is inside an :class:`EdgeFilter`.
    """

    _java_class = 'oracle.pgx.api.filter.ResultSetEdgeFilter'

    def __str__(self) -> str:
        return java_handler(self._filter.toString, [])

    def get_result_set_id(self) -> str:
        """Get the result set id.

        :returns: The result set id.
        :rtype: str
        """
        return java_handler(self._filter.getResultSetId, [])

    def get_column_name(self) -> str:
        """Get the column name.

        :returns: The column name.
        :rtype: str
        """
        return java_handler(self._filter.getColumnName, [])


class VertexCollectionFilter(VertexFilter):
    """Represent a vertex filter used to create a vertex set out of a vertex collection."""

    _java_class = 'oracle.pgx.api.filter.internal.VertexCollectionFilter'

    def __str__(self) -> str:
        return java_handler(self._filter.toString, [])

    def get_collection_id(self) -> PgxId:
        """Get the collection id.

        :returns: The collection id.
        :rtype: PgxId
        """
        java_pgx_id = java_handler(self._filter.getCollectionId, [])
        return PgxId(java_pgx_id)


class EdgeCollectionFilter(EdgeFilter):
    """Class representing an edge filter used to create a edge set out of a edge collection."""

    _java_class = 'oracle.pgx.api.filter.internal.EdgeCollectionFilter'

    def __str__(self) -> str:
        return java_handler(self._filter.toString, [])

    def get_collection_id(self) -> PgxId:
        """Get the collection id.

        :returns: The collection id.
        :rtype: PgxId
        """
        java_pgx_id = java_handler(self._filter.getCollectionId, [])
        return PgxId(java_pgx_id)


class PathFindingFilter(GraphFilter):
    """Class representing a filter that is meant to be evaluated on all vertices/edges
    on a path between two nodes.
    """

    _java_class = 'oracle.pgx.api.filter.PathFindingFilter'

    def __init__(
        self, graph_filter: GraphFilter, source_vertex: PgxVertex, destination_vertex: PgxVertex
    ) -> None:
        java_filter = java_handler(
            filter_types['path_finding'],
            [graph_filter._filter, source_vertex._vertex, destination_vertex._vertex],
        )
        super().__init__(java_filter)
        self.graph_filter = graph_filter
        self.source_vertex = source_vertex
        self.destination_vertex = destination_vertex

    def __repr__(self) -> str:
        return "{}(graph_filter: {}, source_vertex: {}, destination_vertex: {})".format(
            self.__class__.__name__,
            self.graph_filter,
            self.source_vertex,
            self.destination_vertex,
        )

    def __str__(self) -> str:
        return repr(self)
