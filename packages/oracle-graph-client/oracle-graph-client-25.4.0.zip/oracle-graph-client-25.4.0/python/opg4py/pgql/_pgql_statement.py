#
# Copyright (C) 2013 - 2025, Oracle and/or its affiliates. All rights reserved.
# ORACLE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
from jnius import autoclass
from opg4py._utils.error_handling import java_handler
from ._pgql_result_set import PgqlResultSet
from ._pgql_sql_query_trans import PgqlSqlQueryTrans
from ._pgql_sql_trans import PgqlSqlTrans

DbmsUtils = autoclass('oracle.pg.rdbms.pgql.DbmsUtils')


class PgqlStatement:
    """Wrapper class for oracle.pg.rdbms.pgql.PgqlStatement."""

    def __init__(self, java_pgql_statement):
        self._java_pgql_statement = java_pgql_statement

    def cancel(self):
        """Allows to cancel currently running execute operation.

        Note that cancel does not rollback already executed modifications.

        Throws: oracle.pgql.lang.PgqlException - When an error occurs while canceling current operation.
        """
        java_handler(self._java_pgql_statement.cancel, [])

    def execute(self, pgql, parallel=DbmsUtils.DEFAULT_PARALLEL, dynamic_sampling=DbmsUtils.DEFAULT_DS,
                match_options=None, options=None):
        """Executes a PGQL Query, Modify or Create/Drop operation on this instance's property graph.

        Supported query options (matchOptions) are the same as those for executeQuery.

        Supported modify options are:

        STREAMING=T Use result sets instead of temporary tables to perform the update.

        AUTO_COMMIT=F Do not commit after performing the modify operation.

        DELETE_CASCADE=F Do not delete incoming/outgoing edges when deleting a vertex.

        :param pgql: the PGQL modify to execute
        :param parallel: the degree of parallelism to use for query and update execution
        :param dynamic_sampling: the value for dynamic sampling
        :param match_options: additional options used to influence query translation and execution
        :param options: additional options used to influence modify translation and execution

        :return: True if the provided PGQL query is a select, false for other statements

        Throws:
            PgqlToSqlException - if a server-side error occurs during translation or SQL execution
            oracle.pgql.lang.PgqlException - if a server-side error occurs or method is called on a closed Statement
        """
        return java_handler(self._java_pgql_statement.execute,
                            [pgql, parallel, dynamic_sampling, match_options, options])

    def execute_query(self, pgql, timeout=0, parallel=DbmsUtils.DEFAULT_PARALLEL, dynamic_sampling=DbmsUtils.DEFAULT_DS,
                      max_results=DbmsUtils.DEFAULT_MAX_RESULTS, options=None):
        """Translates this PGQL statement into a SQL statement and executes it against this instance's property graph.

        Supported query options are:

        USE_RW=F Use CONNECT BY instead of recursive WITH for unbounded path traversals

        MAX_PATH_LEN=n Traverse at most n hops when evaluating unbounded path traversals

        EDGE_SET_PARTIAL=T Fetch properties for each start and end vertex found when reading edges from the query result

        :param pgql: the PGQL query to execute
        :param timeout: the number of seconds for query execution to finish
        :param parallel: the degree of parallelism to use for query execution
        :param dynamic_sampling: the value for dynamic sampling
        :param max_results: the maximum number of rows returned
        :param options: additional options used to influence query translation and execution

        :return: a PgqlResultSet object with the result of the provided PGQL query

        Throws:
            PgqlToSqlException - if a server-side error occurs during translation or SQL execution
            oracle.pgql.lang.PgqlException - if a server-side error occurs or method is called on a closed Statement
        """
        java_result_set = java_handler(self._java_pgql_statement.executeQuery,
                                       [pgql, timeout, parallel, dynamic_sampling, max_results, options])
        return PgqlResultSet(java_result_set)

    def get_batch_size(self):
        """Get the number of commands that should be batched when executing updates.

        :return: the update batch size
        """
        return java_handler(self._java_pgql_statement.getBatchSize, [])

    def get_fetch_size(self):
        """Get the number of rows that should be fetched from the database when more rows are needed for a query result.

        :return: the query fetch size
        """
        return java_handler(self._java_pgql_statement.getFetchSize, [])

    def get_modify_count(self):
        """Get the number of rows that were modified by last execute operation.

        :return: The number of rows modified
        """
        return java_handler(self._java_pgql_statement.getModifyCount, [])

    def get_result_set(self):
        """Retrieve the current result as a PgqlResultSet object.

        This method should be called only once per result.

        :return: Current result as a ResultSet object or null if the query is not a SELECT query
        """
        java_result_set = java_handler(self._java_pgql_statement.getResultSet, [])
        return PgqlResultSet(java_result_set)

    def set_batch_size(self, batch_size):
        """Set the number of commands that should be batched when executing updates.

        :param batch_size: the update batch size
        """
        java_handler(self._java_pgql_statement.setBatchSize, [batch_size])

    def set_fetch_size(self, fetch_size):
        """Set the number of rows that should be fetched from the database when more rows are needed for a query result.

        :param fetch_size: the query fetch size
        """
        java_handler(self._java_pgql_statement.setFetchSize, [fetch_size])

    def translate_query(self, pgql, parallel=DbmsUtils.DEFAULT_PARALLEL, dynamic_sampling=DbmsUtils.DEFAULT_DS,
                        max_results=DbmsUtils.DEFAULT_MAX_RESULTS, options=None):
        """Translates this instance's PGQL statement into a SQL statement.

        Supported query options are:

        USE_RW=F Use CONNECT BY instead of recursive WITH for unbounded path traversals

        MAX_PATH_LEN=n Traverse at most n hops when evaluating unbounded path traversals

        EDGE_SET_PARTIAL=T Fetch properties for each start and end vertex found when reading edges from the query result

        :param pgql: the PGQL query to translate
        :param parallel: the degree of parallelism to use for query execution
        :param dynamic_sampling: the value for dynamic sampling
        :param max_results: the maximum number of rows returned
        :param options: additional options used to influence query translation

        :return: a PgqlSqlTrans object with the SQL translation and column metadata for the provided PGQL query

        Throws:
            PgqlToSqlException - if a server-side error occurs during translation
            oracle.pgql.lang.PgqlException - if a server-side error occurs or method is called on a closed Statement
        """
        java_pgql_sql_query_trans = java_handler(self._java_pgql_statement.translateQuery,
                                                 [pgql, parallel, dynamic_sampling, max_results, options])
        return PgqlSqlQueryTrans(java_pgql_sql_query_trans)

    def translate_statement(self, pgql, parallel=DbmsUtils.DEFAULT_PARALLEL, dynamic_sampling=DbmsUtils.DEFAULT_DS,
                            max_results=DbmsUtils.DEFAULT_MAX_RESULTS, match_options=None, options=None):
        """Translates the given PGQL statement into a series of SQL statements.

        :param pgql: the PGQL statement to translate
        :param parallel: the degree of parallelism to use for query execution
        :param dynamic_sampling: the value for dynamic sampling
        :param max_results: the maximum number of rows returned
        :param match_options: additional options used to influence query translation and execution
        :param options: additional options used to influence DDL/DML translation and execution

        :return: the SQL statements and metadata necessary to execute the provided SQL statement

        Throws:
            PgqlToSqlException - if a server-side error occurs during translation
            oracle.pgql.lang.PgqlException - if a server-side error occurs or method is called on a closed Statement
        """
        java_pgql_sql_trans = java_handler(self._java_pgql_statement.translateStatement,
                                           [pgql, parallel, dynamic_sampling, max_results, match_options, options])
        return PgqlSqlTrans(java_pgql_sql_trans)

    def close(self):
        """Releases this PgqlStatment's database and JDBC resources.

        Closing this PgqlStatement will close all PgqlResultSets that were created from it.

        Throws: oracle.pgql.lang.PgqlException
        """
        java_handler(self._java_pgql_statement.close, [])

    def __repr__(self):
        return "{}(java_pgql_statement: {})".format(self.__class__.__name__,
                                                    self._java_pgql_statement.__class__.__name__)

    def __str__(self):
        return repr(self)
