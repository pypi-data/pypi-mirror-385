#
# Copyright (C) 2013 - 2025, Oracle and/or its affiliates. All rights reserved.
# ORACLE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
from jnius import autoclass
from opg4py._utils.error_handling import java_handler
from ._pgql_result_set import PgqlResultSet
from ._pgql_statement import PgqlStatement

DbmsUtils = autoclass('oracle.pg.rdbms.pgql.DbmsUtils')


class PgqlPreparedStatement(PgqlStatement):
    """Wrapper class for oracle.pg.rdbms.pgql.PgqlPreparedStatement."""

    def __init__(self, java_pgql_prepared_statement):
        self._java_pgql_prepared_statement = java_pgql_prepared_statement

    def execute(self, parallel=DbmsUtils.DEFAULT_PARALLEL, dynamic_sampling=DbmsUtils.DEFAULT_DS, match_options=None,
                options=None):
        """Executes a PGQL Query, Modify or Create/Drop operation on this instance's property graph.

        Supported query options (matchOptions) are the same as those for executeQuery.

        Supported modify options are:

        STREAMING=T Use result sets instead of temporary tables to perform the update.

        AUTO_COMMIT=F Do not commit after performing the modify operation.

        DELETE_CASCADE=F Do not delete incoming/outgoing edges when deleting a vertex.

        :param parallel: the degree of parallelism to use for query and update execution
        :param dynamic_sampling: the value for dynamic sampling
        :param match_options: additional options used to influence query translation and execution
        :param options: additional options used to influence modify translation and execution

        :return: True if the provided PGQL query is a select, false for other statements

        Throws:
            PgqlToSqlException - if a server-side error occurs during translation or SQL execution
            oracle.pgql.lang.PgqlException - if a server-side error occurs or method is called on a closed Statement
        """
        return java_handler(self._java_pgql_prepared_statement.execute,
                            [parallel, dynamic_sampling, match_options, options])

    def execute_query(self, timeout=0, parallel=DbmsUtils.DEFAULT_PARALLEL, dynamic_sampling=DbmsUtils.DEFAULT_DS,
                      max_results=DbmsUtils.DEFAULT_MAX_RESULTS, options=None):
        """Translates this PGQL statement into a SQL statement and executes it against this instance's property graph.

        Supported query options are:

        USE_RW=F Use CONNECT BY instead of recursive WITH for unbounded path traversals

        MAX_PATH_LEN=n Traverse at most n hops when evaluating unbounded path traversals

        EDGE_SET_PARTIAL=T Fetch properties for each start and end vertex found when reading edges from the query result

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
        java_result_set = java_handler(self._java_pgql_prepared_statement.executeQuery,
                                       [timeout, parallel, dynamic_sampling, max_results, options])
        return PgqlResultSet(java_result_set)

    def set_array(self, param_index, value):
        """Sets the designated parameter to the given Java List value.

        :param param_index: the first parameter is 1, the second is 2, ...
        :param: value: the parameter value
        """
        java_handler(self._java_pgql_prepared_statement.setArray, [param_index, value])

    def set_boolean(self, param_index, value):
        """Sets the designated parameter to the given Java boolean value.

        :param param_index: the first parameter is 1, the second is 2, ...
        :param: value: the parameter value
        """
        java_handler(self._java_pgql_prepared_statement.setBoolean, [param_index, value])

    def set_double(self, param_index, value):
        """Sets the designated parameter to the given Java double value.

        :param param_index: the first parameter is 1, the second is 2, ...
        :param: value: the parameter value
        """
        java_handler(self._java_pgql_prepared_statement.setDouble, [param_index, value])

    def set_float(self, param_index, value):
        """Sets the designated parameter to the given Java float value.

        :param param_index: the first parameter is 1, the second is 2, ...
        :param: value: the parameter value
        """
        java_handler(self._java_pgql_prepared_statement.setFloat, [param_index, value])

    def set_int(self, param_index, value):
        """Sets the designated parameter to the given Java int value.

        :param param_index: the first parameter is 1, the second is 2, ...
        :param: value: the parameter value
        """
        java_handler(self._java_pgql_prepared_statement.setInt, [param_index, value])

    def set_long(self, param_index, value):
        """Sets the designated parameter to the given Java long value.

        :param param_index: the first parameter is 1, the second is 2, ...
        :param: value: the parameter value
        """
        java_handler(self._java_pgql_prepared_statement.setLong, [param_index, value])

    def set_string(self, param_index, value):
        """Sets the designated parameter to the given Java String value.

        :param param_index: the first parameter is 1, the second is 2, ...
        :param: value: the parameter value
        """
        java_handler(self._java_pgql_prepared_statement.setString, [param_index, value])

    def set_timestamp(self, param_index, value):
        """Sets the designated parameter to the given Java Timestamp value.

        Timestamp values are assumed to be in Coordinated Universal Time (UTC).

        :param param_index: the first parameter is 1, the second is 2, ...
        :param: value: the parameter value
        """
        java_handler(self._java_pgql_prepared_statement.setTimestamp, [param_index, value])

    def __repr__(self):
        return "{}(java_pgql_statement: {})".format(self.__class__.__name__,
                                                    self._java_pgql_prepared_statement.__class__.__name__)

    def __str__(self):
        return repr(self)
