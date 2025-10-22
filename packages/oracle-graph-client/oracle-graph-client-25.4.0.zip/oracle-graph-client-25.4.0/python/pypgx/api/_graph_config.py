#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

import json
from typing import Dict, List, Optional, Any

import pypgx._utils.pgx_types as types
from pypgx._utils import conversion
from pypgx._utils.error_handling import java_handler
from pypgx.api._graph_property_config import GraphPropertyConfig
from jnius import autoclass


class GraphConfig:
    """A class for representing graph configurations.

    :ivar bool is_file_format: whether the format is a file-based format
    :ivar bool has_vertices_and_edges_separated_file_format: whether given format has vertices
        and edges separated in different files
    :ivar bool is_single_file_format: whether given format has vertices and edges combined
        in same file
    :ivar bool is_multiple_file_format: whether given format has vertices and edges separated
        in different files
    :ivar bool supports_edge_label: whether given format supports edge label
    :ivar bool supports_vertex_labels: whether given format supports vertex labels
    :ivar bool supports_vector_properties: whether given format supports vector properties
    :ivar bool supports_property_column: whether given format supports property columns
    :ivar str name: the graph name of this graph configuration. Note: for file-based graph
        configurations, this is the file name of the URI this configuration points to.
    :ivar int num_vertex_properties: the number of vertex properties in this graph configuration
    :ivar int num_edge_properties: the number of edge properties in this graph configuration
    :ivar str format: Graph data format. The possible formats are in the table below.

    ==============   ======================================================
    Format string    Description
    ==============   ======================================================
    PGB              PGX Binary File Format (formerly EBIN)
    EDGE_LIST        Edge List file format
    TWO_TABLES       Two-Tables format (vertices, edges)
    ADJ_LIST         Adjacency List File Format
    FLAT_FILE        Flat File Format
    GRAPHML          GraphML File Format
    PG               Property Graph (PG) Database Format
    RDF              Resource Description Framework (RDF) Database Format
    CSV              Comma-Separated Values (CSV) Format
    ==============   ======================================================
    """

    _java_class = "oracle.pgx.config.GraphConfig"

    def __init__(self, java_graph_config) -> None:

        self._graph_config = java_graph_config
        self._graph_config_field = autoclass(f"{self._graph_config.getClass().getName()}$Field")
        self._config_dict = json.loads(java_graph_config.toString())
        format_java = java_graph_config.getFormat()

        # The following attributes do not exist for partitioned graphs. Therefore only access them
        # if 'java_graph_config' does not belong to a partitioned graph.
        if format_java is not None:
            self.format = format_java.toString()
            self.is_file_format = java_graph_config.isFileFormat()
            self.has_vertices_and_edges_separated_file_format = (
                java_graph_config.hasVerticesAndEdgesSeparatedFileFormat()
            )
            self.is_single_file_format = java_graph_config.isSingleFileFormat()
            self.is_multiple_file_format = java_graph_config.isMultipleFileFormat()
            self.supports_edge_label = java_graph_config.supportsEdgeLabel()
            self.supports_vertex_labels = java_graph_config.supportsVertexLabels()
            self.supports_vector_properties = java_graph_config.supportsVectorProperties()
            self.supports_property_column = java_graph_config.supportsPropertyColumn()
        else:
            self.format = None
            self.is_file_format = None
            self.has_vertices_and_edges_separated_file_format = None
            self.is_single_file_format = None
            self.is_multiple_file_format = None
            self.supports_edge_label = None
            self.supports_vertex_labels = None
            self.supports_vector_properties = None
            self.supports_property_column = None

        self.name = java_graph_config.getName()
        self.num_vertex_properties = java_graph_config.numNodeProperties()
        self.num_edge_properties = java_graph_config.numEdgeProperties()

    @property
    def vertex_props(self) -> List[str]:
        """Get the vertex property names as a list."""
        props = []
        prop_list = java_handler(self._graph_config.getVertexProps, [])
        for prop in prop_list:
            props.append(prop.toString())
        return props

    @property
    def edge_props(self) -> List[str]:
        """Get the edge property names as a list."""
        props = []
        prop_list = java_handler(self._graph_config.getEdgeProps, [])
        for prop in prop_list:
            props.append(prop.toString())
        return props

    @property
    def vertex_property_types(self) -> Dict[str, str]:
        """Get the vertex property types as a dictionary.

        :return: dict mapping property names to their types

        """
        prop_types = {}
        prop_map = java_handler(self._graph_config.getVertexPropertyTypes, [])
        for prop_name in prop_map.keySet():
            prop_types[prop_name] = prop_map.get(prop_name).toString()
        return prop_types

    @property
    def edge_property_types(self) -> Dict[str, str]:
        """Get the edge property types as a dictionary.

        :return: dict mapping property names to their types

        """
        prop_types = {}
        prop_map = java_handler(self._graph_config.getEdgePropertyTypes, [])
        for prop_name in prop_map.keySet():
            prop_types[prop_name] = prop_map.get(prop_name).toString()
        return prop_types

    @property
    def vertex_id_type(self) -> Optional[str]:
        """Get the type of the vertex ID.

        :return: a str indicating the type of the vertex ID,
            one of "integer", "long" or "string", or None

        """
        v_type = self._graph_config.getVertexIdType()
        if v_type is not None:
            return v_type.toString()
        else:
            return None

    @property
    def edge_id_type(self) -> Optional[str]:
        """Get the type of the edge ID.

        :return: a str indicating the type of the vertex ID,
            one of "integer", "long" or "string", or None

        """
        e_type = self._graph_config.getEdgeIdType()
        if e_type is not None:
            return e_type.toString()
        else:
            return None

    def get_vertex_props(self) -> List[GraphPropertyConfig]:
        """Get the vertex properties"""
        prop_list = java_handler(self._graph_config.getVertexProps, [])
        return conversion.collection_to_python_list(prop_list)

    def get_edge_props(self) -> List[GraphPropertyConfig]:
        """Get the edge properties"""
        prop_list = java_handler(self._graph_config.getEdgeProps, [])
        return conversion.collection_to_python_list(prop_list)

    def get_array_compaction_threshold(self) -> float:
        """Get the array compaction threshold.

        For graphs optimized for updates, the value corresponds to the
        ratio at which the delta-logs are compacted into new arrays.

        :return: the compaction threshold
        """
        return java_handler(self._graph_config.getArrayCompactionThreshold, [])

    def get_attributes(self) -> Dict[Any, Any]:
        """Get the specific additional attributes needed to read/write the graph data.

        :return: the map of attributes
        """
        attr_map = java_handler(self._graph_config.getAttributes, [])

        return conversion.map_to_python(attr_map)

    def get_edge_property_default(self, i: int) -> Any:
        """Get the default value of an edge property by index.

        :param i: the 0-based index of the edge property
        :return: the default value of the edge property
        """
        default = java_handler(self._graph_config.getEdgePropertyDefault, [i])
        return conversion.property_to_python(default, self.get_edge_property_type(i), None)

    def get_edge_property_dimension(self, i: int) -> int:
        """Get the dimension of an edge property by index.

        :param i: the 0-based index of the edge property
        :return: the default value of the edge property
        """
        return java_handler(self._graph_config.getEdgePropertyDimension, [i])

    def get_edge_property_name(self, i: int) -> str:
        """Get the name of an edge property by index.

        :param i: the 0-based index of the edge property
        :return: the name of the edge property
        """
        return java_handler(self._graph_config.getEdgePropertyName, [i])

    def get_edge_property_type(self, i: int) -> str:
        """Get the type of edge property by index.

        :param i: the 0-based index of the edge property
        :return: the type of the edge property,
                 can be "integer", "long", "string", etc..
        """
        e_type = java_handler(self._graph_config.getEdgePropertyType, [i])
        return conversion.enum_to_python_str(e_type)

    def get_error_handling(self) -> Dict[str, Any]:
        """Get the error handling configuration of this graph configuration.

        :return: the error handling configuration
        """
        handling = java_handler(self._graph_config.getErrorHandling, [])
        return conversion.config_to_python_dict(handling)

    def get_external_stores(self) -> List[Dict[str, Any]]:
        """Get the list of external stores.

        :return: the list of external stores
        """
        stores = java_handler(self._graph_config.getExternalStores, [])
        return conversion.collection_to_python_list(stores)

    def get_keystore_alias(self) -> Optional[str]:
        """Get the keystore alias.

        :return: the keystore alias or None if underlying format does not require a keystore
        """
        return java_handler(self._graph_config.getKeystoreAlias, [])

    def get_loading_options(self) -> Dict[str, Any]:
        """Get the loading configuration of this graph configuration.

        :return: the loading configuration, as a dict
        """

        options = java_handler(self._graph_config.getLoadingOptions, [])
        return conversion.config_to_python_dict(options)

    def get_local_date_format(self) -> List[str]:
        """Get the list of date formats to use when loading and storing local_date properties.

        Please see `DateTimeFormatter <https://docs.oracle.com/javase/8/docs/api/java\
        /time/format/DateTimeFormatter.html>`_ for a documentation of the format string.

        :return: the date format
        """
        return conversion.collection_to_python_list(
            java_handler(self._graph_config.getLocalDateFormat, [])
        )

    def get_vertex_property_default(self, i: int) -> Any:
        """Get the default value of a vertex property by index.

        :param i: the 0-based index of the vertex property
        :return: the default value of the vertex property
        """
        default = java_handler(self._graph_config.getNodePropertyDefault, [i])
        return conversion.property_to_python(default, self.get_vertex_property_type(i), None)

    def get_vertex_property_dimension(self, i: int) -> int:
        """Get the dimension of a vertex property by index.

        :param i: the 0-based index of the vertex property
        :return: the dimension of the vertex property
        """
        return java_handler(self._graph_config.getNodePropertyDimension, [i])

    def get_vertex_property_name(self, i: int) -> str:
        """Get the name of a vertex property by index.

        :param i: the 0-based index of the vertex property
        :return: the name of the vertex property
        """
        return java_handler(self._graph_config.getNodePropertyName, [i])

    def get_vertex_property_type(self, i: int) -> str:
        """Get the type of vertex property by index.

        :param i: the 0-based index of the vertex property
        :return: the type of the vertex property,
                 can be "integer", "long", "string", etc..
        """
        n_type = java_handler(self._graph_config.getNodePropertyType, [i])
        return conversion.enum_to_python_str(n_type)

    def get_optimized_for(self) -> str:
        """Indicate if the graph is optimized for reads or updates.

        :return: if the graph is optimized for reads ("read") or updates ("updates")
        """
        opt_for = java_handler(self._graph_config.getOptimizedFor, [])
        return conversion.enum_to_python_str(opt_for)

    def get_partition_while_loading(self) -> str:
        """Indicate if the graph should be partitioned during loading.

        :return: "by_label" if the graph should be partitioned during loading, "no" otherwise
        """
        part_while = java_handler(self._graph_config.getPartitionWhileLoading, [])
        return conversion.enum_to_python_str(part_while) if part_while is not None else 'no'

    def get_time_format(self) -> List[str]:
        """Get the list of time formats to use when loading and storing time properties.

        Please see `DateTimeFormatter <https://docs.oracle.com/javase/8/docs/api/java\
        /time/format/DateTimeFormatter.html>`_ for a documentation of the format string.

        :return: the time format
        """
        return conversion.collection_to_python_list(
            java_handler(self._graph_config.getTimeFormat, [])
        )

    def get_time_with_timezone_format(self) -> List[str]:
        """Get the list of time with timezone formats to use when loading and storing time with
        timezone properties.

        Please see `DateTimeFormatter <https://docs.oracle.com/javase/8/docs/api/java\
        /time/format/DateTimeFormatter.html>`_ for a documentation of the format string.

        :return: the time with timezone format
        """
        return conversion.collection_to_python_list(
            java_handler(self._graph_config.getTimeWithTimezoneFormat, []))

    def get_timestamp_format(self) -> List[str]:
        """Get the list of timestamp formats to use when loading and storing timestamp properties.

        Please see `DateTimeFormatter <https://docs.oracle.com/javase/8/docs/api/java\
        /time/format/DateTimeFormatter.html>`_ for a documentation of the format string.

        :return: the timestamp format
        """
        return conversion.collection_to_python_list(
            java_handler(self._graph_config.getTimestampFormat, [])
        )

    def get_timestamp_with_timezone_format(self) -> List[str]:
        """Get the list of timestamp with timezone formats to use when loading and storing
        timestamp with timezone properties.

        Please see `DateTimeFormatter <https://docs.oracle.com/javase/8/docs/api/java\
        /time/format/DateTimeFormatter.html>`_ for a documentation of the format string.

        :return: the timestamp with timezone format
        """
        return conversion.collection_to_python_list(
            java_handler(self._graph_config.getTimestampWithTimezoneFormat, [])
        )

    def get_validated_edge_id_strategy(self) -> str:
        """Validate and return the ID strategy used for edges
        (checking if the strategy is compatible with the rest of the graph configuration).

        :return: the ID strategy that can be used for the edges of the graph,
                 one of "no_ids", "keys_as_ids", "unstable_generated_ids", "partitioned_ids"
        """
        e_strat = java_handler(self._graph_config.getValidatedEdgeIdStrategy, [])

        return conversion.enum_to_python_str(e_strat)

    def get_validated_edge_id_type(self) -> str:
        """Validate and return the ID type used for edges
        (checking if the type is compatible with the rest of the configuration).

        :return: the ID type that can be used for the edges of the graph,
                 can be "integer", "long", "string", etc..
        """
        e_type = java_handler(self._graph_config.getValidatedEdgeIdType, [])
        return conversion.enum_to_python_str(e_type)

    def get_validated_vertex_id_strategy(self) -> str:
        """Validate and return the ID strategy used for vertices
        (checking if the strategy is compatible with the rest of the graph configuration).

        :return: the ID strategy that can be used for the vertices of the graph,
                 one of "no_ids", "keys_as_ids", "unstable_generated_ids", "partitioned_ids"
        """
        v_strat = java_handler(self._graph_config.getValidatedVertexIdStrategy, [])

        return conversion.enum_to_python_str(v_strat)

    def get_validated_vertex_id_type(self) -> str:
        """Validate and return the ID type used for vertices
        (checking if the type is compatible with the rest of the configuration).

        :return: the ID type that can be used for the vertices of the graph,
                 can be "integer", "long", "string", etc..
        """
        v_type = java_handler(self._graph_config.getValidatedVertexIdType, [])
        return conversion.enum_to_python_str(v_type)

    @staticmethod
    def get_value_from_environment(key: str) -> Optional[str]:
        """Look up a value by a key from java properties and the system environment.

        Looks up the provided key first in the java system properties prefixed with
        SYSTEM_PROPERTY_PREFIX and returns the value if present.
        If it is not present, looks it up in the system environment prefixed with
        ENV_VARIABLE_PREFIX and returns this one if present.
        Returns None if the key is neither found in the properties nor in the environment.

        :param key: the key to look up
        :return: the found value or None if the key is not available
        """

        return java_handler(types.graph_config.getValueFromEnvironment, [key])

    def get_values(self) -> Dict[Any, Any]:
        """Return values of class

        :return: values
        """
        return conversion.map_to_python(java_handler(self._graph_config.getValues, []))

    def get_vector_component_delimiter(self) -> str:
        """Get delimiter for the different components of vector properties.

        :return: the delimiter
        """
        return conversion.call_and_convert_to_python(
            self._graph_config, 'getVectorComponentDelimiter'
        )

    def is_edge_label_loading_enabled(self) -> bool:
        """Check if edge label loading is enabled.

        :return: True if edge label loading is enabled, False otherwise.
        """
        return java_handler(self._graph_config.isEdgeLabelLoadingEnabled, [])

    def is_load_edge_keys(self) -> bool:
        """Whether to load edge keys.

        :return: True if we should load the edge keys.
        """
        return java_handler(self._graph_config.isLoadEdgeKeys, [])

    def is_load_vertex_keys(self) -> bool:
        """Whether to load vertex keys.

        :return: True if we should load the vertex keys.
        """
        return java_handler(self._graph_config.isLoadVertexKeys, [])

    def is_vertex_labels_loading_enabled(self) -> bool:
        """Check if vertex labels loading is enabled.

        :return: True if vertex label loading is enabled, False otherwise.
        """
        return java_handler(self._graph_config.isVertexLabelsLoadingEnabled, [])

    def can_serialize(self) -> bool:
        """Get the serializable property of this config.

        :return: True if it is serializable, False otherwise.
        """
        return java_handler(self._graph_config.canSerialize, [])

    def skip_edge_loading(self) -> bool:
        """Whether to skip edge loading.

        :return: True if we should skip edge loading.
        """
        return java_handler(self._graph_config.skipEdgeLoading, [])

    def skip_vertex_loading(self) -> bool:
        """Whether to skip vertex loading.

        :return: True if we should skip vertex loading.
        """
        return java_handler(self._graph_config.skipVertexLoading, [])

    def has_default_value(self, field: str) -> bool:
        """Check if field has a default value.

        :param field: the field
        :return: True, if value for given field is the default value
        """
        if not hasattr(self._graph_config, "hasDefaultValue"):
            # all non-abstract descendent classes of the java GraphConfig implement this method
            raise RuntimeError(
                "The corresponding java Graph Config has no 'hasDefaultValue' method")
        from pypgx._utils.error_messages import INVALID_OPTION

        if field != field.lower():
            raise ValueError(f"Only lowercase spellings of fields are valid (got {field})")
        field = field.upper()
        if not hasattr(self._graph_config_field, field):
            raise ValueError(
                INVALID_OPTION.format(
                    var="type",
                    opts=list(
                        map(
                            lambda attr: attr.lower(),
                            filter(
                                # all uppercase attributes of _graph_config_field are valid fields
                                lambda attr: attr.isupper(),
                                self._graph_config_field.__dict__.keys(),
                            )
                        ),
                    )
                )
            )
        java_field = getattr(self._graph_config_field, field)
        return bool(java_handler(self._graph_config.hasDefaultValue, [java_field]))

    def is_empty(self) -> bool:
        """Check if it's empty.

        :return: True if it's empty
        """
        if not hasattr(self._graph_config, "isEmpty"):
            # all non-abstract descendent classes of the java GraphConfig implement this method
            raise RuntimeError("The corresponding java Graph Config has no 'isEmpty' method")
        return bool(java_handler(self._graph_config.isEmpty, []))

    def get_config_fields(self) -> List[str]:
        """Get the fields of the graph config.

        :return: the fields of the graph config
        """
        if not hasattr(self._graph_config, "getConfigFields"):
            # all non-abstract descendent classes of the java GraphConfig implement this method
            raise RuntimeError(
                "The corresponding java Graph Config has no 'getConfigFields' method")
        fields = java_handler(self._graph_config.getConfigFields, [])
        return [conversion.enum_to_python_str(field) for field in fields]

    def get_edge_id_strategy(self) -> Optional[str]:
        """Get the ID strategy that should be used for the edges of this graph.
        If not specified (or set to null), the strategy will be determined during
        loading or using a default value.

        :return: the edge ID strategy
        """
        if not hasattr(self._graph_config, "getEdgeIdStrategy"):
            # all non-abstract descendent classes of the java GraphConfig implement this method
            raise RuntimeError(
                "The corresponding java Graph Config has no 'getEdgeIdStrategy' method")
        strategy = java_handler(self._graph_config.getEdgeIdStrategy, [])
        if strategy is not None:
            strategy = conversion.enum_to_python_str(strategy)
        return strategy

    def get_vertex_id_strategy(self) -> Optional[str]:
        """Get the ID strategy that should be used for the vertices of this graph.
        If not specified (or set to null), the strategy will be automatically detected.

        :return: the vertex id strategy
        """
        if not hasattr(self._graph_config, "getVertexIdStrategy"):
            # all non-abstract descendent classes of the java GraphConfig implement this method
            raise RuntimeError(
                "The corresponding java Graph Config has no 'getVertexIdStrategy' method")
        strategy = java_handler(self._graph_config.getVertexIdStrategy, [])
        if strategy is not None:
            strategy = conversion.enum_to_python_str(strategy)
        return strategy

    def get_values_without_defaults(self) -> Dict[Any, Any]:
        """Return values without defaults.

        :return: values
        """
        if not hasattr(self._graph_config, "getValuesWithoutDefaults"):
            # all non-abstract descendent classes of the java GraphConfig implement this method
            raise RuntimeError(
                "The corresponding java Graph Config has no 'getValuesWithoutDefaults' method")
        values = java_handler(self._graph_config.getValuesWithoutDefaults, [])
        return conversion.map_to_python(values)

    def get_loading(self) -> Dict[str, Any]:
        """Get the loading-specific configuration.

        :return: the loading-specific configuration
        """
        if not hasattr(self._graph_config, "getLoading"):
            # all non-abstract descendent classes of the java GraphConfig implement this method
            raise RuntimeError("The corresponding java Graph Config has no 'getLoading' method")
        loading = java_handler(self._graph_config.getLoading, [])
        return conversion.config_to_python_dict(loading)

    def get_leftover_values(self) -> Dict[str, Any]:
        """Get the values that do not belong to any field.

        :return: the values that do not belong to any field
        """
        if not hasattr(self._graph_config, "getLeftoverValues"):
            # all non-abstract descendent classes of the java GraphConfig implement this method
            raise RuntimeError(
                "The corresponding java Graph Config has no 'getLeftoverValues' method")
        values = java_handler(self._graph_config.getLeftoverValues, [])
        return conversion.map_to_python(values)

    def __repr__(self) -> str:
        return str(self._graph_config.toString())

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._graph_config.equals(other._graph_config)
