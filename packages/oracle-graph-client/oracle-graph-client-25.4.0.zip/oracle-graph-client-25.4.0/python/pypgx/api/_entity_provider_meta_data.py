#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from jnius import autoclass

from pypgx.api._key_column import KeyColumnDescriptor
from pypgx.api._property_meta_data import PropertyMetaData
from pypgx._utils.error_handling import java_handler
from pypgx._utils.error_messages import (
    INVALID_OPTION,
    UNHASHABLE_TYPE
)
from pypgx._utils import conversion
from pypgx._utils.pgx_types import id_types
from typing import List, NoReturn, Set

_JavaEntityProviderMetaData = autoclass('oracle.pgx.api.EntityProviderMetaData')
_JavaEdgeProviderMetaData = autoclass('oracle.pgx.api.EdgeProviderMetaData')
_JavaVertexProviderMetaData = autoclass('oracle.pgx.api.VertexProviderMetaData')


class EntityProviderMetaData:
    """Abstraction of the meta information about an edge or vertex provider."""

    _java_class = 'oracle.pgx.api.EntityProviderMetaData'

    def __init__(
            self,
            java_entity_provider_meta_data,
    ) -> None:
        """Initialize this EntityProviderMetaData object.

        :param java_entity_provider_meta_data: A java object of type 'EntityProviderMetaData'
        """
        self._entity_provider_meta_data = java_entity_provider_meta_data

    def get_id_type(self) -> str:
        """Get the ID type of this entity table.

        :return: the id type.
        """
        java_id_type = java_handler(self._entity_provider_meta_data.getIdType, [])
        id_type = conversion.enum_to_python_str(java_id_type)
        return id_type

    def get_key_columns(self) -> List[KeyColumnDescriptor]:
        """Get the list of key column of this entity table.

        :return: list of key columns
        """
        java_key_columns = java_handler(self._entity_provider_meta_data.getKeyColumns, [])
        return list(map(KeyColumnDescriptor, java_key_columns))

    def get_labels(self) -> Set[str]:
        """Return the set of provider labels ("type labels").

        :return: the set of provider labels
        """
        java_set = java_handler(self._entity_provider_meta_data.getLabels, [])
        return conversion.set_to_python(java_set)

    def get_properties(self) -> List[PropertyMetaData]:
        """Return a list containing the metadata for the properties associated to this provider.

        :return: the list of the properties' metadata
        """
        java_list = java_handler(self._entity_provider_meta_data.getProperties, [])
        return [PropertyMetaData._internal_init(prop) for prop in java_list]

    def get_name(self) -> str:
        """Get the name of this entity table.

        :return: the table name
        """
        return java_handler(self._entity_provider_meta_data.getName, [])

    def set_id_type(self, id_type: str) -> None:
        """Set the ID type of this entity table.

        :param id_type: the new vertex id type
        """
        if id_type in id_types:
            java_id_type = id_types[id_type]
        else:
            raise ValueError(
                INVALID_OPTION.format(var='id_type', opts=[*id_types])
            )

        java_handler(self._entity_provider_meta_data.setIdType, [java_id_type])

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return java_handler(self._entity_provider_meta_data.equals,
                            [other._entity_provider_meta_data])

    def __repr__(self) -> str:
        return java_handler(self._entity_provider_meta_data.toString, [])

    def __hash__(self) -> NoReturn:
        raise TypeError(UNHASHABLE_TYPE.format(type_name=self.__class__))


class EdgeProviderMetaData(EntityProviderMetaData):
    """Meta information about an edge provider in a PgxGraph"""

    _java_class = 'oracle.pgx.api.EdgeProviderMetaData'

    def __init__(
            self,
            name: str,
            id_type: str,
            directed: bool,
            labels: Set[str],
            properties: List[PropertyMetaData],
            source_vertex_provider_name: str,
            destination_vertex_provider_name: str,
    ) -> None:
        """Initialize this EdgeProviderMetaData object.

        :param name: name of the entity provider
        :param id_type: the ID type of this entity provider
        :param labels: set of labels of the entity provider
        :param properties: list of properties of the entity provider
        :param source_vertex_provider_name: name of the source vertex provider
        :param destination_vertex_provider_name: name of the destination vertex provider
        """
        if id_type in id_types:
            java_id_type = id_types[id_type]
        else:
            raise ValueError(
                INVALID_OPTION.format(var='id_type', opts=[*id_types])
            )
        java_labels = conversion.to_java_set(labels)
        java_properties = conversion.to_java_list([p._property_meta_data for p in properties])
        java_edge_provider_meta_data = java_handler(_JavaEdgeProviderMetaData,
                                                    [name, java_id_type, directed,
                                                     java_labels, java_properties,
                                                     source_vertex_provider_name,
                                                     destination_vertex_provider_name])
        super().__init__(java_edge_provider_meta_data)

    @classmethod
    def _internal_init(cls, java_edge_provider_meta_data) -> "EdgeProviderMetaData":
        """For internal use only!
        Initialize this EdgeProviderMetaData object.

        :param java_edge_provider_meta_data: A java object of type 'EdgeProviderMetaData'
        """
        self = cls.__new__(cls)
        self._entity_provider_meta_data = java_edge_provider_meta_data
        return self

    def get_source_vertex_provider_name(self) -> str:
        """Return the name of the vertex provider for the sources of the edges of this edge provider.

        :return: the name of the vertex provider
        """
        return java_handler(self._entity_provider_meta_data.getSourceVertexProviderName, [])

    def get_destination_vertex_provider_name(self) -> str:
        """Return the name of the vertex provider for the destinations of the edges of this edge provider.

        :return: the name of the vertex provider
        """
        return java_handler(self._entity_provider_meta_data.getDestinationVertexProviderName, [])

    def is_directed(self) -> bool:
        """Indicate whether the edge table is directed.

        :return: whether the edge table is directed
        """
        return java_handler(self._entity_provider_meta_data.isDirected, [])

    def set_directed(self, directed: bool) -> None:
        """Set whether the edge table is directed.

        :param directed: A Boolean value
        """
        return java_handler(self._entity_provider_meta_data.setDirected, [directed])


class VertexProviderMetaData(EntityProviderMetaData):
    """Meta information about a vertex provider in a PgxGraph"""

    _java_class = 'oracle.pgx.api.VertexProviderMetaData'

    def __init__(
            self,
            name: str,
            id_type: str,
            labels: Set[str],
            properties: List[PropertyMetaData],
            edge_provider_names_where_source: Set[str],
            edge_provider_names_where_destination: Set[str],
    ) -> None:
        """Initialize this VertexProviderMetaData object.

        :param id_type: the ID type of this entity provider
        :param name: name of the entity provider
        :param labels: set of labels of the entity provider
        :param properties: list of properties of the entity provider
        :param edge_provider_names_where_source: set of provider names where this provider is
        the source
        :param edge_provider_names_where_destination: set of provider names where this provider is
        the destination
        """
        if id_type in id_types:
            java_id_type = id_types[id_type]
        else:
            raise ValueError(
                INVALID_OPTION.format(var='id_type', opts=[*id_types])
            )
        java_labels = conversion.to_java_set(labels)
        java_properties = conversion.to_java_list([p._property_meta_data for p in properties])
        java_sources = conversion.to_java_set(edge_provider_names_where_source)
        java_destinations = conversion.to_java_set(edge_provider_names_where_destination)
        java_vertex_provider_meta_data = java_handler(_JavaVertexProviderMetaData,
                                                      [name, java_id_type, java_labels,
                                                       java_properties,
                                                       java_sources, java_destinations])
        super().__init__(java_vertex_provider_meta_data)

    @classmethod
    def _internal_init(cls, java_vertex_provider_meta_data) -> "VertexProviderMetaData":
        """For internal use only!
        Initialize this VertexProviderMetaData object.

        :param java_vertex_provider_meta_data: A java object of type 'VertexProviderMetaData'
        """
        self = cls.__new__(cls)
        self._entity_provider_meta_data = java_vertex_provider_meta_data
        return self

    def get_edge_provider_names_where_source(self) -> Set[str]:
        """Return the list of edge providers for which this vertex provider is the source provider.

        :return: the list of edge providers
        """
        java_set = java_handler(self._entity_provider_meta_data.getEdgeProviderNamesWhereSource, [])
        return conversion.set_to_python(java_set)

    def get_edge_provider_names_where_destination(self) -> Set[str]:
        """Return the list of edge providers for which this vertex provider is the destination provider.

        :return: the list of edge providers
        """
        java_set = java_handler(
            self._entity_provider_meta_data.getEdgeProviderNamesWhereDestination, []
        )
        return conversion.set_to_python(java_set)
