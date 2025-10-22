#
# Copyright (C) 2013 - 2025, Oracle and/or its affiliates. All rights reserved.
# ORACLE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
from jnius import autoclass
from opg4py._utils.error_handling import java_handler
from ._pgql_connection import PgqlConnection

DriverManager = autoclass('java.sql.DriverManager')
OracleDriver = autoclass('oracle.jdbc.OracleDriver')

java_handler(DriverManager.registerDriver, [OracleDriver()])


def get_connection(usr, pwd, jdbc_url):
    """Get a DB connection.

    :param usr: the DB user
    :param pwd: the DB password
    :param jdbc_url: the DB jdbc url
    :return: A PgqlConnection
    """
    conn = java_handler(DriverManager.getConnection, [jdbc_url, usr, pwd])
    conn.setAutoCommit(0)

    pgql_connection = PgqlConnection.get_connection(conn)
    return pgql_connection
