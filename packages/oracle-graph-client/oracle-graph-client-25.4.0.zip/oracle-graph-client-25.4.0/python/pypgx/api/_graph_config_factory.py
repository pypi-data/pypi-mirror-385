#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from jnius import autoclass, cast

from pypgx._utils.error_handling import java_handler
from ._graph_config import GraphConfig
from ._file_graph_config import FileGraphConfig, TwoTablesTextGraphConfig
from ._partitioned_graph_config import PartitionedGraphConfig
from ._rdf_graph_config import RdfGraphConfig
from ._two_tables_rdbms_graph_config import TwoTablesRdbmsGraphConfig
from typing import Any, TypeVar, Type, Generic

_GraphConfig = TypeVar("_GraphConfig", bound=GraphConfig)


class GraphConfigFactory(Generic[_GraphConfig]):
    """A factory class for creating graph configs."""

    _java_class = "oracle.pgx.config.GraphConfigFactory"

    _graph_config_factory_class = autoclass("oracle.pgx.config.GraphConfigFactory")
    _pgx_config_java_class = autoclass("oracle.pgx.config.PgxConfig$Field")

    strict_mode = java_handler(_pgx_config_java_class.STRICT_MODE.getDefaultVal, []) == 1

    def __init__(
        self,
        java_graph_config_factory,
        graph_config_class: Type[_GraphConfig],
    ) -> None:
        """Initialize this factory object.

        :param java_graph_config_factory: A java object of type 'GraphConfigFactory' or one of
        its subclasses.
        :param graph_config_class: A graph config class of type 'GraphConfig'.
        """
        self._graph_config_factory = java_graph_config_factory
        self._graph_config_class = graph_config_class

    @staticmethod
    def init(want_strict_mode: bool = True) -> None:
        """Setter function for the 'strictMode' class variable.

        :param want_strict_mode: A boolean value which will be assigned to 'strictMode'
            (Default value = True)
        """
        GraphConfigFactory.strict_mode = want_strict_mode
        java_handler(GraphConfigFactory._graph_config_factory_class.init, [want_strict_mode])

    @staticmethod
    def for_partitioned() -> "GraphConfigFactory[PartitionedGraphConfig]":
        """Return a new graph config factory to parse partitioned graph config."""
        java_object = java_handler(
            GraphConfigFactory._graph_config_factory_class.forPartitioned, []
        )
        return GraphConfigFactory(
            java_object,
            PartitionedGraphConfig,
        )

    @staticmethod
    def for_any_format() -> "GraphConfigFactory[GraphConfig]":
        """Return a new factory to parse any graph config from various input sources."""
        java_object = java_handler(GraphConfigFactory._graph_config_factory_class.forAnyFormat, [])
        return GraphConfigFactory(java_object, GraphConfig)

    @staticmethod
    def for_file_formats() -> "GraphConfigFactory[FileGraphConfig]":
        """Return a new graph config factory to parse file-based graph configs from various input
        sources.
        """
        java_object = java_handler(
            GraphConfigFactory._graph_config_factory_class.forFileFormats, []
        )
        return GraphConfigFactory(java_object, FileGraphConfig)

    @staticmethod
    def for_two_tables_rdbms() -> "GraphConfigFactory[TwoTablesRdbmsGraphConfig]":
        """Return a new graph config factory to create graph configs targeting the Oracle RDBMS
        database in the two-tables format.
        """
        java_object = java_handler(
            GraphConfigFactory._graph_config_factory_class.forTwoTablesRdbms, []
        )
        return GraphConfigFactory(java_object, TwoTablesRdbmsGraphConfig)

    @staticmethod
    def for_two_tables_text() -> "GraphConfigFactory[TwoTablesTextGraphConfig]":
        """Return a new graph config factory to create graph configs targeting files in the
        two-tables format.
        """
        java_object = java_handler(
            GraphConfigFactory._graph_config_factory_class.forTwoTablesText, []
        )
        return GraphConfigFactory(java_object, TwoTablesTextGraphConfig)

    @staticmethod
    def for_rdf() -> "GraphConfigFactory[RdfGraphConfig]":
        """Return a new RDF graph config factory."""
        java_object = java_handler(GraphConfigFactory._graph_config_factory_class.forRdf, [])
        return GraphConfigFactory(java_object, RdfGraphConfig)

    def _from_java_config(self, java_config: Any) -> _GraphConfig:
        java_config_casted = cast(
            autoclass(self._graph_config_class._java_class), java_config
        )
        return self._graph_config_class(java_config_casted)

    def from_file_path(self, path: str) -> _GraphConfig:
        """Parse a configuration object given as path to a JSON file.

        Relative paths found in JSON are resolved relative to given file.

        :param path: The path to the JSON file
        """
        java_config = java_handler(self._graph_config_factory.fromFilePath, [path])
        return self._from_java_config(java_config)

    def from_json(self, json: str) -> _GraphConfig:
        """Parse a configuration object given a JSON string.

        :param json: The input JSON string
        """
        java_config = java_handler(self._graph_config_factory.fromJson, [json])
        return self._from_java_config(java_config)

    def from_input_stream(self, stream) -> _GraphConfig:
        """Parse a configuration object given an input stream.

        :param stream: A JAVA 'InputStream' object from where to read the configuration
        """
        java_config = java_handler(self._graph_config_factory.fromInputStream, [stream])
        return self._from_java_config(java_config)

    def from_properties(self, properties) -> _GraphConfig:
        """Parse a configuration object from a properties object.

        :param properties: A JAVA 'Properties' object
        """
        java_config = java_handler(self._graph_config_factory.fromProperties, [properties])
        return self._from_java_config(java_config)

    def from_path(self, path: str) -> _GraphConfig:
        """Parse a configuration object given a path.

        :param path: The path from where to parse the configuration.
        """
        java_config = java_handler(self._graph_config_factory.fromPath, [path])
        return self._from_java_config(java_config)

    def __repr__(self) -> str:
        return self._graph_config_factory.toString()

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._graph_config_factory.equals(other._graph_config_factory)
