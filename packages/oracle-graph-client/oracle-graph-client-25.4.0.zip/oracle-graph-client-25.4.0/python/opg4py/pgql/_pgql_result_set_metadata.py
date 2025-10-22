#
# Copyright (C) 2013 - 2025, Oracle and/or its affiliates. All rights reserved.
# ORACLE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
from opg4py._utils.error_handling import java_handler


class PgqlResultSetMetaData:
    """Wrapper class for oracle.pgql.lang.ResultSetMetaData."""

    def __init__(self, java_pgql_result_set_metadata):
        self._java_pgql_result_set_metadata = java_pgql_result_set_metadata

    def get_column_count(self):
        """Get the total number of columns in the query result.

        :return: the total number of columns
        """
        return java_handler(self._java_pgql_result_set_metadata.getColumnCount, [])

    def get_column_name(self, column):
        """Get the name of the column at the given offset starting from 1.

        :param column: the offset of the column, numbering starts from 1
        :return: the column name
        """
        return java_handler(self._java_pgql_result_set_metadata.getColumnName, [column])

    def __repr__(self):
        return "{}(java_pgql_result_set_metadata: {})".format(self.__class__.__name__,
                                                              self._java_pgql_result_set_metadata.__class__.__name__)

    def __str__(self):
        return repr(self)
