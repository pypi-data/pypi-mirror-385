#
# Copyright (C) 2013 - 2025, Oracle and/or its affiliates. All rights reserved.
# ORACLE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
from jnius import autoclass
from opg4py._utils.error_handling import java_handler
from ._pgql_statement import PgqlStatement
from ._pgql_prepared_statement import PgqlPreparedStatement

PgqlConnectionClass = autoclass('oracle.pg.rdbms.pgql.PgqlConnection')
DbmsUtils = autoclass('oracle.pg.rdbms.pgql.DbmsUtils')


class PgqlConnection:
    """Wrapper class for oracle.pg.rdbms.pgql.PgqlConnection."""

    def __init__(self, java_pgql_connection):
        self._java_pgql_connection = java_pgql_connection

    def clear_graph_metadata_cache(self):
        """Clear the cache that stores graph metadata.
        """
        java_handler(self._java_pgql_connection.clearGraphMetadataCache, [])

    def clear_translation_cache(self):
        """Clear the cache that stores translations.
        """
        java_handler(self._java_pgql_connection.clearTranslationCache, [])

    def create_statement(self):
        """Creates a new PgqlStatement object, which is used to execute PGQL queries.

        :return: a new PgqlStatement object that can be used to perform PGQL queries
        """
        java_pgql_statement = java_handler(self._java_pgql_connection.createStatement, [])
        return PgqlStatement(java_pgql_statement)

    def disable_graph_metadata_cache(self):
        """Disable the cache that stores graph metadata.
        """
        java_handler(self._java_pgql_connection.disableGraphMetadataCache, [])

    def disable_translation_cache(self):
        """Disable the cache that stores translations.
        """
        java_handler(self._java_pgql_connection.disableTranslationCache, [])

    def enable_graph_metadata_cache(self):
        """Enable the cache that stores graph metadata.
        """
        java_handler(self._java_pgql_connection.enableGraphMetadataCache, [])

    def enable_translation_cache(self):
        """Enable the cache that stores translations.
        """
        java_handler(self._java_pgql_connection.enableTranslationCache, [])

    @staticmethod
    def get_connection(java_sql_connection):
        """Factory method to get PgqlConnection instance.

        :param java_sql_connection: a JDBC connection
        :return: a PgqlConnection instance
        """
        java_pgql_connection = java_handler(PgqlConnectionClass.getConnection, [java_sql_connection])
        return PgqlConnection(java_pgql_connection)

    def get_graph(self):
        """Get the graph name on which PGQL queries will be executed for this connection.

        :return: the graph name for this connection
        """
        return java_handler(self._java_pgql_connection.getGraph, [])

    def get_jdbc_connection(self):
        """Get the JDBC connection that is used to execute PGQL queries.

        :return: the connection
        """
        return java_handler(self._java_pgql_connection.getJdbcConnection, [])

    def get_schema(self):
        """Get the schema name that will be used to execute PGQL queries with this connection.

        If the schema has not been set, the schema from JDBC connection is returned.

        :return: the schema set for this connection

        Throws:
            PgqlToSqlException - if a database access error occurs or this method is called on a closed connection
        """
        return java_handler(self._java_pgql_connection.getSchema, [])

    def prepare_statement(self, pgql, timeout=DbmsUtils.DEFAULT_TIMEOUT, parallel=DbmsUtils.DEFAULT_PARALLEL,
                          dynamicSampling=DbmsUtils.DEFAULT_DS, maxResults=DbmsUtils.DEFAULT_MAX_RESULTS,
                          matchOptions=None, options=None):
        """Creates a new PgqlPreparedStatement object, which represents a pre-compiled PGQL statement.

        :param pgql: the PGQL query to compile
        :param timeout: the number of seconds for query execution to finish
        :param parallel: the degree of parallelism to use for query and modify execution
        :param dynamicSampling: the value for dynamic sampling
        :param maxResults: the maximum number of rows returned
        :param matchOptions: additional options used to influence query translation and execution
        :param options: additional options used to influence modify translation and execution
        :return: a PgqlPreparedStatement object that can be used to efficiently execute the same query multiple times
        """
        java_pgql_prepared_statement = java_handler(self._java_pgql_connection.prepareStatement,
                                                    [pgql, timeout, parallel, dynamicSampling, maxResults, matchOptions,
                                                     options])
        return PgqlPreparedStatement(java_pgql_prepared_statement)

    def set_graph(self, graph):
        """Sets the graph name on which PGQL queries will be executed for this connection.

        :param graph: the name of the graph
        """
        java_handler(self._java_pgql_connection.setGraph, [graph])

    def set_graph_metadata_cache_max_capacity(self, max_capacity):
        """Set max capacity value for the graph metadata cache

        :param max_capacity: value for max capacity
        """
        java_handler(self._java_pgql_connection.setGraphMetadataCacheMaxCapacity, [max_capacity])

    def set_schema(self, schema):
        """Sets the schema name that will be used to execute PGQL queries with this connection.

        :param schema: the name of the schema
        """
        java_handler(self._java_pgql_connection.setSchema, [schema])

    def set_translation_cache_max_capacity(self, max_capacity):
        """Set max capacity value for the translation cache

        :param max_capacity: value for max capacity
        """
        java_handler(self._java_pgql_connection.setTranslationCacheMaxCapacity, [max_capacity])

    def close(self):
        """Free the resources of the internal JDBC connection."""
        java_handler(self._java_pgql_connection.conn.close, [])

    def __repr__(self):
        return "{}(schema: {}, graph: {})".format(self.__class__.__name__, self.get_schema(), self.get_graph())

    def __str__(self):
        return repr(self)
