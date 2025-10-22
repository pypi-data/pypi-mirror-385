#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx.api._graph_config import GraphConfig
from pypgx.api._graph_config_interfaces import DbConnectionConfig, TwoTablesGraphConfig
from pypgx._utils.error_handling import java_handler


class TwoTablesRdbmsGraphConfig(GraphConfig, DbConnectionConfig, TwoTablesGraphConfig):
    """A class for representing Two tables RDBMS graph configurations"""

    _java_class = "oracle.pgx.config.TwoTablesRdbmsGraphConfig"

    def get_nodes_table_name(self) -> str:
        """Get the name of nodes table.

        :returns: the name of nodes table
        """
        return java_handler(self._graph_config.getNodesTableName, [])

    def get_edges_table_name(self) -> str:
        """Get the name of edges table.

        :returns: the name of edges table
        """
        return java_handler(self._graph_config.getEdgesTableName, [])

    def get_label_value_delimiter(self) -> str:
        """Get the label value delimiter.

        :returns: the label value delimiter
        """
        return java_handler(self._graph_config.getLabelValueDelimiter, [])

    def has_edges_table(self) -> bool:
        """Whether or not the config has edges table.

        :returns: True if it has edges table
        """
        return bool(java_handler(self._graph_config.hasEdgesTable, []))

    def has_nodes_table(self) -> bool:
        """Whether or not the config has nodes table.

        :returns: True if it has nodes table
        """
        return bool(java_handler(self._graph_config.hasNodesTable, []))

    def get_insert_batch_size(self) -> int:
        """Get the batch size of the rows to be inserted.

        :returns: the batch size of the rows to be inserted
        """
        return java_handler(self._graph_config.getInsertBatchSize, [])

    def get_tablespace(self) -> str:
        """Get the tablespace where the tables are going to be written.

        :returns: the tablespace
        """
        return java_handler(self._graph_config.getTablespace, [])

    def get_num_connections(self) -> int:
        """Get the number of connections to read/write data from/to the RDBMS table.

        :returns: the number of connections
        """
        return java_handler(self._graph_config.getNumConnections, [])
