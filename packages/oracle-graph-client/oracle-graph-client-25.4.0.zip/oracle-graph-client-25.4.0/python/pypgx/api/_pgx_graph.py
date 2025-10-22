#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

import os
import sys
import warnings
from collections.abc import Iterable
from jnius import autoclass

from pypgx._utils import conversion
from pypgx.api._all_paths import AllPaths
from pypgx.api._graph_alteration_builder import GraphAlterationBuilder
from pypgx.api._graph_offloading import PreparedPgqlQuery, _apply_prepared_query_arguments
from pypgx.api._mutation_strategy import MutationStrategy
from pypgx.api._mutation_strategy_builder import MergingStrategyBuilder, PickingStrategyBuilder
from pypgx.api._pgql_result_set import PgqlResultSet
from pypgx.api._pgx_collection import (
    EdgeSequence,
    EdgeSet,
    VertexSequence,
    VertexSet,
    PgxCollection,
)
from pypgx.api._pgx_entity import PgxEdge, PgxVertex
from pypgx.api._pgx_map import PgxMap
from pypgx.api._property import EdgeProperty, VertexProperty, EdgeLabel, VertexLabels
from pypgx.api._scalar import Scalar
from pypgx.api._synchronizer import Synchronizer
from pypgx.api._operation import Operation
from pypgx.api._partition import PgxPartition
from pypgx.api._pgx_path import PgxPath
from pypgx.api._server_instance import ServerInstance
from pypgx.api._pgx_context_manager import PgxContextManager
from pypgx.api._pgx_id import PgxId
from pypgx.api._graph_config import GraphConfig
from pypgx.api._partitioned_graph_config import PartitionedGraphConfig
from pypgx.api._file_graph_config import FileGraphConfig
from pypgx.api._graph_meta_data import GraphMetaData
from pypgx.api.auth import PgxResourcePermission
from pypgx.api.filters import GraphFilter, EdgeFilter, VertexFilter, PathFindingFilter
from pypgx.api.redaction._redaction_rule_config import PgxRedactionRuleConfig
from pypgx._utils.error_handling import java_handler
from pypgx._utils.error_messages import (
    ARG_MUST_BE,
    INVALID_OPTION,
    UNSUPPORTED_QUERY_TYPE,
    INVALID_FORMAT_HOMOGENEOUS,
    INVALID_FORMAT_PARTITIONED,
    GRAPH_EXPAND_SOURCE_AMBIGUOUS,
)
from pypgx._utils.pgx_types import (
    authorization_types,
    collection_types,
    edge_props,
    format_types,
    provider_format_types,
    on_invalid_change_types,
    property_types,
    pgx_resource_permissions,
    vector_types,
    vertex_props,
)
from pypgx._utils.pgx_types import (
    degree_type,
    mode,
    multi_edges,
    self_edges,
    sort_order,
    trivial_vertices,
    id_generation_strategies,
    property_merge_strategies,
)
from pypgx.api.auth import PermissionEntity
from typing import Any, Dict, List, Optional, Tuple, Union, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    # Don't import at runtime, to avoid circular imports.
    from pypgx.api._pgx_session import PgxSession
    from pypgx.api._prepared_statement import PreparedStatement
    from pypgx.api._graph_change_set import GraphChangeSet


class PgxGraph(PgxContextManager):
    """A reference to a graph on the server side.

    Operations on instances of this class are executed on the server side onto the referenced
    graph. Note that a session can have multiple objects referencing the same graph: the result
    of any operation mutating the graph on any of those references will be visible on all of them.
    """

    _java_class = "oracle.pgx.api.PgxGraph"

    def __init__(self, session: "PgxSession", java_graph) -> None:
        self._graph = java_graph
        self.session = session

    @property
    def name(self) -> str:
        """Get the name of the graph."""
        return self._graph.getName()

    @property
    def is_transient(self) -> bool:
        """Whether the graph is transient."""
        return bool(self._graph.isTransient())

    @property
    def num_vertices(self) -> int:
        """Get the number of vertices in the graph."""
        return self._graph.getNumVertices()

    @property
    def num_edges(self) -> int:
        """Get the number of edges in the graph."""
        return self._graph.getNumEdges()

    @property
    def memory_mb(self) -> int:
        """Get the amount of memory in megabytes that the graph consumes."""
        return self._graph.getMemoryMb()

    @property
    def data_source_version(self) -> str:
        """Get the version of the data source that the graph is based on."""
        return self._graph.getDataSourceVersion()

    @property
    def is_directed(self) -> bool:
        """Whether the graph is directed."""
        return bool(self._graph.isDirected())

    @property
    def creation_request_timestamp(self) -> str:
        """Get the timestamp of the creation request."""
        return self._graph.getCreationRequestTimestamp()

    @property
    def creation_timestamp(self) -> str:
        """Get the timestamp of the creation."""
        return self._graph.getCreationTimestamp()

    @property
    def vertex_id_type(self) -> str:
        """Get the type of the vertex id."""
        return self._graph.getVertexIdType().toString()

    @property
    def vertex_id_strategy(self) -> str:
        """Get the strategy of the vertex id."""
        return self._graph.getVertexIdStrategy().toString()

    @property
    def edge_id_strategy(self) -> str:
        """Get the strategy of the edge id."""
        return self._graph.getEdgeIdStrategy().toString()

    @property
    def pgx_instance(self) -> ServerInstance:
        """Get the server instance."""
        return ServerInstance(self._graph.getPgxInstance())

    @property
    def config(self) -> Optional[GraphConfig]:
        """Get the GraphConfig object."""
        java_graph_config = self._graph.getConfig()
        if java_graph_config is None:
            return None
        return conversion.graph_config_to_python(java_graph_config)

    def get_meta_data(self) -> GraphMetaData:
        """Get the GraphMetaData object.

        :returns: A 'GraphMetaData' object of this graph.
        """
        return GraphMetaData(self._graph.getMetaData())

    def get_id(self) -> str:
        """Get the Graph id.

        :returns: A string representation of the id of this graph.
        """
        pgx_id = java_handler(self._graph.getId, [])
        return java_handler(pgx_id.toString, [])

    def get_pgx_id(self) -> PgxId:
        """Get the Graph id.

        :returns: The id of this graph.
        """
        pgx_id = java_handler(self._graph.getId, [])
        return PgxId(pgx_id)

    def get_vertex(self, vid: Union[str, int]) -> PgxVertex:
        """Get a vertex with a specified id.

        :param vid: Vertex id
        :returns: pgxVertex object
        """
        java_vid = conversion.vertex_id_to_java(vid, self.vertex_id_type)
        java_vertex = java_handler(self._graph.getVertex, [java_vid])
        return PgxVertex(self, java_vertex)

    def has_vertex(self, vid: Union[str, int]) -> bool:
        """Check if the vertex with id vid is in the graph.

        :param vid: vertex id
        """
        return bool(java_handler(self._graph.hasVertex, [vid]))

    def get_edge(self, eid: int) -> PgxEdge:
        """Get an edge with a specified id.

        :param eid: edge id
        """
        return PgxEdge(self, java_handler(self._graph.getEdge, [eid]))

    def has_edge(self, eid: int) -> bool:
        """Check if the edge with id eid is in the graph.

        :param eid: Edge id
        """
        return bool(java_handler(self._graph.hasEdge, [eid]))

    def get_random_vertex(self) -> PgxVertex:
        """Get a random vertex from the graph."""
        return PgxVertex(self, self._graph.getRandomVertex())

    def get_random_edge(self) -> PgxEdge:
        """Get a edge vertex from the graph."""
        return PgxEdge(self, self._graph.getRandomEdge())

    def has_vertex_labels(self) -> bool:
        """Return True if the graph has vertex labels, False if not."""
        return bool(self._graph.hasVertexLabels())

    def get_vertex_labels(self) -> VertexLabels:
        """Get the vertex labels belonging to this graph."""
        vl = java_handler(self._graph.getVertexLabels, [])
        return VertexLabels(self, vl)

    def has_edge_label(self) -> bool:
        """Return True if the graph has edge labels, False if not."""
        return bool(self._graph.hasEdgeLabel())

    def get_edge_label(self) -> EdgeLabel:
        """Get the edge labels belonging to this graph."""
        el = java_handler(self._graph.getEdgeLabel, [])
        return EdgeLabel(self, el)

    def get_vertex_properties(self) -> List[VertexProperty]:
        """Get the set of vertex properties belonging to this graph.

        This list might contain transient, private and published properties.
        """
        java_props = self._graph.getVertexProperties()
        props = []
        for prop in java_props:
            props.append(VertexProperty(self, prop))
        props.sort(key=lambda prop: prop.name)
        return props

    def get_edge_properties(self) -> List[EdgeProperty]:
        """Get the set of edge properties belonging to this graph.

        This list might contain transient, private and published properties.
        """
        java_props = self._graph.getEdgeProperties()
        props = []
        for prop in java_props:
            props.append(EdgeProperty(self, prop))
        props.sort(key=lambda prop: prop.name)
        return props

    def get_vertex_property(self, name: str) -> Optional[VertexProperty]:
        """Get a vertex property by name.

        :param name: Property name
        """
        prop = java_handler(self._graph.getVertexProperty, [name])
        if prop:
            return VertexProperty(self, prop)
        return None

    def get_edge_property(self, name: str) -> Optional[EdgeProperty]:
        """Get an edge property by name.

        :param name: Property name
        """
        prop = java_handler(self._graph.getEdgeProperty, [name])
        if prop:
            return EdgeProperty(self, prop)
        return None

    def create_scalar(self, data_type: str, name: Optional[str] = None) -> Scalar:
        """Create a new Scalar.

        :param data_type: Scalar type
        :param name:  Name of the scalar to be created
        """
        if data_type not in property_types:
            raise ValueError(
                INVALID_OPTION.format(var="data_type", opts=list(property_types.keys()))
            )
        scalar = java_handler(self._graph.createScalar, [property_types[data_type], name])
        return Scalar(self, scalar)

    def create_vector_scalar(
        self, data_type: str, dimension: int = 0, name: Optional[str] = None
    ) -> Scalar:
        """Create a new vector scalar.

        :param data_type: Property type
        :param dimension: the dimension of the vector scalar
        :param name:  Name of the scalar to be created
        """
        if data_type not in property_types:
            raise ValueError(
                INVALID_OPTION.format(var="data_type", opts=list(property_types.keys()))
            )
        scalar = java_handler(
            self._graph.createVectorScalar, [property_types[data_type], dimension, name]
        )
        return Scalar(self, scalar)

    def create_vertex_property(self, data_type: str, name: Optional[str] = None) -> VertexProperty:
        """Create a session-bound vertex property.

        :param data_type: Type of the vertex property to be created (one of 'integer', 'long',
            'float', 'double', 'boolean', 'string', 'vertex', 'edge', 'local_date', 'time',
            'timestamp', 'time_with_timezone', 'timestamp_with_timezone')
        :param name: Name of the vertex property to be created
        """
        if data_type not in property_types:
            raise ValueError(
                INVALID_OPTION.format(var="data_type", opts=list(property_types.keys()))
            )
        prop = java_handler(self._graph.createVertexProperty, [property_types[data_type], name])
        return VertexProperty(self, prop)

    def create_vertex_vector_property(
        self, data_type: str, dim: int, name: Optional[str] = None
    ) -> VertexProperty:
        """Create a session-bound vertex vector property.

        :param data_type: Type of the vector property to be created (one of 'integer', 'long',
            'float', 'double')
        :param dim: Dimension of the vector property to be created
        :param name: Name of the vector property to be created
        """
        if data_type not in vector_types:
            raise ValueError(INVALID_OPTION.format(var="data_type", opts=list(vector_types)))
        prop = java_handler(
            self._graph.createVertexVectorProperty, [property_types[data_type], dim, name]
        )
        return VertexProperty(self, prop)

    def get_or_create_vertex_vector_property(
        self, type: str, dimension: int, /, name: str
    ) -> VertexProperty:
        """Get a vertex vector property if it exists or create a new one otherwise.

        :param type: Type of the vector property to be created (one of 'integer', 'long', 'float',
            'double')
        :param dimension: Dimension of the vector property to be created
        :param name: Name of the vector property to be created

        .. versionchanged:: 23.4
            ``name`` is no longer optional. The keyword arguments ``data_type`` and ``dim`` are
            deprecated.
        """
        if not isinstance(type, str):
            raise TypeError(ARG_MUST_BE.format(arg="type", type="str"))
        if not isinstance(dimension, int):
            raise TypeError(ARG_MUST_BE.format(arg="dimension", type="int"))
        if not isinstance(name, str):
            raise TypeError(ARG_MUST_BE.format(arg="name", type="str"))
        if type not in vector_types:
            raise ValueError(INVALID_OPTION.format(var="type", opts=list(vector_types)))
        prop = java_handler(
            self._graph.getOrCreateVertexVectorProperty, [property_types[type], dimension, name]
        )
        return VertexProperty(self, prop)

    def create_edge_property(self, data_type: str, name: Optional[str] = None) -> EdgeProperty:
        """Create a session-bound edge property.

        :param data_type: Type of the edge property to be created (one of 'integer', 'long',
            'float', 'double', 'boolean', 'string', 'vertex', 'edge', 'local_date', 'time',
            'timestamp', 'time_with_timezone', 'timestamp_with_timezone')
        :param name: Name of the edge property to be created
        """
        if data_type not in property_types:
            raise ValueError(
                INVALID_OPTION.format(var="data_type", opts=list(property_types.keys()))
            )
        prop = java_handler(self._graph.createEdgeProperty, [property_types[data_type], name])
        return EdgeProperty(self, prop)

    def get_or_create_edge_vector_property(
        self, type: str, dimension: int, /, name: str
    ) -> EdgeProperty:
        """Get an edge vector property if it exists or create a new one otherwise.

        :param type: Type of the vector property to be created (one of 'integer', 'long', 'float',
            'double')
        :param dimension: Dimension of the vector property to be created
        :param name: Name of the vector property to be created

        .. versionchanged:: 23.4
            ``name`` is no longer optional. The keyword arguments ``data_type`` and ``dim`` are
            deprecated.
        """
        if not isinstance(type, str):
            raise TypeError(ARG_MUST_BE.format(arg="type", type="str"))
        if not isinstance(dimension, int):
            raise TypeError(ARG_MUST_BE.format(arg="dimension", type="int"))
        if not isinstance(name, str):
            raise TypeError(ARG_MUST_BE.format(arg="name", type="str"))
        if type not in vector_types:
            raise ValueError(INVALID_OPTION.format(var="type", opts=list(vector_types)))
        prop = java_handler(
            self._graph.getOrCreateEdgeVectorProperty, [property_types[type], dimension, name]
        )
        return EdgeProperty(self, prop)

    def create_edge_vector_property(
        self, data_type: str, dim: int, name: Optional[str] = None
    ) -> EdgeProperty:
        """Create a session-bound edge vector property.

        :param data_type: Type of the vector property to be created (one of 'integer', 'long',
            'float', 'double')
        :param dim: Dimension of the vector property to be created
        :param name: Name of the vector property to be created
        """
        if data_type not in vector_types:
            raise ValueError(INVALID_OPTION.format(var="data_type", opts=list(vector_types)))
        prop = java_handler(
            self._graph.createEdgeVectorProperty, [property_types[data_type], dim, name]
        )
        return EdgeProperty(self, prop)

    def get_or_create_vertex_property(self, type: str, /, name: str) -> VertexProperty:
        """Get a vertex property if it exists or create a new one otherwise.

        :param type: Type of the property to be created (one of 'integer', 'long', 'float',
            'double', 'boolean', 'string', 'vertex', 'edge', 'local_date', 'time', 'timestamp',
            'time_with_timezone', 'timestamp_with_timezone')
        :param name: Name of the property to be created

        :return: The vertex property

        .. versionchanged:: 23.4
            For consistency, ``type`` is now the first parameter of the method. It is no longer
            optional. The keyword arguments ``data_type`` and ``dim`` are deprecated.
        """
        if not isinstance(type, str):
            raise TypeError(ARG_MUST_BE.format(arg="type", type="str"))
        if not isinstance(name, str):
            raise TypeError(ARG_MUST_BE.format(arg="name", type="str"))
        if type not in property_types:
            raise ValueError(INVALID_OPTION.format(var="type", opts=list(property_types)))
        prop = java_handler(self._graph.getOrCreateVertexProperty, [property_types[type], name])
        return VertexProperty(self, prop)

    def get_or_create_edge_property(self, type: str, /, name: str) -> EdgeProperty:
        """Get an edge property if it exists or create a new one otherwise.

        :param type: Type of the property to be created (one of 'integer', 'long', 'float',
            'double', 'boolean', 'string', 'vertex', 'edge', 'local_date', 'time', 'timestamp',
            'time_with_timezone', 'timestamp_with_timezone')
        :param name: Name of the property to be created

        :return: The edge property

        .. versionchanged:: 23.4
            For consistency, ``type`` is now the first parameter of the method. It is no longer
            optional. The keyword arguments ``data_type`` and ``dim`` are deprecated.
        """
        if not isinstance(type, str):
            raise TypeError(ARG_MUST_BE.format(arg="type", type="str"))
        if not isinstance(name, str):
            raise TypeError(ARG_MUST_BE.format(arg="name", type="str"))
        if type not in property_types:
            raise ValueError(INVALID_OPTION.format(var="type", opts=list(property_types)))
        prop = java_handler(self._graph.getOrCreateEdgeProperty, [property_types[type], name])
        return EdgeProperty(self, prop)

    def pick_random_vertex(self) -> PgxVertex:
        """Select a random vertex from the graph.

        :return: The PgxVertex object
        """
        return self.get_random_vertex()

    def create_components(
        self, components: Union[VertexProperty, str], num_components: int
    ) -> PgxPartition:
        """Create a Partition object holding a collection of vertex sets, one for each component.

        :param components: Vertex property mapping each vertex to its component
            ID. Note that only component IDs in the range of
            [0..numComponents-1] are allowed. The returned future will complete
            exceptionally with an IllegalArgumentException if an invalid
            component ID is encountered. Gaps are supported: certain IDs not
            being associated with any vertices will yield to empty components.
        :param num_components: How many different components the components
            property contains
        :return: The Partition object
        """
        if not isinstance(components, VertexProperty):
            raise TypeError(ARG_MUST_BE.format(arg="components", type=VertexProperty.__name__))
        java_partition = java_handler(
            self._graph.createComponents, [components._prop, num_components]
        )
        java_vertex_property = java_handler(java_partition.getComponentsProperty, [])
        property = VertexProperty(self, java_vertex_property)

        return PgxPartition(self, java_partition, property)

    def store(
        self,
        format: str,
        path: str,
        num_partitions: Optional[int] = None,
        vertex_properties: bool = True,
        edge_properties: bool = True,
        overwrite: bool = False
    ) -> GraphConfig:
        """Store graph in a file.

        This method works for both partitioned and homogeneous graphs.
        Depending on whether the graph is partitioned or not, the ``format``
        parameter accepts different values.
        See the documentation for the ``format`` parameter below.

        .. versionchanged:: 22.3.1
            Added support for storing partitioned graphs.

        :param format: One of ['pgb', 'edge_list', 'two_tables', 'adj_list',
            'flat_file', 'graphml', 'csv'] for a homogeneous
            graph or one of ['pgb', 'csv'] for a partitioned graph
        :param path: Path to which graph will be stored
        :param num_partitions: The number of partitions that should be
            created, when exporting to multiple files
        :param vertex_properties: The collection of vertex properties to store
            together with the graph data. If not specified all the vertex
            properties are stored
        :param edge_properties: The collection of edge properties to store
            together with the graph data. If not specified all the vertex
            properties are stored
        :param overwrite: Overwrite if existing
        """
        is_partitioned = self.get_meta_data().is_partitioned()
        if is_partitioned:
            _format_types = provider_format_types
            error_template = INVALID_FORMAT_PARTITIONED
        else:
            _format_types = format_types
            error_template = INVALID_FORMAT_HOMOGENEOUS

        if format not in _format_types:
            raise ValueError(error_template.format(
                var="format", opts=list(_format_types.keys())))
        else:
            format = _format_types[format]

        vp, ep = self._create_hash_sets(vertex_properties, edge_properties)
        args = [format, path, vp, ep, overwrite]
        if num_partitions or isinstance(num_partitions, int):
            args.insert(2, num_partitions)

        config = java_handler(self._graph.store, args)
        if is_partitioned:
            return PartitionedGraphConfig(config)
        return FileGraphConfig(config)

    def close(self) -> None:
        """Destroy without waiting for completion."""
        return java_handler(self._graph.close, [])

    def destroy_vertex_property_if_exists(self, name: str) -> None:
        """Destroy a specific vertex property if it exists.

        :param name: Property name
        """
        return java_handler(self._graph.destroyVertexPropertyIfExists, [name])

    def destroy_edge_property_if_exists(self, name: str) -> None:
        """Destroy a specific edge property if it exists.

        :param name: Property name
        """
        return java_handler(self._graph.destroyEdgePropertyIfExists, [name])

    @property
    def is_fresh(self) -> bool:
        """Check whether an in-memory representation of a graph is fresh."""
        return bool(self._graph.isFresh())

    def get_vertices(
        self, filter_expr: Optional[Union[str, VertexFilter]] = None, name: Optional[str] = None
    ) -> VertexSet:
        """Create a new vertex set containing vertices according to the given filter expression.

        :param filter_expr:  VertexFilter object with the filter expression
             if None all the vertices are returned
        :param name:  The name of the collection to be created.
             If None, a name will be generated.
        """
        if filter_expr is None:
            filter_expr = VertexFilter("true")
        elif not isinstance(filter_expr, VertexFilter):
            raise TypeError(ARG_MUST_BE.format(arg="filter_expr", type=VertexFilter.__name__))
        return VertexSet(self, java_handler(self._graph.getVertices, [filter_expr._filter, name]))

    def get_edges(
        self, filter_expr: Optional[Union[str, EdgeFilter]] = None, name: Optional[str] = None
    ) -> EdgeSet:
        """Create a new edge set containing vertices according to the given filter expression.

        :param filter_expr:  EdgeFilter object with the filter expression.
             If None all the vertices are returned.
        :param name:  the name of the collection to be created.
             If None, a name will be generated.
        """
        if filter_expr is None:
            filter_expr = EdgeFilter("true")
        elif not isinstance(filter_expr, EdgeFilter):
            raise TypeError(ARG_MUST_BE.format(arg="filter_expr", type=EdgeFilter.__name__))
        return EdgeSet(self, java_handler(self._graph.getEdges, [filter_expr._filter, name]))

    def create_vertex_set(self, name: Optional[str] = None) -> VertexSet:
        """Create a new vertex set.

        :param name:  Set name
        """
        return VertexSet(self, java_handler(self._graph.createVertexSet, [name]))

    def create_vertex_sequence(self, name: Optional[str] = None) -> VertexSequence:
        """Create a new vertex sequence.

        :param name:  Sequence name
        """
        return VertexSequence(self, java_handler(self._graph.createVertexSequence, [name]))

    def create_edge_set(self, name: Optional[str] = None) -> EdgeSet:
        """Create a new edge set.

        :param name:  Edge set name
        """
        return EdgeSet(self, java_handler(self._graph.createEdgeSet, [name]))

    def create_edge_sequence(self, name: Optional[str] = None) -> EdgeSequence:
        """Create a new edge sequence.

        :param name:  Sequence name
        """
        return EdgeSequence(self, java_handler(self._graph.createEdgeSequence, [name]))

    def create_map(self, key_type: str, val_type: str, name: Optional[str] = None) -> PgxMap:
        """Create a session-bound map.

        Possible types are:
        ['integer','long','double','boolean','string','vertex','edge',
        'local_date','time','timestamp','time_with_timezone','timestamp_with_timezone']

        :param key_type:  Property type of the keys that are going to be stored inside the map
        :param val_type:  Property type of the values that are going to be stored inside the map
        :param name:  Map name
        """
        if key_type not in property_types:
            raise ValueError(
                INVALID_OPTION.format(var="key_type", opts=list(property_types.keys()))
            )
        elif val_type not in property_types:
            raise ValueError(
                INVALID_OPTION.format(var="val_type", opts=list(property_types.keys()))
            )
        k = property_types[key_type]
        v = property_types[val_type]
        return PgxMap(self, java_handler(self._graph.createMap, [k, v, name]))

    def sort_by_degree(
        self,
        vertex_properties: Union[List[VertexProperty], bool] = True,
        edge_properties: Union[List[EdgeProperty], bool] = True,
        ascending: bool = True,
        in_degree: bool = True,
        in_place: bool = False,
        name: Optional[str] = None,
    ) -> "PgxGraph":
        """Create a sorted version of a graph and all its properties.

        The returned graph is sorted such that the node numbering is ordered by
        the degree of the nodes. Note that the returned graph and properties
        are transient.

        :param vertex_properties: List of vertex properties belonging to graph
            specified to be kept in the new graph
        :param edge_properties: List of edge properties belonging to graph
            specified to be kept in the new graph
        :param ascending:  Sorting order
        :param in_degree:  If in_degree should be used for sorting. Otherwise use out degree.
        :param in_place:  If the sorting should be done in place or a new graph should be created
        :param name:  New graph name
        """
        warnings.warn(
            "sort_by_degree: this method has been deprecated since 25.1,"
            " sort_by_degree API is not supported for partitioned graphs",
            DeprecationWarning
        )
        vp, ep = self._create_hash_sets(vertex_properties, edge_properties)
        ascending = sort_order[ascending]
        in_degree = degree_type[in_degree]
        in_place = mode[in_place]
        new_graph = java_handler(
            self._graph.sortByDegree, [vp, ep, ascending, in_degree, in_place, name]
        )
        return PgxGraph(self.session, new_graph)

    def transpose(
        self,
        vertex_properties: bool = True,
        edge_properties: bool = True,
        edge_label_mapping: Optional[Mapping[str, str]] = None,
        in_place: bool = False,
        name: Optional[str] = None,
    ) -> "PgxGraph":
        """Create a transpose of this graph.

        A transpose of a directed graph is another directed graph on the same
        set of vertices with all of the edges reversed. If this graph contains
        an edge (u,v) then the return graph will contain an edge (v,u) and vice
        versa. If this graph is undirected (isDirected() returns false), this
        operation has no effect and will either return a copy or act as
        identity function depending on the mode parameter.

        :param vertex_properties:  List of vertex properties belonging to graph
            specified to be kept in the new graph
        :param edge_properties:  List of edge properties belonging to graph
            specified to be kept in the new graph
        :param edge_label_mapping:  Can be used to rename edge labels.
            For example, an edge (John,Mary) labeled "fatherOf" can be transformed
            to be labeled "hasFather" on the transpose graph's edge (Mary,John)
            by passing in a dict like object {"fatherOf":"hasFather"}.
        :param in_place:  If the transpose should be done in place or a new
            graph should be created
        :param name:  New graph name
        """
        warnings.warn(
            "transpose: this method has been deprecated since 25.1,"
            " transpose API is not supported for partitioned graphs",
            DeprecationWarning
        )
        if edge_label_mapping is None:
            edge_label_mapping = {}
        vp, ep = self._create_hash_sets(vertex_properties, edge_properties)
        edge_labels = None
        if len(edge_label_mapping) > 0:
            edge_labels = autoclass("java.util.HashMap")()
            for key in edge_label_mapping.keys():
                edge_labels.put(key, edge_label_mapping[key])
        in_place = mode[in_place]
        new_graph = java_handler(self._graph.transpose, [vp, ep, edge_labels, in_place, name])
        return PgxGraph(self.session, new_graph)

    def undirect(
        self,
        vertex_properties: Union[bool, List[VertexProperty]] = True,
        edge_properties: Union[bool, List[EdgeProperty]] = True,
        keep_multi_edges: bool = True,
        keep_self_edges: bool = True,
        keep_trivial_vertices: bool = True,
        in_place: bool = False,
        name: Optional[str] = None,
    ) -> "PgxGraph":
        """
        Create an undirected version of the graph.

        An undirected graph has some restrictions. Some algorithms are only supported on directed
        graphs or are not yet supported for undirected graphs. Further, PGX does not support
        storing undirected graphs nor reading from undirected formats. Since the edges do not have a
        direction anymore, the behavior of `pgxEdge.source()` or `pgxEdge.destination()` can be
        ambiguous. In order to provide deterministic results, PGX will always return the vertex
        with the smaller internal id as source and the other as destination vertex.

        :param vertex_properties: List of vertex properties belonging to
            graph specified to be kept in the new graph
        :param edge_properties: List of edge properties belonging to graph
            specified to be kept in the new graph
        :param keep_multi_edges: Defines if multi-edges should be kept in the
            result
        :param keep_self_edges: Defines if self-edges should be kept in the
            result
        :param keep_trivial_vertices: Defines if isolated nodes should be kept
            in the result
        :param in_place: If the operation should be done in place of if a new
            graph has to be created
        :param name: New graph name
        """
        warnings.warn(
            "undirect: this method has been deprecated since 25.1,"
            " undirect API is not supported for partitioned graphs",
            DeprecationWarning
        )
        if self.is_directed:
            vp, ep = self._create_hash_sets(vertex_properties, edge_properties)
            keep_multi_edges = multi_edges[keep_multi_edges]
            keep_self_edges = self_edges[keep_self_edges]
            keep_trivial_vertices = trivial_vertices[keep_trivial_vertices]
            in_place = mode[in_place]
            new_graph = java_handler(
                self._graph.undirect,
                [vp, ep, keep_multi_edges, keep_self_edges, keep_trivial_vertices, in_place, name],
            )
            return PgxGraph(self.session, new_graph)
        else:
            return self

    def undirect_with_strategy(self, mutation_strategy: MutationStrategy) -> "PgxGraph":
        """
        Create an undirected version of the graph using a custom mutation strategy.

        An undirected graph has some restrictions. Some algorithms are only supported on directed
        graphs or are not yet supported for undirected graphs. Further, PGX does not support
        storing undirected graphs nor reading from undirected formats. Since the edges do not have a
        direction anymore, the behavior of `pgxEdge.source()` or `pgxEdge.destination()` can be
        ambiguous. In order to provide deterministic results, PGX will always return the vertex
        with the smaller internal id as source and the other as destination vertex.

        :param mutation_strategy: Defines a custom strategy for dealing with multi-edges.
        """
        warnings.warn(
            "undirect: this method has been deprecated since 25.1,"
            " undirect API is not supported for partitioned graphs",
            DeprecationWarning
        )
        if self.is_directed:
            new_graph = java_handler(self._graph.undirect, [mutation_strategy._mutation_strategy])
            return PgxGraph(self.session, new_graph)
        else:
            return self

    def simplify(
        self,
        vertex_properties: Union[bool, List[VertexProperty]] = True,
        edge_properties: Union[bool, List[EdgeProperty]] = True,
        keep_multi_edges: bool = False,
        keep_self_edges: bool = False,
        keep_trivial_vertices: bool = False,
        in_place: bool = False,
        name: Optional[str] = None,
    ) -> "PgxGraph":
        """Create a simplified version of a graph.

        Note that the returned graph and properties are transient and therefore
        session bound. They can be explicitly destroyed and get automatically
        freed once the session dies.

        :param vertex_properties: List of vertex properties belonging to graph
            specified to be kept in the new graph
        :param edge_properties: List of edge properties belonging to graph
            specified to be kept in the new graph
        :param keep_multi_edges: Defines if multi-edges should be kept in the
            result
        :param keep_self_edges: Defines if self-edges should be kept in the
            result
        :param keep_trivial_vertices: Defines if isolated nodes should be kept
            in the result
        :param in_place: If the operation should be done in place of if a new
            graph has to be created
        :param name: New graph name. If None, a name will be generated.
            Only relevant if a new graph is to be created.
        """
        vp, ep = self._create_hash_sets(vertex_properties, edge_properties)
        keep_multi_edges = multi_edges[keep_multi_edges]
        keep_self_edges = self_edges[keep_self_edges]
        keep_trivial_vertices = trivial_vertices[keep_trivial_vertices]
        in_place = mode[in_place]
        new_graph = java_handler(
            self._graph.simplify,
            [vp, ep, keep_multi_edges, keep_self_edges, keep_trivial_vertices, in_place, name],
        )
        return PgxGraph(self.session, new_graph)

    def simplify_with_strategy(self, mutation_strategy: MutationStrategy) -> "PgxGraph":
        """Create a simplified version of a graph using a custom mutation strategy.

        Note that the returned graph and properties are transient and therefore
        session bound. They can be explicitly destroyed and get automatically
        freed once the session dies.

        :param mutation_strategy: Defines a custom strategy for dealing with multi-edges.
        """
        new_graph = java_handler(self._graph.simplify, [mutation_strategy._mutation_strategy])
        return PgxGraph(self.session, new_graph)

    def bipartite_sub_graph_from_left_set(
        self,
        vset: Union[str, VertexSet],
        vertex_properties: Union[List[VertexProperty], bool] = True,
        edge_properties: bool = True,
        name: Optional[str] = None,
        is_left_name: Optional[str] = None,
    ) -> "BipartiteGraph":
        """Create a bipartite version of this graph with the given vertex set being the left set.

        :param vset: Vertex set representing the left side
        :param vertex_properties:  List of vertex properties belonging to graph
            specified to be kept in the new graph
        :param edge_properties:  List of edge properties belonging to graph
            specified to be kept in the new graph
        :param name:  name of the new graph. If None, a name will be generated.
        :param is_left_name:   Name of the boolean isLeft vertex property of
            the new graph. If None, a name will be generated.
        """
        if not isinstance(vset, VertexSet):
            raise TypeError(ARG_MUST_BE.format(arg="vset", type=VertexSet.__name__))
        vp, ep = self._create_hash_sets(vertex_properties, edge_properties)
        b_graph = java_handler(
            self._graph.bipartiteSubGraphFromLeftSet, [vp, ep, vset._collection, name, is_left_name]
        )
        return BipartiteGraph(self.session, b_graph)

    def bipartite_sub_graph_from_in_degree(
        self,
        vertex_properties: Union[List[VertexProperty], bool] = True,
        edge_properties: bool = True,
        name: Optional[str] = None,
        is_left_name: Optional[str] = None,
        in_place: bool = False,
    ) -> "BipartiteGraph":
        """Create a bipartite version of this graph with all vertices of in-degree = 0 being the
        left set.

        :param vertex_properties:   List of vertex properties belonging to
            graph specified to be kept in the new graph
        :param edge_properties:  List of edge properties belonging to graph
            specified to be kept in the new graph
        :param name:  New graph name
        :param is_left_name:  Name of the boolean isLeft vertex property of
            the new graph. If None, a name will be generated.
        :param in_place: Whether to create a new copy (False) or overwrite this
            graph (True)
        """
        vp, ep = self._create_hash_sets(vertex_properties, edge_properties)
        b_graph = java_handler(
            self._graph.bipartiteSubGraphFromInDegree, [vp, ep, name, is_left_name, in_place]
        )
        return BipartiteGraph(self.session, b_graph)

    def is_bipartite(self, is_left: Union[VertexProperty, str]) -> int:
        """Check whether a given graph is a bipartite graph.

        A graph is considered a bipartite graph if all nodes can be divided in a 'left' and a
        'right' side where edges only go from nodes on the 'left' side to nodes on the 'right'
        side.

        :param is_left: Boolean vertex property that - if the method returns true -
            will contain for each node whether it is on the 'left' side of the
            bipartite graph. If the method returns False, the content is undefined.
        """
        if not isinstance(is_left, VertexProperty):
            raise TypeError(ARG_MUST_BE.format(arg="is_left", type=VertexProperty.__name__))
        return java_handler(self._graph.isBipartiteGraph, [is_left._prop])

    def sparsify(
        self,
        sparsification: float,
        vertex_properties: bool = True,
        edge_properties: bool = True,
        name: Optional[str] = None,
    ) -> "PgxGraph":
        """Sparsify the given graph and returns a new graph with less edges.

        :param sparsification:  The sparsification coefficient. Must be between
            0.0 and 1.0..
        :param vertex_properties:   List of vertex properties belonging to
            graph specified to be kept in the new graph
        :param edge_properties:  List of edge properties belonging to graph
            specified to be kept in the new graph
        :param name:  Filtered graph name
        """
        vp, ep = self._create_hash_sets(vertex_properties, edge_properties)
        new_graph = java_handler(self._graph.sparsify, [vp, ep, sparsification, name])
        return PgxGraph(self.session, new_graph)

    def filter(
        self,
        graph_filter: Union[VertexFilter, EdgeFilter, PathFindingFilter],
        vertex_properties: bool = True,
        edge_properties: bool = True,
        name: Optional[str] = None,
    ) -> "PgxGraph":
        """Create a subgraph of this graph.

        To create the subgraph, a given filter expression is used to determine
        which parts of the graph will be part of the subgraph.

        :param graph_filter:  Object representing a filter expression that is
            applied to create the subgraph
        :param vertex_properties:   List of vertex properties belonging to graph
            specified to be kept in the new graph
        :param edge_properties:  List of edge properties belonging to graph
            specified to be kept in the new graph
        :param name:  Filtered graph name
        """
        if not isinstance(graph_filter, GraphFilter):
            raise TypeError(ARG_MUST_BE.format(arg="graph_filter", type=GraphFilter.__name__))
        vp, ep = self._create_hash_sets(vertex_properties, edge_properties)
        new_graph = java_handler(self._graph.filter, [vp, ep, graph_filter._filter, name])
        return PgxGraph(self.session, new_graph)

    def clone(
        self,
        vertex_properties: bool = True,
        edge_properties: bool = True,
        name: Optional[str] = None,
    ) -> "PgxGraph":
        """Return a copy of this graph.

        :param vertex_properties: List of vertex properties belonging to graph
            specified to be cloned as well
        :param edge_properties:  List of edge properties belonging to graph
            specified to be cloned as well
        :param name:  Name of the new graph
        """
        vp, ep = self._create_hash_sets(vertex_properties, edge_properties)
        all_filter = VertexFilter("true")
        new_graph = java_handler(self._graph.filter, [vp, ep, all_filter._filter, name])
        return PgxGraph(self.session, new_graph)

    def create_path(
        self,
        src: PgxVertex,
        dst: PgxVertex,
        cost: EdgeProperty,
        parent: VertexProperty,
        parent_edge: VertexProperty,
    ) -> PgxPath:
        """
        :param src: Source vertex of the path
        :param dst: Destination vertex of the path
        :param cost: Property holding the edge costs. If null, the resulting
            cost will equal the hop distance.
        :param parent: Property holding the parent vertices for each vertex of
            the shortest path. For example, if the shortest path is A -> B -> C,
            then parent[C] -> B and parent[B] -> A.
        :param parent_edge: Property holding the parent edges for each vertex of
            the shortest path
        :return: The PgxPath object
        """
        if not isinstance(src, PgxVertex):
            raise TypeError(ARG_MUST_BE.format(arg="src", type=PgxVertex.__name__))
        if not isinstance(dst, PgxVertex):
            raise TypeError(ARG_MUST_BE.format(arg="dst", type=PgxVertex.__name__))
        if not isinstance(cost, EdgeProperty):
            raise TypeError(ARG_MUST_BE.format(arg="cost", type=EdgeProperty.__name__))
        if not isinstance(parent, VertexProperty):
            raise TypeError(ARG_MUST_BE.format(arg="parent", type=VertexProperty.__name__))
        if not isinstance(parent_edge, VertexProperty):
            raise TypeError(ARG_MUST_BE.format(arg="parent_edge", type=VertexProperty.__name__))

        java_pgx_path = java_handler(
            self._graph.createPath,
            [src._vertex, dst._vertex, cost._prop, parent._prop, parent_edge._prop],
        )
        return PgxPath(self, java_pgx_path)

    def create_all_paths(
        self,
        src: Union[str, PgxVertex],
        cost: Optional[Union[str, EdgeProperty]],
        dist: Union[VertexProperty, str],
        parent: Union[VertexProperty, str],
        parent_edge: Union[VertexProperty, str],
    ) -> AllPaths:
        """
        Create an `AllPaths` object representing all the shortest paths from a single source
        to all the possible destinations (shortest regarding the given edge costs).

        :param src: Source vertex of the path
        :param cost: Property holding the edge costs. If None, the resulting
            cost will equal the hop distance
        :param dist: Property holding the distance to the source vertex for each vertex in the
            graph
        :param parent: Property holding the parent vertices of all the shortest paths
            For example, if the shortest path is A -> B -> C, then parent[C] -> B and
            parent[B] -> A
        :param parent_edge: Property holding the parent edges for each vertex of the shortest path
        :return: The `AllPaths` object
        """
        if not isinstance(src, PgxVertex):
            raise TypeError(ARG_MUST_BE.format(arg="src", type=PgxVertex.__name__))
        if cost is not None and not isinstance(cost, EdgeProperty):
            raise TypeError(ARG_MUST_BE.format(arg="cost", type=EdgeProperty.__name__))
        if not isinstance(dist, VertexProperty):
            raise TypeError(ARG_MUST_BE.format(arg="dist", type=VertexProperty.__name__))
        if not isinstance(parent, VertexProperty):
            raise TypeError(ARG_MUST_BE.format(arg="parent", type=VertexProperty.__name__))
        if not isinstance(parent_edge, VertexProperty):
            raise TypeError(ARG_MUST_BE.format(arg="parent_edge", type=VertexProperty.__name__))

        java_all_paths = java_handler(
            self._graph.createAllPaths,
            [
                src._vertex,
                None if cost is None else cost._prop,
                dist._prop,
                parent._prop,
                parent_edge._prop,
            ],
        )
        return AllPaths(self._graph, java_all_paths)

    def query_pgql(self, query: str) -> PgqlResultSet:
        """Submit a pattern matching select only query.

        :param query:  Query string in PGQL
        :returns: PgqlResultSet with the result
        """
        query_res = java_handler(self._graph.queryPgql, [query])
        return PgqlResultSet(self, query_res)

    def rename(self, name: str) -> None:
        """Rename this graph.

        :param name: New name
        """
        java_handler(self._graph.rename, [name])

    def publish(
        self,
        vertex_properties: Union[List[VertexProperty], bool] = False,
        edge_properties: Union[List[EdgeProperty], bool] = False,
    ) -> None:
        """Publish the graph so it can be shared between sessions.

        This moves the graph name from the private into the public namespace.

        :param vertex_properties: List of vertex properties belonging to graph
            specified to be published as well
        :param edge_properties: List of edge properties belonging to graph
            specified by graph to be published as well
        """
        vp, ep = self._create_hash_sets(vertex_properties, edge_properties)
        java_handler(self._graph.publish, [vp, ep])

    @property
    def is_published(self) -> bool:
        """Check if this graph is published with snapshots."""
        return bool(self._graph.isPublished())

    def combine_vertex_properties_into_vector_property(
        self, properties: List[Union[VertexProperty, str]], name: Optional[str] = None
    ) -> VertexProperty:
        """Take a list of scalar vertex properties of same type and create a new vertex vector
        property by combining them.

        The dimension of the vector property will be equals to the number of properties.

        :param properties:  List of scalar vertex properties
        :param name:  Name for the vector property. If not null, vector property
            will be named. If that results in a name conflict, the returned future
            will complete exceptionally.
        """
        props = autoclass("java.util.ArrayList")()
        for prop in properties:
            if not isinstance(prop, VertexProperty):
                raise TypeError(
                    ARG_MUST_BE.format(arg="props", type="list of " + VertexProperty.__name__)
                )
            props.add(prop._prop)
        vprop = java_handler(self._graph.combineVertexPropertiesIntoVectorProperty, [props, name])
        return VertexProperty(self, vprop)

    def combine_edge_properties_into_vector_property(
        self, properties: List[Union[EdgeProperty, str]], name: Optional[str] = None
    ) -> EdgeProperty:
        """Take a list of scalar edge properties of same type and create a new edge vector
        property by combining them.

        The dimension of the vector property will be equals to the number of properties.

        :param properties: List of scalar edge properties
        :param name:  Name for the vector property. If not null, vector
            property will be named. If that results in a name conflict,
            the returned future will complete exceptionally.
        """
        props = autoclass("java.util.ArrayList")()
        for prop in properties:
            if not isinstance(prop, EdgeProperty):
                raise TypeError(
                    ARG_MUST_BE.format(arg="props", type="list of " + EdgeProperty.__name__)
                )
            props.add(prop._prop)
        vprop = java_handler(self._graph.combineEdgePropertiesIntoVectorProperty, [props, name])
        return EdgeProperty(self, vprop)

    def get_collections(self) -> Dict[str, PgxCollection]:
        """Retrieve all currently allocated collections associated with the graph."""
        java_collections = java_handler(self._graph.getCollections, [])
        collections: Dict[str, PgxCollection] = {}
        for c in java_collections:
            item = java_collections[c]
            if isinstance(item, collection_types["vertex_sequence"]):
                collections[c] = VertexSequence(self, item)
            elif isinstance(item, collection_types["vertex_set"]):
                collections[c] = VertexSet(self, item)
            elif isinstance(item, collection_types["edge_sequence"]):
                collections[c] = EdgeSequence(self, item)
            elif isinstance(item, collection_types["edge_set"]):
                collections[c] = EdgeSet(self, item)
        return collections

    def _create_hash_sets(
        self,
        vertex_properties: Union[List[VertexProperty], bool],
        edge_properties: Union[List[EdgeProperty], bool],
    ) -> Tuple[Any, Any]:
        """
        :param vertex_properties: List of vertex properties belonging to graph
            specified to be published as well
        :param edge_properties: List of edge properties belonging to graph
            specified by graph to be published as well
        """
        vertex_properties_hash_set = autoclass("java.util.HashSet")()
        error_message = ARG_MUST_BE.format(
            arg="vertex_properties", type=f"iterable of {VertexProperty.__name__}"
        )
        if isinstance(vertex_properties, bool):
            vertex_properties_hash_set = vertex_props[vertex_properties]
        elif isinstance(vertex_properties, Iterable):
            for vertex_property in vertex_properties:
                if not isinstance(vertex_property, VertexProperty):
                    raise TypeError(error_message)
                vertex_properties_hash_set.add(vertex_property._prop)
        else:
            raise TypeError(error_message)

        edge_properties_hash_set = autoclass("java.util.HashSet")()
        error_message = ARG_MUST_BE.format(
            arg="edge_properties", type=f"iterable of {EdgeProperty.__name__}"
        )
        if isinstance(edge_properties, bool):
            edge_properties_hash_set = edge_props[edge_properties]
        elif isinstance(edge_properties, Iterable):
            for edge_prop in edge_properties:
                if not isinstance(edge_prop, EdgeProperty):
                    raise TypeError(error_message)
                edge_properties_hash_set.add(edge_prop._prop)
        else:
            raise TypeError(error_message)
        return (vertex_properties_hash_set, edge_properties_hash_set)

    def create_change_set(
        self,
        vertex_id_generation_strategy: str = "user_ids",
        edge_id_generation_strategy: str = "auto_generated",
    ) -> "GraphChangeSet":
        """Create a change set for updating the graph.

        Uses auto generated IDs for the edges.

        .. note:: This is currently not supported for undirected graphs.

        :return: an empty change set
        :rtype: GraphChangeSet
        """

        # NOTE: The import of GraphChangeSet needs to be deferred as otherwise a
        # circular import is generated when executing 'import pypgx'. This
        # would be the import dependency circle:
        # 'PgxGraph' -> 'GraphChangeSet' -> 'GraphBuilder' -> 'PgxGraph'
        from pypgx.api._graph_change_set import GraphChangeSet

        java_v_strategy = id_generation_strategies[vertex_id_generation_strategy]
        java_e_strategy = id_generation_strategies[edge_id_generation_strategy]
        java_change_set = java_handler(
            self._graph.createChangeSet, [java_v_strategy, java_e_strategy]
        )

        return GraphChangeSet(self.session, java_change_set, self.vertex_id_type)

    def prepare_pgql(self, pgql_query: str) -> "PreparedStatement":
        """Prepare a PGQL query.

        :param pgql_query: Query string in PGQL
        :return: A prepared statement object
        """
        from pypgx.api._prepared_statement import PreparedStatement

        java_prepared_statement = java_handler(self._graph.preparePgql, [pgql_query])
        return PreparedStatement(java_prepared_statement, self.session)

    def execute_pgql(self, pgql_query: str) -> Optional[PgqlResultSet]:
        """Execute a PGQL query.

        :param pgql_query: Query string in PGQL
        :return: The query result set as PgqlResultSet object
        """
        java_pgql_result_set = java_handler(self._graph.executePgql, [pgql_query])
        graph = PgxGraph(self.session, self._graph)

        if java_pgql_result_set is None:
            return None
        return PgqlResultSet(graph, java_pgql_result_set)

    def explain_pgql(self, pgql_query: str) -> Operation:
        """Explain the execution plan of a pattern matching query.

        Note: Different PGX versions may return different execution plans.

        :param pgql_query: Query string in PGQL
        :return: The query plan
        """
        java_operation = java_handler(self._graph.explainPgql, [pgql_query])
        return Operation(java_operation)

    def clone_and_execute_pgql(
        self,
        pgql_query: str,
        new_graph_name: Optional[str] = None
    ) -> "PgxGraph":
        """Create a deep copy of the graph, and execute on it the pgql query.

        :param pgql_query: Query string in PGQL
        :param new_graph_name: Name given to the newly created PgxGraph
        :return: A cloned PgxGraph with the pgql query executed

        throws InterruptedException if the caller thread gets interrupted while waiting for
            completion.
        throws ExecutionException   if any exception occurred during asynchronous execution.
            The actual exception will be nested.
        """
        java_graph = java_handler(self._graph.cloneAndExecutePgql, [pgql_query, new_graph_name])
        return PgxGraph(self.session, java_graph)

    def expand_with_pgql(
        self,
        pgql_queries: Union[str, PreparedPgqlQuery, List[Union[str, PreparedPgqlQuery]]],
        new_graph_name: Optional[str] = None,
        pg_view_name: Optional[str] = None,
        as_snapshot: bool = False,
        config: Optional[GraphConfig] = None,
        *,
        num_connections: Optional[int] = None,
        data_source_id: Optional[str] = None,
        jdbc_url: Optional[str] = None,
        keystore_alias: Optional[str] = None,
        owner: Optional[str] = None,
        password: Optional[str] = None,
        schema: Optional[str] = None,
        username: Optional[str] = None,
        edge_properties_merging_strategy: Optional[str] = None,
        vertex_properties_merging_strategy: Optional[str] = None,
        pg_sql_name: Optional[str] = None,
    ) -> "PgxGraph":
        """
        Expand this graph with data matching one or more PGQL queries.
        Given a list of either queries or prepared queries (with arguments), this will load
        all data matching at least on of the queries and merge it with the data from this graph.
        By default, this will expand from the same graph source as the original graph. To load data
        from another graph, specify either the pg_view_name or the pg_sql_name parameter.

        :param pgql_queries: One or more PGQL queries (or prepared queries).
        :param new_graph_name: An optional name for the new graph.
        :param pg_view_name: The PG View name from which to load the data.
        :param scn: The SCN as of which the data should be loaded (optional).
        :param as_snapshot: Expand as a new snapshot, instead of new graph.
        :param config: An optional config used to describe how to load the additional graph data.
        :param num_connections: The number of connections to open to load the data in parallel.
        :param data_source_id: The dataSourceId to which to connect.
        :param jdbc_url: The jdbcUrl to use for connection to the DB.
        :param keystore_alias: The key store alias to retrieve the password from the keystore.
        :param owner: The owner (schema) of the PG view from which to load the data.
        :param password: The password to use for connecting to the database.
        :param schema: The schema from which to load the PG view.
        :param username: The username of the DB user to use to connect to the DB.
        :param edge_properties_merging_strategy: The strategy to specify how edge properties
            of duplicates element are handled. Allowed values: 'keep_current_values',
            'update_with_new_values'.
        :param vertex_properties_merging_strategy: The strategy to specify how vertex properties
            of duplicate element are handled. Allowed values: 'keep_current_values',
            'update_with_new_values'.
        :param pg_sql_name: The name of the SQL property graph from which to load data.
        :return: The graph containing data both from this graph and the external source.
        """
        generic_expander = java_handler(self._graph.expandGraph, [])
        expander = java_handler(generic_expander.withPgql, [])
        # In case the expansion is from a different PG view/SQL graph
        if pg_view_name is not None:
            if pg_sql_name is not None:
                raise ValueError(GRAPH_EXPAND_SOURCE_AMBIGUOUS)
            java_handler(expander.fromPgPgql, [pg_view_name])
        if pg_sql_name is not None:
            java_handler(expander.fromPgSql, [pg_sql_name])
        # The DB parameters and config
        if config is not None:
            java_handler(expander.withConfig, [config._graph_config])
        if num_connections is not None:
            java_handler(expander.connections, [num_connections])
        if data_source_id is not None:
            java_handler(expander.dataSourceId, [data_source_id])
        if jdbc_url is not None:
            java_handler(expander.jdbcUrl, [jdbc_url])
        if keystore_alias is not None:
            java_handler(expander.keystoreAlias, [keystore_alias])
        if owner is not None:
            java_handler(expander.owner, [owner])
        if password is not None:
            java_handler(expander.password, [password])
        if schema is not None:
            java_handler(expander.schema, [schema])
        if username is not None:
            java_handler(expander.username, [username])
        # Merging strategies
        if edge_properties_merging_strategy is not None:
            if edge_properties_merging_strategy not in list(property_merge_strategies.keys()):
                raise ValueError(
                    INVALID_OPTION.format(
                        var="edge_properties_merging_strategy",
                        opts=", ".join(list(property_merge_strategies.keys())),
                    )
                )
            java_handler(
                expander.edgePropertiesMergingStrategy,
                [property_merge_strategies[edge_properties_merging_strategy]],
            )
        if vertex_properties_merging_strategy is not None:
            if vertex_properties_merging_strategy not in list(property_merge_strategies.keys()):
                raise ValueError(
                    INVALID_OPTION.format(
                        var="vertex_properties_merging_strategy",
                        opts=", ".join(list(property_merge_strategies.keys())),
                    )
                )
            java_handler(
                expander.vertexPropertiesMergingStrategy,
                [property_merge_strategies[vertex_properties_merging_strategy]],
            )
        # The queries
        if isinstance(pgql_queries, str):
            java_handler(expander.queryPgql, [pgql_queries])
        elif isinstance(pgql_queries, PreparedPgqlQuery):
            prepared_pgql_query = java_handler(expander.preparedPgqlQuery, [pgql_queries.query])
            _apply_prepared_query_arguments(prepared_pgql_query, pgql_queries.arguments)
        elif isinstance(pgql_queries, list):
            for query in pgql_queries:
                if isinstance(query, str):
                    java_handler(expander.queryPgql, [query])
                elif isinstance(query, PreparedPgqlQuery):
                    prepared_pgql_query = java_handler(expander.preparedPgqlQuery, [query.query])
                    _apply_prepared_query_arguments(prepared_pgql_query, query.arguments)
                else:
                    raise TypeError(UNSUPPORTED_QUERY_TYPE)
        else:
            raise TypeError(UNSUPPORTED_QUERY_TYPE)

        if not as_snapshot:
            java_graph = java_handler(expander.expand, [new_graph_name])
        elif new_graph_name is not None:
            raise ValueError(
                "'new_graph_name' should not be provided together with as_snapshot=True"
            )
        else:
            java_graph = java_handler(expander.expandNewSnapshot, [])
        return PgxGraph(self.session, java_graph)

    def publish_with_snapshots(
        self,
        vertex_properties: Union[List[VertexProperty], bool] = False,
        edge_properties: Union[List[EdgeProperty], bool] = False,
    ) -> None:
        """Publish the graph and all its snapshots so they can be shared between sessions

        This moves the graph name from the private into the public namespace.

        :param vertex_properties: List of vertex properties belonging to graph
            specified to be published as well
        :param edge_properties: List of edge properties belonging to graph
            specified by graph to be published as well
        """
        vp, ep = self._create_hash_sets(vertex_properties, edge_properties)
        java_handler(self._graph.publishWithSnapshots, [vp, ep])

    def is_published_with_snapshots(self) -> bool:
        """Check if this graph is published with snapshots.

        :return: True if this graph is published, false otherwise
        """
        return bool(java_handler(self._graph.isPublishedWithSnapshots, []))

    def destroy(self) -> None:
        """Destroy the graph with all its properties.

        After this operation, neither the graph nor its properties can be used
        anymore within this session.

        .. note:: if you have multiple :class:`PgxGraph` objects referencing the same graph
            (e.g. because you called :meth:`PgxSession.get_graph` multiple times with the
            same argument), they will ALL become invalid after calling this method;
            therefore, subsequent operations on ANY of them will result in an exception.
        """
        java_handler(self._graph.destroy, [])

    def is_pinned(self) -> bool:
        """For a published graph, indicates if the graph is pinned. A pinned graph will stay
        published even if no session is using it.
        """
        return bool(java_handler(self._graph.isPinned, []))

    def pin(self) -> None:
        """For a published graph, pin the graph so that it stays published even if no sessions uses
        it. This call pins the graph lineage, which ensures that at least the latest available
        snapshot stays published when no session uses the graph.
        """
        java_handler(self._graph.pin, [])

    def unpin(self) -> None:
        """For a published graph, unpin the graph so that if no snapshot of the graph is used by
        any session or pinned, the graph and all its snapshots can be removed.
        """
        java_handler(self._graph.unpin, [])

    def create_picking_strategy_builder(self) -> PickingStrategyBuilder:
        """Create a new `PickingStrategyBuilder` that can be used to build a new `PickingStrategy`
        to simplify this graph.
        """
        return PickingStrategyBuilder(java_handler(self._graph.createPickingStrategyBuilder, []))

    def create_merging_strategy_builder(self) -> MergingStrategyBuilder:
        """Create a new `MergingStrategyBuilder` that can be used to build a new `MutationStrategy`
        to simplify this graph.
        """
        return MergingStrategyBuilder(java_handler(self._graph.createMergingStrategyBuilder, []))

    def create_synchronizer(
        self,
        *,
        synchronizer_class: str = "oracle.pgx.api.FlashbackSynchronizer",
        invalid_change_policy: Optional[str] = None,
        graph_config: Optional[GraphConfig] = None,
        jdbc_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        parallel_hint_degree: Optional[int] = None
    ) -> Synchronizer:
        """Create a synchronizer object which can be used to keep this graph in sync with changes
        happening in its original data source. Only partitioned graphs with all providers loaded
        from Oracle Database are supported.

        :param synchronizer_class: string representing java class including package, currently
            'oracle.pgx.api.FlashbackSynchronizer' is the only existent option
        :param invalid_change_policy: sets the ``OnInvalidChange`` parameter to the Synchronizer
            ``ChangeSet``. Possible values are: 'ignore', 'ignore_and_log', 'ignore_and_log_once',
            'error'.
        :param graph_config: the graph configuration to use for synchronization
        :param jdbc_url: jdbc url of database
        :param username: username in database
        :param password: password of username in database
        :param parallel_hint_degree: parallel hint degree to be used in synchronizer queries
        :return: a synchronizer

        .. versionchanged:: 23.4
            The parameter ``connection`` has been removed. Use ``jdbc_url``, ``username``, and
            ``password`` instead.
        """

        synchronizer_builder = autoclass("oracle.pgx.api.Synchronizer$Builder")()
        java_handler(synchronizer_builder.setGraph, [self._graph])
        java_handler(synchronizer_builder.setType, [autoclass(synchronizer_class)])

        if jdbc_url is None and invalid_change_policy is not None:
            raise ValueError("an invalid_change_policy can only be used if the jdbc_url is set")

        if jdbc_url is not None or username is not None or password is not None:
            connection_handler = autoclass("oracle.pgx.api.SynchronizerConnectionHandler")
            connection = java_handler(
                connection_handler.createConnection, [jdbc_url, username, password]
            )
            java_handler(synchronizer_builder.setConnection, [connection])

        if graph_config is not None:
            java_handler(synchronizer_builder.setGraphConfiguration, [graph_config._graph_config])
        if invalid_change_policy is not None:
            if invalid_change_policy not in on_invalid_change_types:
                raise ValueError(
                    INVALID_OPTION.format(
                        var="invalid_change_policy", opts=list(on_invalid_change_types.keys())
                    )
                )
            on_invalid_change_type = on_invalid_change_types[invalid_change_policy]
            java_handler(synchronizer_builder.setInvalidChangePolicy, [on_invalid_change_type])
        if parallel_hint_degree is not None:
            java_handler(synchronizer_builder.setParallelHintDegree, [parallel_hint_degree])
        return Synchronizer(java_handler(synchronizer_builder.build, []), self.session)

    def alter_graph(self) -> GraphAlterationBuilder:
        """Create a graph alteration builder to define the graph schema alterations to perform on
        the graph.

        :return: an empty graph alteration builder
        """
        return GraphAlterationBuilder(java_handler(self._graph.alterGraph, []), self.session)

    def get_redaction_rules(
        self, authorization_type: str, name: str
    ) -> List[PgxRedactionRuleConfig]:
        """Get the redaction rules for an `authorization_type` name.

        Possible authorization types are: ['user', 'role']

        :param authorization_type: the authorization type of the rules to be returned
        :param name: the name of the user or role for which the rules should be returned
        :return: a list of redaction rules for the given name of type `authorization_type`
        """
        if authorization_type not in authorization_types:
            raise ValueError(
                INVALID_OPTION.format(
                    var="authorization_type", opts=list(authorization_types.keys())
                )
            )
        t = authorization_types[authorization_type]
        java_redaction_rules = java_handler(self._graph.getRedactionRules, [t, name])
        redaction_rules = []
        for rule in java_redaction_rules:
            redaction_rules.append(PgxRedactionRuleConfig(rule))
        return redaction_rules

    def add_redaction_rule(
        self, redaction_rule_config: PgxRedactionRuleConfig, authorization_type: str, *names: str
    ) -> None:
        """Add a redaction rule for `authorization_type` names.

        Possible authorization types are: ['user', 'role']

        :param authorization_type: the authorization type of the rule to be added
        :param names: the names of the users or roles for which the rule should be added
        """
        if authorization_type not in authorization_types:
            raise ValueError(
                INVALID_OPTION.format(
                    var="authorization_type", opts=list(authorization_types.keys())
                )
            )
        t = authorization_types[authorization_type]
        java_handler(
            self._graph.addRedactionRule, [redaction_rule_config._redaction_rule_config, t, *names]
        )

    def remove_redaction_rule(
        self, redaction_rule_config: PgxRedactionRuleConfig, authorization_type: str, *names: str
    ) -> None:
        """Remove a redaction rule for `authorization_type` names.

        Possible authorization types are: ['user', 'role']

        :param authorization_type: the authorization type of the rule to be removed
        :param names: the names of the users or roles for which the rule should be removed
        """
        if authorization_type not in authorization_types:
            raise ValueError(
                INVALID_OPTION.format(
                    var="authorization_type", opts=list(authorization_types.keys())
                )
            )
        t = authorization_types[authorization_type]
        java_handler(
            self._graph.removeRedactionRule,
            [redaction_rule_config._redaction_rule_config, t, *names],
        )

    def grant_permission(
        self, permission_entity: PermissionEntity, pgx_resource_permission: str
    ) -> None:
        """Grant a permission on this graph to the given entity.

        Possible `PGXResourcePermission` types are: ['none', 'read', 'write', 'export', 'manage']
        Possible `PermissionEntity` objects are: `PgxUser` and `PgxRole`.

        Cannont grant 'manage'.

        :param permission_entity: the entity the rule is granted to
        :param pgx_resource_permission: the permission type
        """
        java_permission_entity = permission_entity._permission_entity
        if pgx_resource_permission not in pgx_resource_permissions:
            raise ValueError(
                INVALID_OPTION.format(
                    var="pgx_resource_permission", opts=list(pgx_resource_permissions.keys())
                )
            )
        t = pgx_resource_permissions[pgx_resource_permission]
        java_handler(self._graph.grantPermission, [java_permission_entity, t])

    def revoke_permission(self, permission_entity: PermissionEntity) -> None:
        """Revoke all permissions on this graph from the given entity.

        Possible `PermissionEntity` objects are: `PgxUser` and `PgxRole`.

        :param permission_entity: the entity for which all permissions will be revoked
        """
        java_permission_entity = permission_entity._permission_entity
        java_handler(self._graph.revokePermission, [java_permission_entity])

    def get_permission(self) -> PgxResourcePermission:
        """Return permission object for the graph."""
        java_resource_permission = java_handler(self._graph.getPermission, [])
        resource_permission = PgxResourcePermission(java_resource_permission)
        return resource_permission

    def __repr__(self) -> str:
        return "{}(name: {}, v: {}, e: {}, directed: {}, memory(Mb): {})".format(
            self.__class__.__name__,
            self.name,
            self.num_vertices,
            self.num_edges,
            self.is_directed,
            self.memory_mb,
        )

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return bool(self._graph.equals(other._graph))

    # Methods to manage deprecated calls from user code. These method definitions override the
    # definitions above, except when we build the documentation. (We do not want to show these
    # convoluted signatures in the sphinx docs.) This whole if-block can be removed in PyPGX 24.4
    # after a deprecation period.
    if (not TYPE_CHECKING) and os.path.basename(sys.argv[0]) != "sphinx-build":
        _new_get_or_create_vertex_vector_property = get_or_create_vertex_vector_property
        _new_get_or_create_edge_vector_property = get_or_create_edge_vector_property
        _new_get_or_create_vertex_property = get_or_create_vertex_property
        _new_get_or_create_edge_property = get_or_create_edge_property

        # These methods take Ellipsis rather than None to reduce any confusion when users
        # explicitly pass None. Users are not expected to ever explicitly pass Ellipsis.

        def get_or_create_vertex_vector_property(
            self,
            type: str = Ellipsis,
            dimension: int = Ellipsis,
            /,
            name: str = Ellipsis,
            *,
            data_type: str = Ellipsis,
            dim: int = Ellipsis,
        ) -> VertexProperty:
            """Get a vertex vector property if it exists or create a new one otherwise."""

            example_call = (
                ' - example of correct usage: '
                'graph.get_or_create_vertex_vector_property("long", 5, "property_name")'
            )

            # Raise errors for calls that are illegal with old signature and with new signature.
            too_many_arguments = (
                (type is not Ellipsis and data_type is not Ellipsis)
                or (dimension is not Ellipsis and dim is not Ellipsis)
            )
            if too_many_arguments:
                raise TypeError(
                    "get_or_create_vertex_vector_property() received too many arguments"
                    + example_call
                )
            if type is Ellipsis and data_type is Ellipsis:
                raise TypeError(
                    "get_or_create_vertex_vector_property() missing required argument 'type'"
                    + example_call
                )
            if dimension is Ellipsis and dim is Ellipsis:
                raise TypeError(
                    "get_or_create_vertex_vector_property() missing required argument 'dimension'"
                    + example_call
                )

            if type is Ellipsis:
                assert data_type is not Ellipsis
                warnings.warn(
                    "get_or_create_vertex_vector_property: the 'data_type' parameter is deprecated "
                    "since 23.4"
                    + example_call,
                    DeprecationWarning
                )
                type = data_type

            if dimension is Ellipsis:
                assert dim is not Ellipsis
                warnings.warn(
                    "get_or_create_vertex_vector_property: the 'dim' parameter is deprecated "
                    "since 23.4"
                    + example_call,
                    DeprecationWarning
                )
                dimension = dim

            if name is Ellipsis or name is None:
                warnings.warn(
                    "get_or_create_vertex_vector_property: not specifying a name is deprecated "
                    "since 23.4, use create_vertex_vector_property instead",
                    DeprecationWarning
                )
                return self.create_vertex_vector_property(type, dimension)

            return self._new_get_or_create_vertex_vector_property(type, dimension, name)

        def get_or_create_edge_vector_property(
            self,
            type: str = Ellipsis,
            dimension: int = Ellipsis,
            /,
            name: str = Ellipsis,
            *,
            data_type: str = Ellipsis,
            dim: int = Ellipsis,
        ) -> EdgeProperty:
            """Get an edge vector property if it exists or create a new one otherwise."""

            example_call = (
                ' - example of correct usage: '
                'graph.get_or_create_edge_vector_property("long", 5, "property_name")'
            )

            # Raise errors for calls that are illegal with old signature and with new signature.
            too_many_arguments = (
                (type is not Ellipsis and data_type is not Ellipsis)
                or (dimension is not Ellipsis and dim is not Ellipsis)
            )
            if too_many_arguments:
                raise TypeError(
                    "get_or_create_edge_vector_property() received too many arguments"
                    + example_call
                )
            if type is Ellipsis and data_type is Ellipsis:
                raise TypeError(
                    "get_or_create_edge_vector_property() missing required argument 'type'"
                    + example_call
                )
            if dimension is Ellipsis and dim is Ellipsis:
                raise TypeError(
                    "get_or_create_edge_vector_property() missing required argument 'dimension'"
                    + example_call
                )

            if type is Ellipsis:
                assert data_type is not Ellipsis
                warnings.warn(
                    "get_or_create_edge_vector_property: the 'data_type' parameter is deprecated "
                    "since 23.4"
                    + example_call,
                    DeprecationWarning
                )
                type = data_type

            if dimension is Ellipsis:
                assert dim is not Ellipsis
                warnings.warn(
                    "get_or_create_edge_vector_property: the 'dim' parameter is deprecated "
                    "since 23.4"
                    + example_call,
                    DeprecationWarning
                )
                dimension = dim

            if name is Ellipsis or name is None:
                warnings.warn(
                    "get_or_create_edge_vector_property: not specifying a name is deprecated "
                    "since 23.4, use create_edge_vector_property instead",
                    DeprecationWarning
                )
                return self.create_edge_vector_property(type, dimension)

            return self._new_get_or_create_edge_vector_property(type, dimension, name)

        def get_or_create_vertex_property(
            self,
            type: str = Ellipsis,
            /,
            name: str = Ellipsis,
            dim: int = Ellipsis,
            *,
            data_type: str = Ellipsis,
        ) -> VertexProperty:
            """Get a vertex property if it exists or create a new one otherwise."""

            example_call = (
                ' - example of correct usage: '
                'graph.get_or_create_vertex_property("long", "property_name")'
            )

            # Raise errors for calls that are illegal with old signature and with new signature.
            if type is not Ellipsis and name is not Ellipsis and data_type is not Ellipsis:
                raise TypeError(
                    "get_or_create_vertex_property() received too many arguments" + example_call
                )
            if type is Ellipsis and name is Ellipsis:
                raise TypeError(
                    "get_or_create_vertex_property() missing required argument 'type'"
                    + example_call
                )

            using_old_signature = (
                type is Ellipsis
                or name is Ellipsis
                or (name in list(property_types) and type not in list(property_types))
                or dim is not Ellipsis
            )
            if using_old_signature:
                # The old signature had arguments in different order. We need to switch them around.
                # Since arguments could have been passed by keyword or positionally, there are lots
                # of combinations to cover.
                if type is not Ellipsis and name is not Ellipsis:
                    type, name = name, type
                elif type is not Ellipsis and data_type is not Ellipsis:
                    type, name = data_type, type
                elif name is not Ellipsis and data_type is not Ellipsis:
                    type, name = data_type, name
                elif type is not Ellipsis:
                    type, name = None, type
                else:
                    assert name is not Ellipsis
                    type, name = None, name

            if type is None:
                warnings.warn(
                    "get_or_create_vertex_property: not specifying a type is deprecated "
                    "since 23.4, use get_vertex_property instead",
                    DeprecationWarning
                )
                return self.get_vertex_property(name)

            if dim is not Ellipsis:
                warnings.warn(
                    "get_or_create_vertex_property: the 'dim' parameter is deprecated "
                    "since 23.4, use get_or_create_vertex_vector_property instead",
                    DeprecationWarning
                )
                return self.get_or_create_vertex_vector_property(type, dim, name)

            if using_old_signature:
                warnings.warn(
                    "get_or_create_vertex_property: the signature of this method has changed and "
                    "the old signature has been deprecated since 23.4, please switch to the new "
                    "signature"
                    + example_call,
                    DeprecationWarning
                )

            return self._new_get_or_create_vertex_property(type, name)

        def get_or_create_edge_property(
            self,
            type: str = Ellipsis,
            /,
            name: str = Ellipsis,
            dim: int = Ellipsis,
            *,
            data_type: str = Ellipsis,
        ) -> EdgeProperty:
            """Get an edge property if it exists or create a new one otherwise."""

            example_call = (
                ' - example of correct usage: '
                'graph.get_or_create_edge_property("long", "property_name")'
            )

            # Raise errors for calls that are illegal with old signature and with new signature.
            if type is not Ellipsis and name is not Ellipsis and data_type is not Ellipsis:
                raise TypeError(
                    "get_or_create_edge_property() received too many arguments" + example_call
                )
            if type is Ellipsis and name is Ellipsis:
                raise TypeError(
                    "get_or_create_edge_property() missing required argument 'type'"
                    + example_call
                )

            using_old_signature = (
                type is Ellipsis
                or name is Ellipsis
                or (name in list(property_types) and type not in list(property_types))
                or dim is not Ellipsis
            )
            if using_old_signature:
                # The old signature had arguments in different order. We need to switch them around.
                # Since arguments could have been passed by keyword or positionally, there are lots
                # of combinations to cover.
                if type is not Ellipsis and name is not Ellipsis:
                    type, name = name, type
                elif type is not Ellipsis and data_type is not Ellipsis:
                    type, name = data_type, type
                elif name is not Ellipsis and data_type is not Ellipsis:
                    type, name = data_type, name
                elif type is not Ellipsis:
                    type, name = None, type
                else:
                    assert name is not Ellipsis
                    type, name = None, name

            if type is None:
                warnings.warn(
                    "get_or_create_edge_property: not specifying a type is deprecated "
                    "since 23.4, use get_edge_property instead",
                    DeprecationWarning
                )
                return self.get_edge_property(name)

            if dim is not Ellipsis:
                warnings.warn(
                    "get_or_create_edge_property: the 'dim' parameter is deprecated "
                    "since 23.4, use get_or_create_edge_vector_property instead",
                    DeprecationWarning
                )
                return self.get_or_create_edge_vector_property(type, dim, name)

            if using_old_signature:
                warnings.warn(
                    "get_or_create_edge_property: the signature of this method has changed and "
                    "the old signature has been deprecated since 23.4, please switch to the new "
                    "signature"
                    + example_call,
                    DeprecationWarning
                )

            return self._new_get_or_create_edge_property(type, name)


class BipartiteGraph(PgxGraph):
    """A bipartite PgxGraph.

    Constructor arguments:

    :param session: Pgx Session
    :type session: PgxSession
    :param java_graph: Java PgxGraph
    :type java_graph: oracle.pgx.api.PgxGraph
    """

    _java_class = "oracle.pgx.api.BipartiteGraph"

    def __init__(self, session: "PgxSession", java_graph) -> None:
        super().__init__(session, java_graph)

    def get_is_left_property(self) -> VertexProperty:
        """Get the 'is Left' vertex property of the graph."""
        is_left_prop = java_handler(self._graph.getIsLeftProperty, [])
        return VertexProperty(self, is_left_prop)
