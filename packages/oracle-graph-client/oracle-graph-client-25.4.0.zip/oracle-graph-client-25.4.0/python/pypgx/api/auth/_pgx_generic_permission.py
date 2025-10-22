#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils.error_handling import java_handler
from pypgx.api.auth import PgxResourcePermission, PgxGeneralPermission


class PgxGenericPermission:
    """Class for generic permission."""

    _java_class = 'oracle.pgx.common.auth.PgxGenericPermission'

    def __init__(self, java_generic_permission):
        self._generic_permission = java_generic_permission

    def is_general_permission(self) -> bool:
        """Check if it is a general permission.

        :return: Boolean indicating if permission is general.
        """
        return java_handler(self._generic_permission.isGeneralPermission, [])

    def is_file_location_permission(self) -> bool:
        """Check if the location and resource permission aren't null

        :return: Boolean indicating location and resource permission aren't null
        """
        return java_handler(self._generic_permission.isFileLocationPermission, [])

    def get_general_permission(self) -> PgxGeneralPermission:
        """Get the general permission

        :return: The general permission
        """
        general_permission = PgxGeneralPermission(
            java_handler(self._generic_permission.getGeneralPermission, [])
        )
        return general_permission

    def get_location(self) -> str:
        """Get the generic permission location

        :return: The generic permission location
        """
        return java_handler(self._generic_permission.getLocation, [])

    def get_resource_permission(self) -> PgxResourcePermission:
        """Get pgx resource permission

        :return: pgx resource permission
        """
        permission = java_handler(self._generic_permission.getResourcePermission, [])
        return PgxResourcePermission(permission)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self):
        return java_handler(self._generic_permission.toString, [])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._generic_permission.equals(other._generic_permission)

    def __hash__(self) -> int:
        return java_handler(self._generic_permission.hashCode, [])
