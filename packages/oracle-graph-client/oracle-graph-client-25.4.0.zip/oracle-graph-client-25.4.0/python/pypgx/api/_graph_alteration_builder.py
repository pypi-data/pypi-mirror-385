#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from typing import cast, List, Optional, Tuple, Union, TYPE_CHECKING

from pypgx.api._graph_property_config import GraphPropertyConfig
from pypgx._utils.error_handling import java_handler
from pypgx._utils.error_messages import ARG_MUST_BE, INVALID_OPTION
from pypgx._utils.pgx_types import (
    id_types,
    property_types
)

if TYPE_CHECKING:
    # Don't import at runtime, to avoid circular imports.
    from pypgx.api._pgx_graph import PgxGraph
    from pypgx.api._pgx_session import PgxSession


class GraphAlterationBuilder:
    """Builder to describe the alterations (graph schema modification) to perform to a graph.

    It is for example possible to add or remove vertex and edge providers.
    """

    _java_class = "oracle.pgx.api.graphalteration.GraphAlterationBuilder"

    def __init__(self, java_graph_alteration_builder, session: "PgxSession") -> None:
        self._graph_alteration_builder = java_graph_alteration_builder
        self._session = session

    def set_data_source_version(self, data_source_version: str) -> None:
        """Set the version information for the built graph or snapshot.

        :param data_source_version: the version information.
        """
        java_handler(self._graph_alteration_builder.setDataSourceVersion, [data_source_version])

    def cascade_edge_provider_removals(
        self, cascade_edge_provider_removals: bool
    ) -> "GraphAlterationBuilder":
        """Specify if the edge providers associated to a vertex provider
        (the vertex provider is either the source or destination provider for that edge provider)
        being removed should be automatically removed too or not.
        By default, edge providers are not automatically removed whenever an associated vertex
        is removed. In that setting, if the associated edge providers are not specifically removed,
        an exception will be thrown to indicate that issue.

        :param cascade_edge_provider_removals: whether or not to automatically
                remove associated edge providers of removed vertex providers.
        :returns: a GraphAlterationBuilder instance with new changes.
        """
        graph_builder = java_handler(
            self._graph_alteration_builder.cascadeEdgeProviderRemovals,
            [cascade_edge_provider_removals],
        )
        self._graph_alteration_builder = graph_builder
        return self

    def add_vertex_provider(self, path_to_vertex_provider_config: str) -> "GraphAlterationBuilder":
        """Add a vertex provider for which the configuration is in a file at the specified path.

        :param path_to_vertex_provider_config: the path to the JSON configuration
                of the vertex provider.
        :returns: a GraphAlterationBuilder instance with the added vertex provider.
        """
        graph_builder = java_handler(
            self._graph_alteration_builder.addVertexProvider, [path_to_vertex_provider_config]
        )
        self._graph_alteration_builder = graph_builder
        return self

    def add_empty_vertex_provider(
            self, provider_name: str, label: Optional[str] = None, key_type: Optional[str] = None,
            key_column: Optional[Union[int, str]] = None, create_key_mapping: Optional[bool] = None,
            properties: Optional[
                List[Union[Tuple[str, str], Tuple[str, str, int], GraphPropertyConfig]]
            ] = None
    ) -> None:
        """Add an empty vertex provider

        :param provider_name: the name of the vertex provider to add
        :param label: the label to associate to the provider
        :param key_type: the key type
        :param key_column: the key column name or index
        :param create_key_mapping: boolean indicating if the provider key mapping should be created
        :param properties: the property configurations, these can either of the following forms:
            a length 2 tuple (name, type), a length 3 tuple (name, type, dimension)
            or a GraphPropertyConfig object
        :return:
        """
        vertex_provider_builder = java_handler(
            self._graph_alteration_builder.addEmptyVertexProvider,
            [provider_name]
        )
        if label is not None:
            java_handler(vertex_provider_builder.setLabel, [label])
        if key_type is not None:
            if key_type in id_types:
                java_type = id_types[key_type]
            else:
                raise ValueError(
                    INVALID_OPTION.format(var='type',
                                          opts=[*id_types])
                )
            java_handler(vertex_provider_builder.setKeyType, [java_type])
        if key_column is not None:
            java_handler(vertex_provider_builder.setKeyColumn, [key_column])
        if create_key_mapping is not None:
            java_handler(vertex_provider_builder.createKeyMapping, [create_key_mapping])
        if properties is not None:
            for property in properties:
                if isinstance(property, tuple):
                    name = property[0]
                    property_type = property[1]
                    if property_type in property_types:
                        java_property_type = property_types[property_type]
                    else:
                        raise ValueError(
                            INVALID_OPTION.format(var='property_type',
                                                  opts=[*property_types])
                        )
                    if len(property) == 2:
                        prop_args = [name, java_property_type]
                    elif len(property) == 3:
                        casted_property = cast(Tuple[str, str, int], property)
                        dimension = casted_property[2]
                        prop_args = [name, java_property_type, dimension]
                    else:
                        raise ValueError(
                            INVALID_OPTION.format(var='property tuple',
                                                  opts="[('name', 'property_type'), ('name', "
                                                       + "'property_type', dimension)]")
                        )
                elif isinstance(property, GraphPropertyConfig):
                    prop_args = [property._graph_property_config]
                else:
                    raise TypeError(
                        ARG_MUST_BE.format(arg='property',
                                           type='tuple or GraphPropertyConfig')
                    )
                java_handler(vertex_provider_builder.addProperty, prop_args)

    def remove_vertex_provider(self, vertex_provider_name: str) -> "GraphAlterationBuilder":
        """Remove the vertex provider that has the given name.
        Also removes the associated edge providers if True was specified when calling
        `cascade_edge_provider_removals(boolean)`.

        :param vertex_provider_name: the name of the provider to remove.
        :returns: a GraphAlterationBuilder instance with the vertex_provider removed.
        """
        graph_builder = java_handler(
            self._graph_alteration_builder.removeVertexProvider, [vertex_provider_name]
        )
        self._graph_alteration_builder = graph_builder
        return self

    def add_edge_provider(self, path_to_edge_provider_config: str) -> "GraphAlterationBuilder":
        """Add an edge provider for which the configuration is in a file at the specified path.

        :param path_to_edge_provider_config: the path to the JSON configuration of the edge provider
        :returns: a GraphAlterationBuilder instance containing the added edge provider.
        """
        graph_builder = java_handler(
            self._graph_alteration_builder.addEdgeProvider, [path_to_edge_provider_config]
        )
        self._graph_alteration_builder = graph_builder
        return self

    def add_empty_edge_provider(
        self, provider_name: str, source_provider: str, dest_provider: str,
        label: Optional[str] = None, key_type: Optional[str] = None,
        key_column: Optional[Union[int, str]] = None, create_key_mapping: Optional[bool] = None,
        properties: Optional[
            List[Union[Tuple[str, str], Tuple[str, str, int], GraphPropertyConfig]]
        ] = None
    ) -> None:
        """Add an empty edge provider

        :param provider_name: the name of the edge provider to add
        :param source_provider: the name of the vertex provider for the source of the edges
        :param dest_provider: the name of the vertex provider for the destination of the edges
        :param label: the label to associate to the provider
        :param key_type: the key type
        :param key_column: the key column name or index
        :param create_key_mapping: boolean indicating if the provider key mapping should be created
        :param properties: the property configurations, these can either of the following forms:
            a length 2 tuple (name, type), a length 3 tuple (name, type, dimension)
            or a GraphPropertyConfig object
        :return:
        """
        edge_provider_builder = java_handler(
            self._graph_alteration_builder.addEmptyEdgeProvider,
            [provider_name, source_provider, dest_provider]
        )
        if label is not None:
            java_handler(edge_provider_builder.setLabel, [label])
        if key_type is not None:
            if key_type in id_types:
                java_type = id_types[key_type]
            else:
                raise ValueError(
                    INVALID_OPTION.format(var='type',
                                          opts=[*id_types])
                )
            java_handler(edge_provider_builder.setKeyType, [java_type])
        if key_column is not None:
            java_handler(edge_provider_builder.setKeyColumn, [key_column])
        if create_key_mapping is not None:
            java_handler(edge_provider_builder.createKeyMapping, [create_key_mapping])
        if properties is not None:
            for property in properties:
                if isinstance(property, tuple):
                    name = property[0]
                    property_type = property[1]
                    if property_type in property_types:
                        java_property_type = property_types[property_type]
                    else:
                        raise ValueError(
                            INVALID_OPTION.format(var='property_type',
                                                  opts=[*property_types])
                        )
                    if len(property) == 2:
                        prop_args = [name, java_property_type]
                    elif len(property) == 3:
                        casted_property = cast(Tuple[str, str, int], property)
                        dimension = casted_property[2]
                        prop_args = [name, java_property_type, dimension]
                    else:
                        raise ValueError(
                            INVALID_OPTION.format(var='property tuple',
                                                  opts="[('name', 'property_type'), ('name', "
                                                       + "'property_type', dimension)]")
                        )
                elif isinstance(property, GraphPropertyConfig):
                    prop_args = [property._graph_property_config]
                else:
                    raise TypeError(
                        ARG_MUST_BE.format(arg='property',
                                           type='tuple or GraphPropertyConfig')
                    )
                java_handler(edge_provider_builder.addProperty, prop_args)

    def remove_edge_provider(self, edge_provider_name: str) -> "GraphAlterationBuilder":
        """Remove the edge provider that has the given name.

        :param edge_provider_name: the name of the provider to remove.
        :returns: a GraphAlterationBuilder instance with the edge_provider removed.
        """
        graph_builder = java_handler(
            self._graph_alteration_builder.removeEdgeProvider, [edge_provider_name]
        )
        self._graph_alteration_builder = graph_builder
        return self

    def build(self, new_graph_name: Optional[str] = None) -> "PgxGraph":
        """Create a new graph that is the result of the alteration of the current graph.

        :param new_graph_name: name of the new graph to create.
        :returns: a PgxGraph instance of the current alteration builder.
        """
        from pypgx.api._pgx_graph import PgxGraph  # need to import here to avoid import loop

        java_graph = java_handler(self._graph_alteration_builder.build, [new_graph_name])
        return PgxGraph(self._session, java_graph)

    def build_new_snapshot(self) -> "PgxGraph":
        """Create a new snapshot for the current graph that is the result of
        the alteration of the current snapshot.

        :returns: a PgxGraph instance of the current alteration builder.
        """
        from pypgx.api._pgx_graph import PgxGraph  # need to import here to avoid import loop

        java_graph = java_handler(self._graph_alteration_builder.buildNewSnapshot, [])
        return PgxGraph(self._session, java_graph)
