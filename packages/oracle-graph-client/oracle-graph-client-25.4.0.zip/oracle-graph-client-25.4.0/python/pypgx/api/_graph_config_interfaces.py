#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils.error_handling import java_handler
from pypgx._utils.conversion import enum_to_python_str
from typing import Optional


class DbConnectionConfig:
    """A class for representing the database connection config interface"""

    _java_class = "oracle.pgx.config.DbConnectionConfig"

    def __init__(self, java_graph_config) -> None:
        self._graph_config = java_graph_config

    def get_jdbc_url(self) -> Optional[str]:
        """Get the JDBC URL pointing to an RDBMS instance.

        :returns: the JDBC URL
        """
        return java_handler(self._graph_config.getJdbcUrl, [])

    def get_username(self) -> Optional[str]:
        """Get the username to use when connecting to an RDBMS instance.

        :returns: the username
        """
        return java_handler(self._graph_config.getUsername, [])

    def get_max_prefetched_rows(self) -> int:
        """Get the maximum number of rows prefetched during each round trip resultset-database.

        :returns: the maximum number of prefetched rows
        """
        return java_handler(self._graph_config.getMaxPrefetchedRows, [])

    def get_data_source_id(self) -> Optional[str]:
        """Get the data source id to use to connect to an RDBMS instance.

        :returns: the data source id
        """
        return java_handler(self._graph_config.getDataSourceId, [])

    def get_schema(self) -> Optional[str]:
        """Get the schema to use when reading/writing RDBMS objects.

        :returns: the schema
        """
        return java_handler(self._graph_config.getSchema, [])


class TwoTablesGraphConfig:
    """A class for representing the two tables graph config interface"""

    _java_class = "oracle.pgx.config.TwoTablesGraphConfig"

    def __init__(self, java_graph_config) -> None:
        self._graph_config = java_graph_config

    def get_datastore(self) -> str:
        """Get the underlying datastore.

        :returns: the underlying datastore
        """
        e_type = java_handler(self._graph_config.getDatastore, [])
        return enum_to_python_str(e_type)

    def get_nodes_key_column(self) -> str:
        """Get the name of primary key column in nodes table.

        :returns: the name of primary key column
        """
        return java_handler(self._graph_config.getNodesKeyColumn, [])

    def get_edges_key_column(self) -> str:
        """Get the name of primary key column in edges table.

        :returns: the name of primary key column
        """
        return java_handler(self._graph_config.getEdgesKeyColumn, [])

    def get_from_nid_column(self) -> str:
        """Get the column name for source node.

        :returns: the column name for source node
        """
        return java_handler(self._graph_config.getFromNidColumn, [])

    def get_to_nid_column(self) -> str:
        """Get the column name for destination node.

        :returns: the column name for destination node
        """
        return java_handler(self._graph_config.getToNidColumn, [])

    def get_nodes_label_column(self) -> str:
        """Get the column name for node label.

        :returns: the column name for node label
        """
        return java_handler(self._graph_config.getNodesLabelColumn, [])

    def get_edges_label_column(self) -> str:
        """Get the column name for edge label.

        :returns: the column name for edge label
        """
        return java_handler(self._graph_config.getEdgesLabelColumn, [])

    def has_edge_keys(self) -> bool:
        """Whether or not the config has edge keys.

        :returns: True if it has edge keys
        """
        return bool(java_handler(self._graph_config.hasEdgeKeys, []))
