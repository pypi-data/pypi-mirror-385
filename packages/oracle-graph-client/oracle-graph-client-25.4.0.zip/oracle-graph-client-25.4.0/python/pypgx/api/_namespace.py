#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from jnius import autoclass
from pypgx._utils.error_handling import java_handler
from pypgx.api._pgx_id import PgxId

_JavaNamespace = autoclass('oracle.pgx.api.Namespace')


class Namespace:
    """Represents a namespace for objects (e.g. graphs, properties) in PGX.

    .. note:: This class is just a thin wrapper and does not check if the input
       is actually a java namespace.
    """

    _java_class = 'oracle.pgx.api.Namespace'

    def __init__(self, java_namespace) -> None:
        self._namespace = java_namespace

    @staticmethod
    def from_id(namespace_id: PgxId) -> 'Namespace':
        """Get the Python namespace object.

        :param namespace_id: A new namespace object will be created for this ID.
        :returns: The Python namespace object.
        :rtype: oracle.pgx.api.Namespace
        """
        return Namespace(java_handler(_JavaNamespace.fromId, [namespace_id._id]))

    def get_namespace_id(self) -> PgxId:
        """Get the Python PgxId object.

        :returns: The Python PgxId object.
        :rtype: PgxId
        """
        return PgxId(java_handler(self._namespace.getNamespaceId, []))

    def get_java_namespace(self):
        """Get the java namespace object.

        :returns: The java namespace object.
        :rtype: oracle.pgx.api.Namespace
        """
        return self._namespace


NAMESPACE_PRIVATE = Namespace(_JavaNamespace.PRIVATE)
NAMESPACE_PUBLIC = Namespace(_JavaNamespace.PUBLIC)
