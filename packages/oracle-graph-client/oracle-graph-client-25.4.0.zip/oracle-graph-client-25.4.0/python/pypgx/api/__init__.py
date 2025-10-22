#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

"""Public API for the PGX client.

Classes found in the ``pypgx.api`` package and its subpackages should typically
not be directly instantiated by the user. Instead, they are returned by functions,
instance methods, and in some cases, class methods.
"""

from ._all_paths import AllPaths
from ._analyst import Analyst
from ._compiled_program import CompiledProgram
from ._entity_provider_meta_data import (
    EntityProviderMetaData,
    EdgeProviderMetaData,
    VertexProviderMetaData
)
from ._graph_alteration_builder import GraphAlterationBuilder
from ._graph_builder import EdgeBuilder, GraphBuilder, VertexBuilder
from ._graph_change_set import EdgeModifier, GraphChangeSet, VertexModifier
from ._graph_config import GraphConfig
from ._graph_config_factory import GraphConfigFactory
from ._graph_delta import GraphDelta
from ._graph_meta_data import GraphMetaData
from ._graph_offloading import (
    PreparedPgqlQueryBooleanArgument,
    PreparedPgqlQueryDateArgument,
    PreparedPgqlQueryDoubleArgument,
    PreparedPgqlQueryFloatArgument,
    PreparedPgqlQueryIntegerArgument,
    PreparedPgqlQueryLongArgument,
    PreparedPgqlQueryStringArgument,
    PreparedPgqlQueryTimeArgument,
    PreparedPgqlQueryTimestampArgument,
    PreparedPgqlQueryTimestampWithTimezoneArgument,
    PreparedPgqlQueryTimeWithTimezoneArgument,
    PreparedPgqlQuery
)
from ._graph_property_config import GraphPropertyConfig
from ._graph_config_interfaces import DbConnectionConfig, TwoTablesGraphConfig
from ._file_graph_config import FileGraphConfig, TwoTablesTextGraphConfig
from ._key_column import KeyColumnDescriptor
from ._partitioned_graph_config import PartitionedGraphConfig
from ._rdf_graph_config import RdfGraphConfig
from ._two_tables_rdbms_graph_config import TwoTablesRdbmsGraphConfig
from ._matrix_factorization_model import MatrixFactorizationModel
from ._mutation_strategy_builder import (
    MutationStrategyBuilder,
    MergingStrategyBuilder,
    PickingStrategyBuilder
)
from ._namespace import (
    Namespace,
    NAMESPACE_PRIVATE,
    NAMESPACE_PUBLIC
)
from ._operation import Operation
from ._partition import PgxPartition
from ._pgql_result_element import PgqlResultElement
from ._pgql_result_set import PgqlResultSet
from ._pgx import Pgx
from ._pgx_collection import (
    EdgeCollection,
    EdgeSequence,
    EdgeSet,
    PgxCollection,
    ScalarCollection,
    ScalarSequence,
    ScalarSet,
    VertexCollection,
    VertexSequence,
    VertexSet,
)
from ._pgx_entity import PgxEdge, PgxEntity, PgxVertex
from ._pgx_graph import BipartiteGraph, PgxGraph
from ._pgx_map import PgxMap
from ._pgx_path import PgxPath
from ._pgx_session import PgxSession
from ._prepared_statement import PreparedStatement
from ._property import EdgeLabel, EdgeProperty, VertexProperty, VertexLabels, PgxProperty
from ._property_meta_data import PropertyMetaData
from ._scalar import Scalar
from ._server_instance import ServerInstance
from ._session_context import SessionContext
from ._synchronizer import Synchronizer
from ._execution_environment import ExecutionEnvironment, CpuEnvironment, IoEnvironment

__all__ = [name for name in dir() if not name.startswith('_')]
