#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from jnius import autoclass
from pypgx._utils.error_handling import java_handler
from pypgx._utils.pgx_types import pgx_resource_permissions

_PgxResourcePermission = autoclass('oracle.pgx.common.auth.PgxResourcePermission')


class PgxResourcePermission:
    """Class representing a type of resource permission."""

    _java_class = 'oracle.pgx.common.auth.PgxResourcePermission'

    NONE : "PgxResourcePermission"
    READ : "PgxResourcePermission"
    WRITE : "PgxResourcePermission"
    EXPORT : "PgxResourcePermission"
    MANAGE : "PgxResourcePermission"

    def __init__(self, java_resource_permission):
        self._resource_permission = java_resource_permission

    @staticmethod
    def get_strongest(
        a: "PgxResourcePermission",
        b: "PgxResourcePermission",
    ) -> "PgxResourcePermission":
        """Return the strongest permission of the two.

        :param a: A pgx resource permission.
        :type a: PgxResourcePermission
        :param b: A pgx resource permission.
        :type b: PgxResourcePermission

        :returns: The strongest pgx resource permission.
        :type: PgxResourcePermission
        """
        permission = java_handler(
            _PgxResourcePermission.getStrongest,
            [a._resource_permission, b._resource_permission],
        )
        return PgxResourcePermission(permission)

    def allows_inspect(self) -> bool:
        """Check if the resource can be inspected.

        :returns: Boolean indicating if the resource can be inspected.
        :type: bool
        """
        return java_handler(self._resource_permission.allowsInspect, [])

    def allows_read(self) -> bool:
        """Check if the resource can be read.

        :returns: Boolean indicating if the resource can be read.
        :type: bool
        """
        return java_handler(self._resource_permission.allowsRead, [])

    def allows_write(self) -> bool:
        """Check if the resource can be written.

        :returns: Boolean indicating if the resource can be written.
        :type: bool
        """
        return java_handler(self._resource_permission.allowsWrite, [])

    def allows_export(self) -> bool:
        """Check if the resource can be exported.

        :returns: Boolean indicating if the resource can be exported.
        :type: bool
        """
        return java_handler(self._resource_permission.allowsExport, [])

    def allows_manage(self) -> bool:
        """Check if the resource can be managed.

        :returns: Boolean indicating if the resource can be managed.
        :type: bool
        """
        return java_handler(self._resource_permission.allowsManage, [])

    def name(self) -> str:
        """Get the name of the resource permission

        :returns: The name of the resource permission.
        :type: str
        """
        return(java_handler(self._resource_permission.name, []))

    def __str__(self) -> str:
        return java_handler(self._resource_permission.toString, [])

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._resource_permission.equals(other._resource_permission)

    def __hash__(self) -> int:
        return java_handler(self._resource_permission.hashCode, [])


# make the general permissions available on the class
PgxResourcePermission.NONE = PgxResourcePermission(
    pgx_resource_permissions['none']
)
PgxResourcePermission.READ = PgxResourcePermission(
    pgx_resource_permissions['read']
)
PgxResourcePermission.WRITE = PgxResourcePermission(
    pgx_resource_permissions['write']
)
PgxResourcePermission.EXPORT = PgxResourcePermission(
    pgx_resource_permissions['export']
)
PgxResourcePermission.MANAGE = PgxResourcePermission(
    pgx_resource_permissions['manage']
)
