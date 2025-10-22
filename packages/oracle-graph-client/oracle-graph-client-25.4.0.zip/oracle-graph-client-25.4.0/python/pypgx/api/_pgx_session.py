#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

import datetime
import json
import os
import collections.abc
import warnings

from jnius import autoclass, cast

from pypgx.api._analyst import Analyst
from pypgx.api._compiled_program import CompiledProgram
from pypgx.api._graph_builder import GraphBuilder
from pypgx.api._graph_offloading import PreparedPgqlQuery, _apply_prepared_query_arguments
from pypgx.api._pgx_collection import ScalarSequence, ScalarSet
from pypgx.api.frames._pgx_frame import PgxFrame
from pypgx.api.frames._pgx_frame_builder import PgxFrameBuilder
from pypgx.api.frames._pgx_frame_reader import PgxGenericFrameReader
from pypgx.api.frames._vertex_frame_declaration import VertexFrameDeclaration
from pypgx.api.frames._edge_frame_declaration import EdgeFrameDeclaration
from pypgx.api._pgx_graph import PgxGraph
from pypgx.api._pgx_map import PgxMap
from pypgx.api._pgql_result_set import PgqlResultSet
from pypgx.api._operation import Operation
from pypgx.api._prepared_statement import PreparedStatement
from pypgx.api._server_instance import ServerInstance
from pypgx.api._pgx_context_manager import PgxContextManager
from pypgx.api._session_context import SessionContext
from pypgx.api._graph_config import GraphConfig
from pypgx.api._graph_meta_data import GraphMetaData
from pypgx._utils.error_handling import java_handler
from pypgx._utils.error_messages import (
    INVALID_OPTION,
    VALID_CONFIG_ARG,
    VALID_PATH_LISTS,
    VALID_PATH_OR_LIST_OF_PATHS,
    UNSUPPORTED_QUERY_TYPE,
)
from pypgx._utils import conversion
from pypgx._utils.pgx_types import (
    format_types,
    source_types,
    read_graph_options,
    id_generation_strategies,
    id_types,
    id_strategies,
    property_types,
    time_units,
    compiler_optimizations,
    property_loading_option
)
from pypgx.api.frames._pgx_data_types import _get_data_type
from pypgx._utils.error_messages import UNHASHABLE_TYPE, ARG_MUST_BE, ARG_MUST_BE_REASON
from pypgx.api._namespace import Namespace
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union, Any, NoReturn
from pypgx.api._execution_environment import ExecutionEnvironment

# Read the static final variable LATEST_SNAPSHOT from the corresponding java class

_PgxSession_class = autoclass('oracle.pgx.api.PgxSession')
_LATEST_SNAPSHOT = _PgxSession_class.LATEST_SNAPSHOT

_ColumnDescriptor = autoclass('oracle.pgx.api.frames.schema.ColumnDescriptor')


class PgxSession(PgxContextManager):
    """A PGX session represents an active user connected to a ServerInstance.

    Every session gets a workspace assigned on the server, which can be used to
    read graph data, create transient data or custom algorithms for the sake of
    graph analysis. Once a session gets destroyed, all data in the session
    workspace is freed.

    :ivar LATEST_SNAPSHOT: The timestamp of the most recent snapshot, used to easily move to the
        newest snapshot (see :meth:`set_snapshot`)
    :type LATEST_SNAPSHOT: int or None
    """

    _java_class = 'oracle.pgx.api.PgxSession'

    def __init__(self, java_session) -> None:
        self._session = java_session
        java_analyst = java_session.createAnalyst()
        self.analyst = Analyst(self, java_analyst)
        self.context = SessionContext(java_session.getSessionContext())

    LATEST_SNAPSHOT = _LATEST_SNAPSHOT

    @property
    def id(self) -> str:
        """Get the ID of the session.

        :return: The ID of the session.
        """
        return self._session.getName()

    @property
    def source(self) -> str:
        """Get the current session source.

        :return: the session source.
        """
        return self._session.getSource()

    @property
    def idle_timeout(self) -> Optional[int]:
        """Get the idle timeout in seconds.

        :return: the idle timeout.
        """
        return self._session.getIdleTimeout()

    @property
    def task_timeout(self) -> Optional[int]:
        """Get the task timeout in seconds.

        :return: the task timeout.
        """
        return self._session.getTaskTimeout()

    @property
    def server_instance(self) -> ServerInstance:
        """Get the server instance.

        :returns: The server instance
        """
        instance = self._session.getServerInstance()
        return ServerInstance(instance)

    def create_analyst(self) -> Analyst:
        """Create and return a new analyst.

        :returns: An analyst object
        """
        java_analyst = self._session.createAnalyst()
        return Analyst(self, java_analyst)

    def get_graph(self, name: str, namespace: Optional[Namespace] = None) -> Optional[PgxGraph]:
        """Find and return a graph with name `name` within the given namespace loaded inside PGX.

        The search for the snapshot to return is done according to the following rules:

            - if namespace is private, than the search occurs on already referenced snapshots of the
              graph with name `name` and the most recent snapshot is returned
            - if namespace is public, then the search occurs on published graphs and the most recent
              snapshot of the published graph with name `name` is returned
            - if namespace is None, then the private namespace is searched first and, if no snapshot
              is found, the public namespace is then searched

        Multiple calls of this method with the same parameters will return different
        :class:`PgxGraph` objects referencing the same graph, with the server keeping track
        of how many references a session has to each graph.

        Therefore, a graph is released within the server either if:

            - all the references are moved to another graph (e.g. via :meth:`set_snapshot`)
            - the :meth:`PgxGraph.destroy` method is called on one reference. Note that
              this invalidates all references

        :param name: The name of the graph
        :type name: str
        :param namespace: The namespace where to look up the graph
        :type namespace: Namespace or None
        :returns: The graph with the given name
        :rtype: PgxGraph or None
        """
        if namespace is None:
            graph = java_handler(self._session.getGraph, [name])
        else:
            graph = java_handler(self._session.getGraph, [namespace.get_java_namespace(), name])
        if graph is None:
            return None
        return PgxGraph(self, graph)

    def get_graphs(self, namespace: Namespace) -> List[str]:
        """Return a collection of graph names accessible under the given namespace.

        :param namespace: The namespace where to look up the graphs
        """
        return list(java_handler(self._session.getGraphs, [namespace.get_java_namespace()]))

    def get_compiled_program(self, id: str) -> CompiledProgram:
        """Get a compiled program by ID.

        :param id: The id of the compiled program
        """
        program = java_handler(self._session.getCompiledProgram, [id])
        return CompiledProgram(self, program)

    def get_available_compiled_program_ids(self) -> Set[str]:
        """Get the set of available compiled program IDs."""
        return set(self._session.getAvailableCompiledProgramIds())

    def compile_program_code(
        self,
        code: str,
        overwrite: bool = False,
        parrallel: bool = True,
        disabled_optimizations: Optional[List[str]] = None,
        verbose: bool = False,
    ) -> CompiledProgram:
        """Compile a Green-Marl program (if it is supported by the corresponding PyPGX distribution).
        Otherwise compile a Java program.

        :param code: The Green-Marl/Java code to compile
        :param overwrite:  If the procedure in the given code already exists, overwrite if true,
            throw an exception otherwise
        :param parrallel: if False, the compiled program will be optimized for sequential execution
        :param disabled_optimizations: list of compiler optimizations to disable
        :param verbose: if True, the compiler will output compilation stages
        """
        java_disabled_optimizations = []
        if disabled_optimizations is not None:
            for optimization in disabled_optimizations:
                if optimization in compiler_optimizations:
                    java_disabled_optimizations.append(compiler_optimizations[optimization])
                else:
                    raise ValueError(
                        INVALID_OPTION.format(
                            var="disabled_optimizations", opts=list(compiler_optimizations.keys())
                        )
                    )

        program = java_handler(
            self._session.compileProgramCode,
            (
                code,
                overwrite,
                parrallel,
                conversion.to_java_list(java_disabled_optimizations),
                verbose,
            ),
        )
        return CompiledProgram(self, program)

    def compile_program(self, path: str, overwrite: bool = False) -> CompiledProgram:
        """Compile a Green-Marl program for parallel execution with all optimizations enabled.

        :param path: Path to program
        :param overwrite:  If the procedure in the given code already exists, overwrite if true,
            throw an exception otherwise
        """
        program = java_handler(self._session.compileProgram, (path, overwrite))
        return CompiledProgram(self, program)

    def create_graph_builder(
        self,
        id_type: str = "integer",
        vertex_id_generation_strategy: str = "user_ids",
        edge_id_generation_strategy: str = "auto_generated",
    ) -> GraphBuilder:
        """Create a graph builder with the given vertex ID type and Ids Mode.

        :param id_type: The type of the vertex ID
        :param vertex_id_generation_strategy: The vertices Id generation
            strategy to be used
        :param edge_id_generation_strategy: The edges Id generation strategy to be used
        """
        if id_type in id_types:
            java_id_type = id_types[id_type]
        else:
            raise ValueError(INVALID_OPTION.format(var='id_type', opts=list(id_types.keys())))
        if vertex_id_generation_strategy in id_generation_strategies:
            vertex_id_generation_strategy = id_generation_strategies[vertex_id_generation_strategy]
        else:
            raise ValueError(
                INVALID_OPTION.format(
                    var='vertex_id_generation_strategy', opts=list(id_generation_strategies.keys())
                )
            )
        if edge_id_generation_strategy in id_generation_strategies:
            edge_id_generation_strategy = id_generation_strategies[edge_id_generation_strategy]
        else:
            raise ValueError(
                INVALID_OPTION.format(
                    var='edge_id_generation_strategy', opts=list(id_generation_strategies.keys())
                )
            )
        builder = java_handler(
            self._session.createGraphBuilder,
            [java_id_type, vertex_id_generation_strategy, edge_id_generation_strategy],
        )
        return GraphBuilder(self, builder, java_id_type.toString())

    def create_frame(
        self,
        schema: List[Tuple[str, str]],
        column_data: Dict[str, List],
        frame_name: str,
    ) -> PgxFrame:
        """Create a frame with the specified data

        :param schema: List of tuples (columnName, columnType)
        :param column_data: Map of iterables, columnName -> columnData
        :param frame_name: Name of the frame
        :return: A frame builder initialized with the given schema
        """
        if not isinstance(column_data, dict):
            raise TypeError(ARG_MUST_BE.format(arg='column_data', type=dict))
        if not isinstance(frame_name, str):
            raise TypeError(ARG_MUST_BE.format(arg='frame_name', type=str))
        java_column_descriptors = autoclass('java.util.ArrayList')()
        for col_desc in schema:
            column_name = col_desc[0]
            column_type = _get_data_type(col_desc[1])
            java_column_descriptors.add(
                _ColumnDescriptor.columnDescriptor(column_name, column_type)
            )
        java_data = autoclass('java.util.HashMap')()
        for column_name in column_data:
            python_list = column_data[column_name]
            java_list = autoclass('java.util.ArrayList')()
            for x in python_list:
                java_list.add(conversion.anything_to_java(x))
            java_data.put(column_name, java_list)
        java_frame = java_handler(
            self._session.createFrame,
            [java_column_descriptors, java_data, frame_name],
        )
        return PgxFrame(java_frame)

    def create_frame_builder(self, schema: List[Tuple[str, str]]) -> PgxFrameBuilder:
        """Create a frame builder initialized with the given schema

        :param schema: List of tuples (columnName, columnType)
        :return: A frame builder initialized with the given schema
        """
        java_column_descriptors = autoclass('java.util.ArrayList')()
        for col_desc in schema:
            column_name = col_desc[0]
            column_type = _get_data_type(col_desc[1])
            java_column_descriptors.add(
                _ColumnDescriptor.columnDescriptor(column_name, column_type)
            )
        java_builder = java_handler(
            self._session.createFrameBuilder,
            [java_column_descriptors],
        )
        return PgxFrameBuilder(java_builder)

    def pandas_to_pgx_frame(self, pandas_dataframe, frame_name: str) -> PgxFrame:
        """Create a frame from a pandas dataframe.

        Duplicate columns will be renamed. Mixed column types are not supported.

        This method requires pandas.

        :param pandas_dataframe: The Pandas dataframe to use
        :param frame_name: Name of the frame
        :return: the frame created
        """
        # Mixed columns will throw an error on the Java side when validating the columns
        try:
            import pandas as pd
        except Exception:
            raise ImportError("Could not find pandas package")
        if not isinstance(pandas_dataframe, pd.DataFrame):
            raise TypeError(ARG_MUST_BE.format(arg='pandas_dataframe', type=pd.DataFrame))
        if not isinstance(frame_name, str):
            raise TypeError(ARG_MUST_BE.format(arg='frame_name', type=str))
        schema = []
        data: Dict[str, list] = {}
        column_name_counts: Dict[str, int] = {}
        for name, col in pandas_dataframe.items():
            count = column_name_counts.get(name, 0)
            if count > 0:
                name = '{}.{}'.format(name, count)
            column_name_counts[name] = count + 1
            data_type = col.dtype
            if data_type == 'int64':
                schema.append((name, "LONG_TYPE"))
                data[name] = col.values.tolist()
            elif data_type in ['int32', 'int16', 'int8']:
                schema.append((name, "INTEGER_TYPE"))
                data[name] = col.values.tolist()
            elif data_type == 'float64':
                schema.append((name, "DOUBLE_TYPE"))
                data[name] = col.values.tolist()
            elif data_type in ['float32', 'float16']:
                schema.append((name, "FLOAT_TYPE"))
                data[name] = col.values.tolist()
            elif data_type == 'bool':
                schema.append((name, "BOOLEAN_TYPE"))
                data[name] = col.values.tolist()
            elif data_type == 'object':
                if len(col) == 0:
                    schema.append((name, "STRING_TYPE"))
                    data[name] = col
                else:
                    el = col[0]
                    if isinstance(el, datetime.date) and not isinstance(el, datetime.datetime):
                        schema.append((name, "LOCAL_DATE_TYPE"))
                        data[name] = col.values.tolist()
                    elif isinstance(el, datetime.time):
                        if el.tzinfo:
                            schema.append((name, "TIME_WITH_TIMEZONE_TYPE"))
                        else:
                            schema.append((name, "TIME_TYPE"))
                            data[name] = col.values.tolist()
                    elif isinstance(el, datetime.datetime):
                        if el.tzinfo:
                            schema.append((name, "TIMESTAMP_WITH_TIMEZONE_TYPE"))
                        else:
                            schema.append((name, "TIMESTAMP_TYPE"))
                        data[name] = pandas_dataframe[name].values.tolist()
                    else:
                        schema.append((name, "STRING_TYPE"))
                        data[name] = pandas_dataframe[name].apply(str).values.tolist()
            else:
                raise ValueError(
                    INVALID_OPTION.format(
                        var='data_type',
                        opts=[
                            'int8',
                            'int16',
                            'int32',
                            'int64',
                            'float16',
                            'float32',
                            'float64',
                            'bool',
                            'object',
                        ],
                    )
                )
        return self.create_frame(schema, data, frame_name)

    def read_graph_by_name(
        self, graph_name: str,
        graph_source: str,
        schema: Optional[str] = None,
        options: Tuple[Union[str, property_loading_option], ...] = ()
    ) -> PgxGraph:
        """
        :param graph_name: Name of graph
        :param graph_source: Source of graph
        :param schema: Schema of graph
        :param options: Tuple of read graph options.
        The options are either strings, or property loading options.
        property loading options are used to filter the set of properties to be loaded:
        by default, all properties are loaded.

        To include only a sub-set of properties,
        use the :func: `pypgx._utils.pgx_types.include_properties` method,
        with a property map parameter specified the properties to be included for each provider.

        To exclude a sub-set of properties,
        use the :func: `pypgx._utils.pgx_types.exclude_properties` method,
        with a property map parameter specified the properties to be excluded for each provider.

        To load the graph without properties,
        use the :func: `pypgx._utils.pgx_types.topology_only` method

        The possible string options are in the list below.

        List of options:

        ``optimized_for_updates``: Specify if the loaded graph will be optimized for updates
        (Default).

        ``optimized_for_read``: Specify if the loaded graph will be optimized for reads.

        ``synchronizable``: If used and graph cannot be synchronized, PGX will throw an Exception.

        ``on_missing_vertex_ignore_edge``: Ignore edges with missing source/destination vertex
        (without logging).

        ``on_missing_vertex_ignore_edge_log``: Ignore edges with missing source/destination vertex
        and log every ignored edge.

        ``on_missing_vertex_ignore_edge_log_once``: Ignore edges with missing source/destination
        vertex and log the first ignored edge.

        ``on_missing_vertex_error``: Throw an error when an edge misses source/destination vertex
        (Default).

        .. versionchanged:: 24.1
            Added the ``options`` parameter.
        """
        if graph_source is None or graph_source not in source_types:
            raise ValueError(
                INVALID_OPTION.format(var='graph_source', opts=list(source_types.keys()))
            )
        java_graph_source = source_types[graph_source]
        read_graph_by_name_args = [schema, graph_name, java_graph_source]
        for option in options:
            if isinstance(option, str):
                if option not in read_graph_options:
                    raise ValueError(
                        INVALID_OPTION.format(var='option', opts=list(read_graph_options.keys()))
                    )
                else:
                    read_graph_by_name_args.append(read_graph_options[option])
            elif isinstance(option, property_loading_option):
                read_graph_by_name_args.append(option)
            else:
                raise ValueError(
                    INVALID_OPTION.format(var='option', opts=list(read_graph_options.keys()))
                )

        graph = java_handler(self._session.readGraphByName, read_graph_by_name_args)
        return PgxGraph(self, graph)

    def read_graph_file(
        self, file_path: str, file_format: Optional[str] = None,
        graph_name: Optional[str] = None
    ) -> PgxGraph:
        """
        :param file_path: File path
        :param file_format: File format of graph
        :param graph_name: Name of graph
        """
        if file_format is not None and file_format not in format_types:
            raise ValueError(
                INVALID_OPTION.format(var='file_format', opts=list(format_types.keys()))
            )
        if file_format is not None:
            file_format = format_types[file_format]
        graph = java_handler(self._session.readGraphFile, [file_path, file_format, graph_name])
        return PgxGraph(self, graph)

    def read_graph_files(
        self,
        file_paths: Union[str, Iterable[str]],
        edge_file_paths: Optional[Union[str, Iterable[str]]] = None,
        file_format: Optional[str] = None,
        graph_name: Optional[str] = None,
    ) -> PgxGraph:
        """Load the graph contained in the files at the given paths.

        :param file_paths: Paths to the vertex files
        :param edge_file_paths: Path to the edge file
        :param file_format:  File format
        :param graph_name:  Loaded graph name
        """
        if file_format is not None and file_format not in format_types:
            raise ValueError(
                INVALID_OPTION.format(var='file_format', opts=list(format_types.keys()))
            )
        if file_format is not None:
            file_format = format_types[file_format]
        if not (
            isinstance(file_paths, collections.abc.Iterable)
            and (isinstance(edge_file_paths, collections.abc.Iterable) or edge_file_paths is None)
        ):
            raise TypeError(VALID_PATH_LISTS.format(path1='file_paths', path2='edge_file_paths'))
        f_paths = self._read_file_paths(file_paths, 'file_paths')
        graph = None
        if edge_file_paths is None:
            graph = java_handler(self._session.readGraphFiles, [f_paths, file_format, graph_name])
        else:
            e_paths = self._read_file_paths(edge_file_paths, 'edge_file_paths')
            graph = java_handler(
                self._session.readGraphFiles, [f_paths, e_paths, file_format, graph_name]
            )
        return PgxGraph(self, graph)

    def _read_file_paths(
        self,
        file_paths: Union[str, Iterable[str]],
        path_var_name: str,
    ) -> Union[str, Iterable]:
        """
        :param file_paths: File path
        :param path_var_name: The path variable name
        :return: the file paths
        """
        if isinstance(file_paths, str):
            return file_paths
        elif isinstance(file_paths, collections.abc.Iterable):
            f_paths = autoclass('java.util.ArrayList')()
            for f in file_paths:
                f_paths.add(f)
            return f_paths
        raise TypeError(VALID_PATH_OR_LIST_OF_PATHS.format(path=path_var_name))

    def read_graph_with_properties(
        self,
        config: Union[str, os.PathLike, Dict[str, Any], GraphConfig],
        max_age: int = 9223372036854775807,
        max_age_time_unit: str = 'days',
        block_if_full: bool = False,
        update_if_not_fresh: bool = True,
        graph_name: Optional[str] = None,
    ) -> PgxGraph:
        """Read a graph and its properties, specified in the graph config, into memory.

        :param config: The graph config
        :param max_age: If another snapshot of the given graph already exists,
            the age of the latest existing snapshot will be compared to the given maxAge.
            If the latest snapshot is in the given range,
            it will be returned, otherwise a new snapshot will be created.
        :param max_age_time_unit: The time unit of the maxAge parameter
        :param block_if_full:  If true and a new snapshot needs to be created but
            no more snapshots are allowed by the server configuration, the
            returned future will not complete until space becomes available.
            Iterable full and this flag is false, the returned future will
            complete exceptionally instead.
        :param update_if_not_fresh:  If a newer data version exists in the backing data source
            (see PgxGraph.is_fresh()),
            this flag tells whether to read it and create another snapshot inside PGX.
            If the "snapshots_source" field of config is SnapshotsSource.REFRESH,
            the returned graph may have multiple snapshots, depending on whether
            previous reads with the same config occurred; otherwise, if the
            "snapshots_source" field is SnapshotsSource.CHANGE_SET,
            only the most recent snapshot (either pre-existing or freshly read) will be visible.
        :param graph_name:   How the graph should be named. If null, a name will be generated.
            If a graph with that name already exists, the returned future will
            complete exceptionally.
        """
        if update_if_not_fresh:
            max_age = 0
        if max_age_time_unit not in time_units:
            raise ValueError(
                INVALID_OPTION.format(var='max_age_time_unit', opts=list(time_units.keys()))
            )
        max_age_time_unit = time_units[max_age_time_unit]

        if isinstance(config, (str, os.PathLike)):
            config = os.fspath(config)
            graph = java_handler(self._session.readGraphWithProperties, [config, graph_name])
        elif isinstance(config, GraphConfig):
            graph = java_handler(
                self._session.readGraphWithProperties,
                [config._graph_config, max_age, max_age_time_unit, block_if_full, graph_name],
            )
        elif isinstance(config, dict):
            config = json.dumps(config)
            graph_config_factory = autoclass('oracle.pgx.config.GraphConfigFactory')
            graph_config = autoclass('oracle.pgx.config.GraphConfig')
            config = java_handler(graph_config_factory.forAnyFormat().fromJson, [config])
            config = cast(graph_config, config)
            graph = java_handler(
                self._session.readGraphWithProperties,
                [config, max_age, max_age_time_unit, block_if_full, graph_name],
            )
        else:
            raise TypeError(
                VALID_CONFIG_ARG.format(config='config', config_type=GraphConfig.__name__)
            )
        return PgxGraph(self, graph)

    def read_subgraph_from_pg_pgql(
            self,
            view: str,
            queries: Union[None, str, PreparedPgqlQuery,
                           List[Union[str, PreparedPgqlQuery]]] = None,
            config: Optional[GraphConfig] = None,
            *,
            num_connections: Optional[int] = None,
            data_source_id: Optional[str] = None,
            jdbc_url: Optional[str] = None,
            keystore_alias: Optional[str] = None,
            password: Optional[str] = None,
            schema: Optional[str] = None,
            username: Optional[str] = None,
            graph_name: Optional[str] = None,
            escape_keys_with_pgx_special_characters: Optional[bool] = None
    ) -> PgxGraph:
        """Load a graph from PGQL.

        :param view: The name of the PG View.
        :param graph_name: the name of the resulting graph.
        :param queries: A query or queries used to specify which data is to be loaded.
        :param config: An optional config used to describe how data should be loaded.
        :param num_connections: The number of connections to open to load the data in parallel.
        :param data_source_id: The dataSourceId to which to connect.
        :param jdbc_url: The jdbcUrl to use for connection to the DB.
        :param keystore_alias: The key store alias to retrieve the password from the keystore.
        :param password: The password to use for connecting to the database.
        :param schema: The schema from which to load the PG view.
        :param username: The username of the DB user to use to connect to the DB.
        :param escape_keys_with_pgx_special_characters: A flag indicating whether to escape
            keys containing special characters in subgraph loading.
        :return: The graph.
        """
        generic_reader = java_handler(self._session.readSubgraph, [])
        reader = java_handler(generic_reader.fromPgPgql, [schema, view])
        return self._read_subgraph_with_pgql(
            reader, queries=queries, config=config,
            num_connections=num_connections,
            data_source_id=data_source_id, jdbc_url=jdbc_url,
            keystore_alias=keystore_alias, password=password,
            username=username, graph_name=graph_name,
            escape_keys_with_pgx_special_characters=escape_keys_with_pgx_special_characters
        )

    def read_subgraph_from_pg_view(
            self,
            view: str,
            queries: Union[None, str, PreparedPgqlQuery,
                           List[Union[str, PreparedPgqlQuery]]] = None,
            config: Optional[GraphConfig] = None,
            *,
            num_connections: Optional[int] = None,
            data_source_id: Optional[str] = None,
            jdbc_url: Optional[str] = None,
            keystore_alias: Optional[str] = None,
            password: Optional[str] = None,
            schema: Optional[str] = None,
            username: Optional[str] = None,
            graph_name: Optional[str] = None,
            escape_keys_with_pgx_special_characters: Optional[bool] = None
    ) -> PgxGraph:
        """Load a graph from PG Views.

        :param view: The name of the PG View.
        :param graph_name: the name of the resulting graph.
        :param queries: A query or queries used to specify which data is to be loaded.
        :param config: An optional config used to describe how data should be loaded.
        :param num_connections: The number of connections to open to load the data in parallel.
        :param data_source_id: The dataSourceId to which to connect.
        :param jdbc_url: The jdbcUrl to use for connection to the DB.
        :param keystore_alias: The key store alias to retrieve the password from the keystore.
        :param password: The password to use for connecting to the database.
        :param schema: The schema from which to load the PG view.
        :param username: The username of the DB user to use to connect to the DB.
        :param escape_keys_with_pgx_special_characters: A flag indicating whether
            to escape keys containing special characters in subgraph loading.
        :return: The graph.
        """
        warnings.warn(
            "read_subgraph_from_pg_view: this method has been deprecated since 24.1,"
            " please use read_subgraph_from_pg_pgql instead",
            DeprecationWarning
        )
        generic_reader = java_handler(self._session.readSubgraph, [])
        reader = java_handler(generic_reader.fromPgPgql, [schema, view])
        return self._read_subgraph_with_pgql(
            reader, queries=queries, config=config,
            num_connections=num_connections,
            data_source_id=data_source_id, jdbc_url=jdbc_url,
            keystore_alias=keystore_alias, password=password,
            username=username, graph_name=graph_name,
            escape_keys_with_pgx_special_characters=escape_keys_with_pgx_special_characters
        )

    def read_subgraph_from_pg_sql(
            self,
            sql_graph_name: str,
            queries: Union[None, str, PreparedPgqlQuery,
                           List[Union[str, PreparedPgqlQuery]]] = None,
            config: Optional[GraphConfig] = None,
            *,
            num_connections: Optional[int] = None,
            data_source_id: Optional[str] = None,
            jdbc_url: Optional[str] = None,
            keystore_alias: Optional[str] = None,
            password: Optional[str] = None,
            schema: Optional[str] = None,
            username: Optional[str] = None,
            graph_name: Optional[str] = None,
            escape_keys_with_pgx_special_characters: Optional[bool] = None

    ) -> PgxGraph:
        """Load a subgraph of a SQL property graph.

        :param sql_graph_name: The name of SQL graph.
        :param graph_name: the name of the resulting graph.
        :param queries: A query or queries used to specify which data is to be loaded.
        :param config: An optional config used to describe how data should be loaded.
        :param num_connections: The number of connections to open to load the data in parallel.
        :param data_source_id: The dataSourceId to which to connect.
        :param jdbc_url: The jdbcUrl to use for connection to the DB.
        :param keystore_alias: The key store alias to retrieve the password from the keystore.
        :param password: The password to use for connecting to the database.
        :param schema: The schema from which to load the PG view.
        :param username: The username of the DB user to use to connect to the DB.
        :param escape_keys_with_pgx_special_characters: A flag indicating whether
            to escape keys containing special characters in subgraph loading.
        :return: The graph.
        """
        generic_reader = java_handler(self._session.readSubgraph, [])
        reader = java_handler(generic_reader.fromPgSql, [schema, sql_graph_name])
        return self._read_subgraph_with_pgql(
            reader, queries=queries, config=config,
            num_connections=num_connections,
            data_source_id=data_source_id, jdbc_url=jdbc_url,
            keystore_alias=keystore_alias, password=password,
            username=username, graph_name=graph_name,
            escape_keys_with_pgx_special_characters=escape_keys_with_pgx_special_characters
        )

    def _read_subgraph_with_pgql(
            self,
            reader,
            queries: Union[None, str, PreparedPgqlQuery,
                           List[Union[str, PreparedPgqlQuery]]] = None,
            config: Optional[GraphConfig] = None,
            *,
            num_connections: Optional[int] = None,
            data_source_id: Optional[str] = None,
            jdbc_url: Optional[str] = None,
            keystore_alias: Optional[str] = None,
            password: Optional[str] = None,
            username: Optional[str] = None,
            graph_name: Optional[str] = None,
            escape_keys_with_pgx_special_characters: Optional[bool] = None
    ) -> PgxGraph:
        # The DB parameters and config
        if config is not None:
            java_handler(reader.withConfig, [config._graph_config])
        if num_connections is not None:
            java_handler(reader.connections, [num_connections])
        if data_source_id is not None:
            java_handler(reader.dataSourceId, [data_source_id])
        if jdbc_url is not None:
            java_handler(reader.jdbcUrl, [jdbc_url])
        if keystore_alias is not None:
            java_handler(reader.keystoreAlias, [keystore_alias])
        if password is not None:
            java_handler(reader.password, [password])
        if username is not None:
            java_handler(reader.username, [username])
        if escape_keys_with_pgx_special_characters is not None:
            java_handler(
                reader.escapeKeysWithPgxSpecialCharacters,
                [escape_keys_with_pgx_special_characters]
            )
        # The query
        if isinstance(queries, str):
            java_handler(reader.queryPgql, [queries])
        elif isinstance(queries, PreparedPgqlQuery):
            prepared_pgql_query = java_handler(reader.preparedPgqlQuery, [queries.query])
            _apply_prepared_query_arguments(prepared_pgql_query, queries.arguments)
        elif isinstance(queries, list):
            for query in queries:
                if isinstance(query, str):
                    java_handler(reader.queryPgql, [query])
                elif isinstance(query, PreparedPgqlQuery):
                    prepared_pgql_query = java_handler(reader.preparedPgqlQuery, [query.query])
                    _apply_prepared_query_arguments(prepared_pgql_query, query.arguments)
                else:
                    raise TypeError(UNSUPPORTED_QUERY_TYPE)
        else:
            raise TypeError(UNSUPPORTED_QUERY_TYPE)
        # if graph_name is 'None' the Java client handles it and treats it as 'null'
        return PgxGraph(self, java_handler(reader.load, [graph_name]))

    def register_keystore(self, keystore_path: str, keystore_password: str) -> None:
        """Register a keystore.

        :param keystore_path: The path to the keystore which shall be registered
        :param keystore_password: The password of the provided keystore
        """
        java_handler(self._session.registerKeystore, (keystore_path, keystore_password))

    def get_available_snapshots(self, snapshot: PgxGraph) -> List[GraphMetaData]:
        """Return a list of all available snapshots of the given input graph.

        :param snapshot: A 'PgxGraph' object for which the available snapshots
            shall be retrieved
        :return: A list of 'GraphMetaData' objects, each corresponding to a
            snapshot of the input graph
        """
        if not isinstance(snapshot, PgxGraph):
            raise TypeError(ARG_MUST_BE.format(arg='snapshot', type=PgxGraph.__name__))
        result = list(java_handler(self._session.getAvailableSnapshots, [snapshot._graph]))
        snapshots = []
        for java_graph_meta_data in result:
            snapshots.append(GraphMetaData(java_graph_meta_data))
        return snapshots

    def set_snapshot(
        self,
        graph: Union[str, PgxGraph],
        meta_data: Optional[GraphMetaData] = None,
        creation_timestamp: Optional[int] = None,
        force_delete_properties: bool = False,
    ) -> None:
        """Set a graph to a specific snapshot.

        You can use this method to jump back and forth in time between various
        snapshots of the same graph.
        If successful, the given graph will point to the requested snapshot
        after the returned future completes.

        :param graph: Input graph
        :param meta_data: A GraphMetaData object used to identify the snapshot
        :param creation_timestamp: The metaData object returned by (GraphConfig) identifying
            the version to be checked out
        :param force_delete_properties: Graphs with transient properties
            cannot be checked out to a different version.
            If this flag is set to true, the checked out graph will
            no longer contain any transient properties.
            If false, the returned future will complete exceptionally with
            an UnsupportedOperationException as its cause.

        """
        if not isinstance(graph, PgxGraph):
            raise TypeError(ARG_MUST_BE.format(arg='graph', type=PgxGraph.__name__))
        if not isinstance(meta_data, (type(None), GraphMetaData)):
            raise TypeError(ARG_MUST_BE.format(arg='meta_data', type=GraphMetaData.__name__))
        if not isinstance(creation_timestamp, (type(None), int)):
            raise TypeError(ARG_MUST_BE.format(arg='creation_timestamp', type=int.__name__))
        if not isinstance(force_delete_properties, bool):
            raise TypeError(ARG_MUST_BE.format(arg='force_delete_properties', type=bool.__name__))

        if meta_data is None and creation_timestamp is None:
            raise ValueError("You must specify either a meta data object or a creation timestamp.")

        if meta_data is not None and creation_timestamp is not None:
            if meta_data.get_creation_timestamp() != creation_timestamp:
                raise ValueError(
                    "The provided creation timestamp doesn't match the creation "
                    "timestamp associated with the provided 'GraphMetaData' object."
                )

        if meta_data is not None:
            java_handler(
                self._session.setSnapshot,
                [graph._graph, meta_data._graph_meta_data, force_delete_properties],
            )
        else:
            java_handler(
                self._session.setSnapshot,
                [graph._graph, creation_timestamp, force_delete_properties],
            )

    def get_session_context(self) -> SessionContext:
        """Get the context describing the current session.

        :return: context of this session
        """
        return self.context

    def get_name(self) -> str:
        """Get the identifier of the current session.

        :return: identifier of this session
        """
        return java_handler(self._session.getName, [])

    def get_source(self) -> str:
        """Get the current session source

        :return: session source
        """
        return self.source

    def get_idle_timeout(self) -> Optional[int]:
        """Get the idle timeout of this session

        :return: the idle timeout in seconds
        """
        return self.idle_timeout

    def get_task_timeout(self) -> Optional[int]:
        """Get the task timeout of this session

        :return: the task timeout in seconds
        """
        return self.task_timeout

    def get_pgql_result_set(self, id: str) -> Optional[PgqlResultSet]:
        """Get a PGQL result set by ID.

        :param id: The PGQL result set ID
        :return: The requested PGQL result set or None if no such result set
            exists for this session
        """
        java_pgql_result_set = java_handler(self._session.getPgqlResultSet, [id])
        if java_pgql_result_set is None:
            return None

        java_graph = java_handler(java_pgql_result_set.getGraph, [])
        graph = PgxGraph(self, java_graph)

        return PgqlResultSet(graph, java_pgql_result_set)

    def query_pgql(self, pgql_query: str) -> Optional[PgqlResultSet]:
        """Submit a pattern matching query with a ON-clause.

        The ON-clause indicates the graph on which the query will be executed.
        The graph name in the ON-clause is evaluated with the same semantics as
        PgxSession.getGraph(String).

        :param pgql_query: Query string in PGQL
        :return: The query result set

        throws InterruptedException if the caller thread gets interrupted while
        waiting for completion.
        throws ExecutionException   if any exception occurred during
        asynchronous execution. The actual exception will be nested.
        """
        java_pgql_result_set = java_handler(self._session.queryPgql, [pgql_query])
        if java_pgql_result_set is None:
            return None

        java_graph = java_handler(java_pgql_result_set.getGraph, [])
        graph = PgxGraph(self, java_graph)

        return PgqlResultSet(graph, java_pgql_result_set)

    def execute_pgql(self, pgql_query: str) -> Optional[PgqlResultSet]:
        """Submit any query with a ON-clause.

        The ON-clause indicates the graph on which the query will be executed.
        The graph name in the ON-clause is evaluated with the same semantics as
        PgxSession.getGraphAsync(String).

        :param pgql_query: Query string in PGQL
        :return: The query result set

        throws InterruptedException if the caller thread gets interrupted while
        waiting for completion.
        throws ExecutionException   if any exception occurred during
        asynchronous execution. The actual exception will be nested.
        """
        java_pgql_result_set = java_handler(self._session.executePgql, [pgql_query])
        if java_pgql_result_set is None:
            return None

        java_graph = java_handler(java_pgql_result_set.getGraph, [])
        graph = PgxGraph(self, java_graph)

        return PgqlResultSet(graph, java_pgql_result_set)

    def explain_pgql(self, pgql_query: str) -> Operation:
        """Explain the execution plan of a pattern matching query.

        Note: Different PGX versions may return different execution plans.

        :param pgql_query: Query string in PGQL
        :return: The query plan
        """

        java_operation = java_handler(self._session.explainPgql, [pgql_query])
        return Operation(java_operation)

    def prepare_pgql(self, pgql_query: str) -> PreparedStatement:
        """Prepare a pattern matching query with a ON-clause.

        The ON-clause indicates the graph on which the query will be executed.
        The graph name in the ON-clause is evaluated with the same semantics as
        getGraph(String).

        :param pgql_query: Query string in PGQL
        :return: A prepared statement object
        """
        java_prepared_statement = java_handler(self._session.preparePgql, [pgql_query])
        return PreparedStatement(java_prepared_statement, self)

    def create_set(self, content_type: str, name: Optional[str] = None) -> ScalarSet:
        """Create a set of scalars.

        Possible types are:
        ['integer','long','double','boolean','string','vertex','edge',
        'local_date','time','timestamp','time_with_timezone','timestamp_with_timezone']

        :param content_type: content type of the set
        :param name: the set's name
        :return: A named ScalarSet of content type `content_type`
        """
        if content_type not in property_types:
            raise ValueError(
                INVALID_OPTION.format(var='content_type', opts=list(property_types.keys()))
            )
        t = property_types[content_type]
        return ScalarSet(java_handler(self._session.createSet, [t, name]))

    def create_sequence(self, content_type: str, name: Optional[str] = None) -> ScalarSequence:
        """Create a sequence of scalars.

        Possible types are:
        ['integer','long','double','boolean','string','vertex','edge',
        'local_date','time','timestamp','time_with_timezone','timestamp_with_timezone']

        :param content_type: Property type of the elements in the sequence
        :param name: Sequence name
        :return: A named ScalarSequence of content type `content_type`
        """
        if content_type not in property_types:
            raise ValueError(
                INVALID_OPTION.format(var='content_type', opts=list(property_types.keys()))
            )
        t = property_types[content_type]
        return ScalarSequence(java_handler(self._session.createSequence, [t, name]))

    def create_map(self, key_type: str, value_type: str, name: Optional[str] = None) -> PgxMap:
        """Create a map.

        Possible types are:
        ['integer','long','double','boolean','string','vertex','edge',
        'local_date','time','timestamp','time_with_timezone','timestamp_with_timezone']

        :param key_type:  Property type of the keys that are going to be stored inside the map
        :param value_type:  Property type of the values that are going to be stored inside the map
        :param name:  Map name
        :return: A named PgxMap of key content type `key_type` and value content type `value_type`
        """
        if key_type not in property_types:
            raise ValueError(
                INVALID_OPTION.format(var='key_type', opts=list(property_types.keys()))
            )
        elif value_type not in property_types:
            raise ValueError(
                INVALID_OPTION.format(var='value_type', opts=list(property_types.keys()))
            )
        k = property_types[key_type]
        v = property_types[value_type]
        return PgxMap(None, java_handler(self._session.createMap, [k, v, name]))

    def describe_graph_file(self, file_path: str) -> GraphConfig:
        """Describe the graph contained in the file at the given path.

        :param file_path: Graph file path
        :return: The configuration which can be used to load the graph
        """
        java_graph_config = java_handler(self._session.describeGraphFile, [file_path])
        return conversion.graph_config_to_python(java_graph_config)

    def describe_graph_files(self, files_path: str) -> GraphConfig:
        """Describe the graph contained in the files at the given paths.

        :param files_path: Paths to the files
        :return: The configuration which can be used to load the graph
        """
        java_graph_config = java_handler(self._session.describeGraphFiles, [files_path])
        return conversion.graph_config_to_python(java_graph_config)

    def read_graph_as_of(
        self,
        config: GraphConfig,
        meta_data: Optional[GraphMetaData] = None,
        creation_timestamp: Optional[int] = None,
        new_graph_name: Optional[str] = None,
    ) -> PgxGraph:
        """Read a graph and its properties of a specific version (metaData or creationTimestamp)
        into memory.

        The creationTimestamp must be a valid version of the graph.

        :param config: The graph config
        :param meta_data: The metaData object returned by
            get_available_snapshots(GraphConfig) identifying the version
        :param creation_timestamp: The creation timestamp (milliseconds since jan 1st 1970)
            identifying the version to be checked out
        :param new_graph_name: How the graph should be named. If None, a name
            will be generated.
        :return: The PgxGraph object
        """
        if not isinstance(config, GraphConfig):
            raise TypeError(ARG_MUST_BE.format(arg='config', type=GraphConfig.__name__))
        if not isinstance(meta_data, (type(None), GraphMetaData)):
            raise TypeError(ARG_MUST_BE.format(arg='meta_data', type=GraphMetaData.__name__))

        if creation_timestamp is None and meta_data is not None:
            java_pgx_graph = java_handler(
                self._session.readGraphAsOf,
                [config._graph_config, meta_data._graph_meta_data, new_graph_name],
            )
        elif meta_data is None and creation_timestamp is not None:
            java_pgx_graph = java_handler(
                self._session.readGraphAsOf,
                [config._graph_config, creation_timestamp, new_graph_name],
            )
        else:
            raise ValueError(
                "You must specify either a Java 'GraphMetaDataObject' object or a "
                "'creation_timestamp'"
            )
        return PgxGraph(self, java_pgx_graph)

    def read_frame(self) -> PgxGenericFrameReader:
        """Create a new frame reader with which it is possible to parameterize the loading of the
        row frame.

        :return: A frame reader object with which it is possible to parameterize
            the loading
        """
        java_pgx_generic_frame_reader = java_handler(self._session.readFrame, [])
        return PgxGenericFrameReader(java_pgx_generic_frame_reader)

    def vertex_provider_from_frame(
        self,
        provider_name: str,
        frame: PgxFrame,
        vertex_key_column: str = 'id',
        label: Optional[str] = None,
    ) -> VertexFrameDeclaration:
        """Create a vertex provider from a PgxFrame to later build a PgxGraph

        :param provider_name: vertex provider name
        :param frame: PgxFrame to use
        :param vertex_key_column: column to use as keys. Defaults to "id"
        :param label: label to set for the provider. Default to the name of the provider
        :return: the VertexFrameDeclaration object

        .. versionchanged:: 24.1
            Added the ``label`` parameter.
        """
        if not isinstance(provider_name, str):
            raise TypeError(ARG_MUST_BE.format(arg='provider_name', type=str))
        if not isinstance(frame, PgxFrame):
            raise TypeError(ARG_MUST_BE.format(arg='frame', type=PgxFrame))
        if not isinstance(vertex_key_column, str):
            raise TypeError(ARG_MUST_BE.format(arg='vertex_key_column', type=str))

        vertex_provider = VertexFrameDeclaration(provider_name, frame, vertex_key_column, label)
        return vertex_provider

    def edge_provider_from_frame(
        self,
        provider_name: str,
        source_provider: str,
        destination_provider: str,
        frame: PgxFrame,
        source_vertex_column: str = "src",
        destination_vertex_column: str = "dst",
        edge_key_column: Optional[str] = None,
        label: Optional[str] = None,
    ) -> EdgeFrameDeclaration:
        """Create an edge provider from a PgxFrame to later build a PgxGraph

        :param provider_name: edge provider name
        :param source_provider: vertex source provider name
        :param destination_provider: vertex destination provider name
        :param frame: PgxFrame to use
        :param source_vertex_column: column to use as source keys. Defaults to "src"
        :param destination_vertex_column: column to use as destination keys. Defaults to "dst"
        :param edge_key_column: column to use as keys
        :param label: label to set for the provider. Defaults to the name of the provider
        :return: the EdgeFrameDeclaration object

        .. versionchanged:: 24.1
            Added the ``edge_key_column`` parameter.
            Added the ``label`` parameter.
        """
        if not isinstance(provider_name, str):
            raise TypeError(ARG_MUST_BE.format(arg='provider_name', type=str))
        if not isinstance(source_provider, str):
            raise TypeError(ARG_MUST_BE.format(arg='source_provider', type=str))
        if not isinstance(destination_provider, str):
            raise TypeError(ARG_MUST_BE.format(arg='destination_provider', type=str))
        if not isinstance(frame, PgxFrame):
            raise TypeError(ARG_MUST_BE.format(arg='frame', type=PgxFrame))
        if not isinstance(source_vertex_column, str):
            raise TypeError(ARG_MUST_BE.format(arg='source_vertex_column', type=str))
        if not isinstance(destination_vertex_column, str):
            raise TypeError(ARG_MUST_BE.format(arg='destination_vertex_column', type=str))

        edge_provider = EdgeFrameDeclaration(
            provider_name,
            source_provider,
            destination_provider,
            frame,
            source_vertex_column,
            destination_vertex_column,
            edge_key_column,
            label,
        )
        return edge_provider

    def graph_from_frames(
        self,
        graph_name: str,
        vertex_providers: List[VertexFrameDeclaration],
        edge_providers: List[EdgeFrameDeclaration],
        partitioned: bool = True,
        vertex_id_strategy: str = "keys_as_ids",
        edge_id_strategy: str = "keys_as_ids",
    ) -> PgxGraph:
        """Create PgxGraph from vertex providers and edge providers.

        partitioned must be set to True if multiple vertex or edge providers are given

        :param graph_name: graph name
        :param vertex_providers: list of vertex providers
        :param edge_providers: list of edge providers
        :param partitioned: whether the graph is partitioned or not. Defaults to True
        :param vertex_id_strategy: id strategy for generating vertex ids. Possible values are
            ``'keys_as_ids'``, ``'unstable_generated_ids'``, ``'partitioned_ids'``, ``'no_ids'``.
        :param edge_id_strategy: id strategy for generating edge ids. Possible values are
            ``'keys_as_ids'``, ``'unstable_generated_ids'``, ``'partitioned_ids'``, ``'no_ids'``.
        :return: the PgxGraph object

        .. versionchanged:: 24.1
            Added the ``vertex_id_strategy`` parameter.
            Added the ``edge_id_strategy`` parameter.
        """
        if not partitioned:
            warnings.warn(
                "non partitioned graphs are now deprecated since 25.1",
                DeprecationWarning
            )
        if not isinstance(graph_name, str):
            raise TypeError(ARG_MUST_BE.format(arg='graph_name', type=str))
        if len(vertex_providers) > 1 or len(edge_providers) > 1:
            if not partitioned:
                raise ValueError(
                    ARG_MUST_BE_REASON.format(
                        arg='partitioned',
                        value='True',
                        cause='Multiple vertex providers or '
                        'edge providers have been ' + 'provided',
                    )
                )
        if not isinstance(partitioned, bool):
            raise TypeError(ARG_MUST_BE.format(arg='partitioned', type=bool))
        java_graph_from_frames_creator = java_handler(
            self._session.createGraphFromFrames, [graph_name]
        )
        java_handler(java_graph_from_frames_creator.partitioned, [partitioned])
        if vertex_id_strategy in id_strategies:
            java_id_strategy = id_strategies[vertex_id_strategy]
            java_handler(java_graph_from_frames_creator.vertexIdStrategy, [java_id_strategy])
        else:
            raise ValueError(
                INVALID_OPTION.format(
                    var='vertex_id_strategy', opts=list(id_strategies.keys())
                )
            )
        if edge_id_strategy in id_strategies:
            java_id_strategy = id_strategies[vertex_id_strategy]
            java_handler(java_graph_from_frames_creator.edgeIdStrategy, [java_id_strategy])
        else:
            raise ValueError(
                INVALID_OPTION.format(
                    var='edge_id_strategy', opts=list(id_strategies.keys())
                )
            )
        for vertex_provider in vertex_providers:
            if not isinstance(vertex_provider, VertexFrameDeclaration):
                raise TypeError(
                    ARG_MUST_BE.format(arg='vertex_provider', type=VertexFrameDeclaration)
                )
            java_vertex_table_from_frames_creator = java_handler(
                java_graph_from_frames_creator.vertexProvider,
                [vertex_provider.provider_name, vertex_provider.frame._frame],
            )
            java_handler(
                java_vertex_table_from_frames_creator.vertexKeyColumn,
                [vertex_provider.vertex_key_column],
            )
            java_handler(
                java_vertex_table_from_frames_creator.label,
                [vertex_provider.label],
            )
        for edge_provider in edge_providers:
            if not isinstance(edge_provider, EdgeFrameDeclaration):
                raise TypeError(
                    ARG_MUST_BE.format(arg='edge_provider', type=VertexFrameDeclaration)
                )
            java_edge_table_from_frames_creator = java_handler(
                java_graph_from_frames_creator.edgeProvider,
                [
                    edge_provider.provider_name,
                    edge_provider.source_provider,
                    edge_provider.destination_provider,
                    edge_provider.frame._frame,
                ],
            )
            java_handler(
                java_edge_table_from_frames_creator.sourceVertexKeyColumn,
                [edge_provider.source_vertex_column],
            )
            java_handler(
                java_edge_table_from_frames_creator.destinationVertexKeyColumn,
                [edge_provider.destination_vertex_column],
            )
            java_handler(
                java_edge_table_from_frames_creator.edgeKeyColumn,
                [edge_provider.edge_key_column],
            )
            java_handler(
                java_edge_table_from_frames_creator.label,
                [edge_provider.label],
            )
        java_graph = java_handler(java_graph_from_frames_creator.create, [])
        return PgxGraph(self._session, java_graph)

    def run_concurrently(self, async_request=None):  # noqa: D102
        raise NotImplementedError

    def get_execution_environment(self):
        """Get the execution environment for this session.

        :return: the execution environment
        """
        java_env = java_handler(self._session.getExecutionEnvironment, [])
        return ExecutionEnvironment(java_env, self)

    def close(self) -> None:
        """Close this session object."""
        java_handler(self._session.close, [])

    def destroy(self) -> None:
        """Destroy this session object."""
        java_handler(self._session.destroy, [])

    def set_session_idle_timeout(self, idle_timeout: int, unit: str) -> None:
        """Update the idle timeout for the current session."""
        if unit not in time_units:
            raise ValueError(INVALID_OPTION.format(var='unit', opts=list(time_units.keys())))
        unit = time_units[unit]
        java_handler(self._session.setSessionIdleTimeout, [idle_timeout, unit])

    def __repr__(self) -> str:
        return "{}(id: {}, name: {})".format(self.__class__.__name__, self.id, self.source)

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> NoReturn:
        raise TypeError(UNHASHABLE_TYPE.format(type_name=self.__class__))
