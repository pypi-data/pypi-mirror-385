#
# Copyright (C) 2013 - 2025, Oracle and/or its affiliates. All rights reserved.
# ORACLE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
from opg4py._utils.error_handling import java_handler
from ._pgql_sql_trans import PgqlSqlTrans


class PgqlSqlQueryTrans(PgqlSqlTrans):
    """Wrapper class for oracle.pg.rdbms.pgql.PgqlSqlQueryTrans."""

    def __init__(self, java_pgql_sql_query_trans):
        self._java_pgql_sql_trans = java_pgql_sql_query_trans
        self._java_pgql_sql_query_trans = java_pgql_sql_query_trans

    def get_sql_bv_list(self):
        """Get a list of Bind Values to be used with this SQL translation.

        The first element in the list should be set at position 1 in a JDBC PreparedStatement created from this
        SQL translation.

        :return: the list of bind values for this query translation
        """
        return list(java_handler(self._java_pgql_sql_query_trans.getSqlBvList, []))

    def get_sql_translation(self):
        """Get the SQL string for the PGQL to SQL translation.

        :return: the SQL query string
        """
        return java_handler(self._java_pgql_sql_query_trans.getSqlTranslation, [])

    def __repr__(self):
        return "{}(java_pgql_sql_query_trans: {})".format(self.__class__.__name__,
                                                          self._java_pgql_sql_query_trans.__class__.__name__)

    def __str__(self):
        return repr(self)
