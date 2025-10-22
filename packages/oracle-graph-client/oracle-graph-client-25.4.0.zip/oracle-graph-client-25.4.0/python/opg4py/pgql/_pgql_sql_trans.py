#
# Copyright (C) 2013 - 2025, Oracle and/or its affiliates. All rights reserved.
# ORACLE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
from jnius import autoclass
from opg4py._utils.error_handling import java_handler

translation_type = autoclass('oracle.pg.rdbms.pgql.PgqlSqlTrans$TranslationType')
translation_types = {
    'create': translation_type.CREATE,
    'drop': translation_type.DROP,
    'modify': translation_type.MODIFY,
    'query': translation_type.QUERY
}


class PgqlSqlTrans:
    """Wrapper class for oracle.pg.rdbms.pgql.PgqlSqlTrans."""

    def __init__(self, java_pgql_sql_trans):
        self._java_pgql_sql_trans = java_pgql_sql_trans

    def get_translation_type(self):
        """Get the type for the PGQL to SQL translation.

        :return: a PgqlSqlTrans.TranslationType object with the SQL translation type
        """
        java_translation_type = java_handler(self._java_pgql_sql_trans.getTranslationType, [])
        return java_translation_type.toString()

    def __repr__(self):
        return "{}(java_pgql_sql_trans: {})".format(self.__class__.__name__,
                                                    self._java_pgql_sql_trans.__class__.__name__)

    def __str__(self):
        return repr(self)
