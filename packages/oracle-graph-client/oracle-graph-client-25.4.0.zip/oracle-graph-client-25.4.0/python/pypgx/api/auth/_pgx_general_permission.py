#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils.error_handling import java_handler
from pypgx._utils.pgx_types import pgx_general_permissions


class PgxGeneralPermission:
    """Class representing a type of general permission."""

    _java_class = 'oracle.pgx.common.auth.PgxGeneralPermission'

    NONE : "PgxGeneralPermission"
    SERVER_GET_INFO : "PgxGeneralPermission"
    SERVER_MANAGE : "PgxGeneralPermission"
    SESSION_ADD_PUBLISHED_GRAPH : "PgxGeneralPermission"
    SESSION_COMPILE_ALGORITHM : "PgxGeneralPermission"
    SESSION_CREATE : "PgxGeneralPermission"
    SESSION_GET_PUBLISHED_GRAPH : "PgxGeneralPermission"
    SESSION_NEW_GRAPH : "PgxGeneralPermission"
    SESSION_READ_MODEL : "PgxGeneralPermission"
    SESSION_MODIFY_MODEL : "PgxGeneralPermission"
    SESSION_SET_IDLE_TIMEOUT : "PgxGeneralPermission"

    def __init__(self, java_general_permission):
        self._general_permission = java_general_permission

    def allows_session_create(self) -> bool:
        """Check if session creation is permitted.

        :return: Boolean indicating if session creation is permitted.
        """
        return java_handler(self._general_permission.allowsSessionCreate, [])

    def allows_set_session_idle_timeout(self) -> bool:
        """Check if set session idle timeout is permitted.

        :return: Boolean indicating if idle timeout updating is permitted.
        """
        return java_handler(self._general_permission.allowsSetSessionIdleTimeout, [])

    def allows_create_graph(self) -> bool:
        """Check if graph creation is permitted.

        :return: Boolean indicating if graph creation is permitted.
        """
        return java_handler(self._general_permission.allowsCreateGraph, [])

    def allows_get_published_graph(self) -> bool:
        """Check if you have permission to get a published graph.

        :return: Boolean indicating if getting a published graph is permitted.
        """
        return java_handler(self._general_permission.allowsGetPublishedGraph, [])

    def allows_publish_graph(self) -> bool:
        """Check if you have permission to publish a graph.

        :return: Boolean indicating if publishing a graph is permitted.
        """
        return java_handler(self._general_permission.allowsPublishGraph, [])

    def allows_compile_algorithm(self) -> bool:
        """Check if you have permission to compile algorithms.

        :return: Boolean indicating if compiling algorithms is permitted.
        """
        return java_handler(self._general_permission.allowsCompileAlgorithm, [])

    def allows_get_server_info(self) -> bool:
        """Check if you have permission to get the server info.

        :return: Boolean indicating if getting the server info is permitted.
        """
        return java_handler(self._general_permission.allowsGetServerInfo, [])

    def allows_manage_server(self) -> bool:
        """Check if you have permission for managing the server.

        :return: Boolean indicating if managing the server is permitted.
        """
        return java_handler(self._general_permission.allowsManageServer, [])

    def allows_ml_model_reading(self) -> bool:
        """Check if you have permission to read ML models.

        :return: Boolean indicating if reading ML models is permitted.
        """
        return java_handler(self._general_permission.allowsMlModelReading, [])

    def allows_ml_model_inference(self) -> bool:
        """Check if you have permission for ML model inference.

        :return: Boolean indicating if ML model inference is permitted.
        """
        return java_handler(self._general_permission.allowsMlModelInference, [])

    def allows_ml_model_training(self) -> bool:
        """Check if you have permission to train ML models.

        :return: Boolean indicating if training ML models is permitted.
        """
        return java_handler(self._general_permission.allowsMlModelTraining, [])

    def allows_ml_model_storing(self) -> bool:
        """Check if you have permission to store ML models.

        :return: Boolean indicating if storing ML models is permitted.
        """
        return java_handler(self._general_permission.allowsMlModelStoring, [])

    def allows_create_frame(self) -> bool:
        """Check if you have permission to create a frame.

        :return: Boolean indicating if creating a frame is permitted.
        """
        return java_handler(self._general_permission.allowsCreateFrame, [])

    def allows_store_frame(self) -> bool:
        """Check if you have permission to store a frame.

        :return: Boolean indicating if storing a frame is permitted.
        """
        return java_handler(self._general_permission.allowsStoreFrame, [])

    def allows_load_frame(self) -> bool:
        """Check if you have permission to load a frame.

        :return: Boolean indicating if loading a frame is permitted.
        """
        return java_handler(self._general_permission.allowsLoadFrame, [])

    def name(self) -> str:
        """Get the name of the general permission

        :returns: name of the general permission
        """
        return(java_handler(self._general_permission.name, []))

    def __repr__(self) -> str:
        return java_handler(self._general_permission.toString, [])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._general_permission.equals(other._general_permission)

    def __hash__(self) -> int:
        return java_handler(self._general_permission.hashCode, [])


# make the general permissions available on the class
PgxGeneralPermission.NONE = PgxGeneralPermission(
    pgx_general_permissions['none']
)
PgxGeneralPermission.SERVER_GET_INFO = PgxGeneralPermission(
    pgx_general_permissions['server_get_info']
)
PgxGeneralPermission.SERVER_MANAGE = PgxGeneralPermission(
    pgx_general_permissions['server_manage']
)
PgxGeneralPermission.SESSION_ADD_PUBLISHED_GRAPH = PgxGeneralPermission(
    pgx_general_permissions['session_add_published_graph']
)
PgxGeneralPermission.SESSION_COMPILE_ALGORITHM = PgxGeneralPermission(
    pgx_general_permissions['session_compile_algorithm']
)
PgxGeneralPermission.SESSION_CREATE = PgxGeneralPermission(
    pgx_general_permissions['session_create']
)
PgxGeneralPermission.SESSION_GET_PUBLISHED_GRAPH = PgxGeneralPermission(
    pgx_general_permissions['session_get_published_graph']
)
PgxGeneralPermission.SESSION_NEW_GRAPH = PgxGeneralPermission(
    pgx_general_permissions['session_new_graph']
)
PgxGeneralPermission.SESSION_READ_MODEL = PgxGeneralPermission(
    pgx_general_permissions['session_read_model']
)
PgxGeneralPermission.SESSION_MODIFY_MODEL = PgxGeneralPermission(
    pgx_general_permissions['session_modify_model']
)
