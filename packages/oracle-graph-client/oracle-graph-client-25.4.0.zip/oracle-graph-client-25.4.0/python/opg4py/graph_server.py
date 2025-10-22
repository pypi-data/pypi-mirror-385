#
# Copyright (C) 2013 - 2025, Oracle and/or its affiliates. All rights reserved.
# ORACLE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
from jnius import autoclass
from pypgx.api._server_instance import ServerInstance
from pypgx._utils.error_handling import java_handler

GraphServer = autoclass('oracle.pg.rdbms.GraphServer')
"""Wrapper class for oracle.pg.rdbms.GraphServer"""


def get_embedded_instance():
    """Connects to an embedded graph server. An embedded graph server runs inside the client JVM.

    :return: a handle to the embedded graph server
    """
    instance = java_handler(GraphServer.getEmbeddedInstance, [])
    return ServerInstance(instance)


def get_instance(base_url: str, username: str, password: str, *, kerberos_ticket_path: str = None) -> ServerInstance:
    """Connects to a remote graph server.

    :param base_url: the base URL in the format host [ : port][ /path] of the remote graph server.
        If `base_url` is None, the default will be used which points to embedded graph server instance.
    :param username: the Database username to use for authentication.
    :param password: the Database password to use for authentication.
    :param kerberos_ticket_path: the kerberos ticket to be used for authentication.

    :return: a handle to the remote graph server
    """
    if (username is not None and password is not None) and kerberos_ticket_path is not None:
        raise ValueError("arguments username and password cannot be specified when kerberos_ticket_path is specified")

    if (kerberos_ticket_path is not None):
        instance = java_handler(GraphServer.getInstance, [base_url, kerberos_ticket_path])
    else:
        instance = java_handler(GraphServer.getInstance, [base_url, username, password])
    return ServerInstance(instance)


def reauthenticate(instance, username, password):
    """Re-authenticates an existing ServerInstance object with a remote graph server.

    :param instance: the PGX instance on which the session is going to reauthenticate.
    :param username: the Database username to use for authentication.
    :param password: the Database password to use for authentication.

    :return: the newly generated authentication token
    """
    instance = java_handler(GraphServer.reauthenticate, [instance._server_instance, username, password])
    return ServerInstance(instance)


def generate_token(base_url, username, password):
    """Generates a new authentication token.

    :param base_url: the base URL in the format host [ : port][ /path] of the remote graph server.
    :param username: the Database username to use for authentication.
    :param password: the Database password to use for authentication.

    :return: the newly generated authentication token
    """
    return java_handler(GraphServer.generateToken, [base_url, username, password])
