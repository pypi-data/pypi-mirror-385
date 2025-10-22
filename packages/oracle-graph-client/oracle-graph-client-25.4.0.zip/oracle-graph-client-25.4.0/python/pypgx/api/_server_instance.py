#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

import json
import warnings
from jnius import autoclass

from pypgx._utils.error_handling import java_handler
from pypgx._utils.error_messages import INVALID_OPTION
from pypgx._utils.pgx_types import time_units, memory_units
from pypgx._utils import conversion
from typing import Dict, Optional, Any, Union, Set, Mapping, TYPE_CHECKING
from pypgx.api.auth import PgxGenericPermission

if TYPE_CHECKING:
    # Don't import at runtime, to avoid circular imports.
    from pypgx.api._pgx_session import PgxSession
    from pypgx.api._version_info import VersionInfo


class ServerInstance:
    """A PGX server instance."""

    _java_class = 'oracle.pgx.api.ServerInstance'

    def __init__(self, java_server_instance) -> None:
        self._server_instance = java_server_instance

    @property
    def is_embedded_instance(self) -> bool:
        """Whether or not the engine is embedded.

        :returns: True if embedded, False otherwise.
        """
        return self._server_instance.isEmbeddedInstance()

    @property
    def username(self) -> Optional[str]:
        """Get the username.

        :returns: the username.
        """
        return self._server_instance.getPgxUsername()

    @property
    def base_url(self) -> str:
        """Get the base URL of the server instance.

        :returns: the base URL of the server instance.
        """
        return self._server_instance.getBaseUrl()

    @property
    def prefetch_size(self) -> int:
        """Get the prefetch size.

        :returns: the prefetch size.
        """
        return self._server_instance.getPrefetchSize()

    @property
    def upload_batch_size(self) -> int:
        """Get the upload batch size.

        :returns: the upload batch size.
        """
        return self._server_instance.getUploadBatchSize()

    @property
    def remote_future_timeout(self) -> int:
        """Get the remote future timeout.

        :returns: the remote future timeout.
        """
        return self._server_instance.getRemoteFutureTimeout()

    @property
    def client_server_interaction_mode(self) -> str:
        """Get the client server interaction mode.

        :returns: the client server interaction mode.
        """
        return self._server_instance.getClientServerInteractionMode().toString()

    @property
    def remote_future_pending_retry_interval(self) -> int:
        """Get the remote future pending retry interval.

        :returns: the remote future pending retry interval.
        """
        return self._server_instance.getRemoteFuturePendingRetryInterval()

    @property
    def is_create_partitioned_graphs_with_graph_builder(self) -> bool:
        """Check if the graph builder should create partitioned graphs by default.

        :returns: true if the graph builder should create partitioned graphs by default
        """
        return self._server_instance.isCreatePartitionedGraphsWithGraphBuilder()

    @property
    def version(self) -> str:
        """Get the PGX version of this instance.

        :returns: the PGX version of this instance.
        """
        return self._server_instance.getVersion().toString()

    @property
    def pgx_version(self) -> Any:
        """Get the PGX version of this instance.

        :returns: the PGX version of this instance.
        """
        warnings.warn(
            "`pgx_version` is deprecated since 23.1, use `get_version()` instead",
            DeprecationWarning
        )
        return self._server_instance.getVersion()

    def create_session(
        self,
        source: str,
        idle_timeout: Optional[int] = None,
        task_timeout: Optional[int] = None,
        time_unit: str = 'milliseconds',
    ) -> "PgxSession":
        """
        :param source: A descriptive string identifying the client
        :param idle_timeout: If not null, tries to overwrite server default idle timeout
        :param task_timeout: If not null, tries to overwrite server default task timeout
        :param time_unit: Time unit of idleTimeout and taskTimeout
             ('days', 'hours', 'microseconds', 'milliseconds', 'minutes', 'nanoseconds', 'seconds')
        :returns: PgxSession
        """
        from pypgx.api._pgx_session import PgxSession

        if time_unit not in time_units:
            raise ValueError(INVALID_OPTION.format(var='time_unit', opts=list(time_units.keys())))

        # Convert timeouts to Long, as Pyjnius only converts to int, and createSession() doesn't
        # accept it
        long = autoclass('java.lang.Long')
        idle_timeout = long(idle_timeout) if idle_timeout is not None else None
        task_timeout = long(task_timeout) if task_timeout is not None else None
        time_unit = time_units[time_unit]
        session = java_handler(
            self._server_instance.createSession, [source, idle_timeout, task_timeout, time_unit]
        )
        return PgxSession(session)

    def get_session(self, session_id: str) -> "PgxSession":
        """Get a session by ID.

        :param session_id: Id of the session
        :returns: PgxSession
        """
        from pypgx.api._pgx_session import PgxSession

        session = java_handler(self._server_instance.getSession, [session_id])
        return PgxSession(session)

    def get_pgx_config(self) -> Dict[str, Any]:
        """Get the PGX config.

        :returns: Dict containing current config
        """
        config = self._server_instance.getPgxConfig()
        pgx_config = {}
        for k in config.keySet():
            key = k
            value = config.get(k)
            if not isinstance(key, str):
                tmp = getattr(key, "toString", None)
                key = tmp() if tmp is not None else str(key)
            if not isinstance(value, str):
                tmp = getattr(value, "toString", None)
                value = tmp() if tmp is not None else str(value)
            pgx_config[key] = value
        return pgx_config

    def get_server_state(self) -> Dict[str, Any]:
        """Return the server state.

        :return: Server state as a dict
        """
        server_state = self._server_instance.getServerState()
        return json.loads(server_state.toString())

    def get_version(self) -> "VersionInfo":
        """Get the PGX extended version of this instance.

        :returns: VersionInfo object
        """
        from pypgx.api._version_info import VersionInfo

        version = self._server_instance.getVersion()
        return VersionInfo(version)

    def kill_session(self, session_id: str) -> None:
        """Kill a session.

        :param session_id: Session id
        """
        java_handler(self._server_instance.killSession, [session_id])

    def is_engine_ready(self) -> bool:
        """Boolean of whether or not the engine is ready to accept new requests"""
        return java_handler(self._server_instance.isEngineReady, [])

    def unpin_graph(self, graph_name: str) -> None:
        """Unpin the specified published graph so that if no session
        uses any of its snapshot, it can be removed.

        :param graph_name: name of the published graph to unpin
        """
        java_handler(self._server_instance.unpinGraph, [graph_name])

    def shutdown_engine_now(self) -> None:
        """Force the engine to stop and clean up resources. Currently
        running tasks are interrupted. New incoming requests get rejected.
        Throws an exception when current tasks didn't finish after a short
        grace period.
        """
        java_handler(self._server_instance.shutdownEngineNow, [])

    def set_token(self, token: str) -> None:
        """Set the current auth token for this ServerInstance.
        Note depending on the RealmClient implementation used, this might
        not be supported or have no effect.

        :param token: the new auth token
        """
        java_handler(self._server_instance.setToken, [token])

    def set_session_max_memory_size(self, session: "PgxSession", size: int, unit: str) -> None:
        """Set the maximum memory limit for the given session.

        :param session: on which session to apply the memory limit
        :param size: memory limit to be set relative to the provided memory_unit
        :param unit: the memory_unit to use for the given size
            Only supports megabyte, gigabyte, terabyte
            Requires SERVER_MANAGE permission
        """
        if unit not in memory_units:
            raise ValueError(
                INVALID_OPTION.format(var='unit', opts=list(memory_units.keys()))
            )
        else:
            java_handler(
                self._server_instance.setSessionMaxMemorySize,
                [session._session, size, memory_units[unit]]
            )

    def set_session_idle_timeout(self, session_id: str, idle_timeout: int, unit: str) -> None:
        """Set the session idle timeout for the given session.

        :param session_id: on which session to apply the idle timeout
        :param idle_timeout: value of idle timeout
        :param unit: the time unit to use for the given idle_timeout
            Only supports days, hours, microseconds, milliseconds, minutes, nanoseconds, seconds
            Requires SERVER_MANAGE or SESSION_SET_IDLE_TIMEOUT permission
        """
        if unit not in time_units:
            raise ValueError(
                INVALID_OPTION.format(var='unit', opts=list(time_units.keys()))
            )
        else:
            java_handler(
                self._server_instance.setSessionIdleTimeout,
                [session_id, idle_timeout, time_units[unit]]
            )

    def is_graph_preloading_done(self) -> bool:
        """Boolean of whether or not the preloading of the graphs has completed"""
        return java_handler(self._server_instance.isGraphPreloadingDone, [])

    def get_pgx_username(self) -> str:
        """Get PGX username"""
        return java_handler(self._server_instance.getPgxUsername, [])

    def get_pgx_user_roles(self) -> Set[str]:
        """Get PGX user roles"""
        java_set = java_handler(self._server_instance.getPgxUserRoles, [])
        user_roles = conversion.set_to_python(java_set)
        return user_roles

    def free_cached_memory(self) -> int:
        """Free cached PGX memory and return the freed memory in MB.
        This may be done after closing a graph in order to free up resources.
        Note that memory might not be freed immediately on the system.
        """
        java_cache_statistics = java_handler(self._server_instance.freeCachedMemory, [0.0])
        freed_memory = java_handler(java_cache_statistics.getFreedMemory, [])
        return freed_memory

    def is_engine_running(self) -> bool:
        """Boolean of whether or not the engine is running"""
        return java_handler(self._server_instance.isEngineRunning, [])

    def start_engine(self, config: Optional[Union[str, Mapping[str, Any]]] = None) -> None:
        """Start the PGX engine.

        :param config: path to json file or dict-like containing the PGX config
        """

        if config is None:
            java_handler(self._server_instance.startEngine, [])
        elif isinstance(config, str):
            java_handler(self._server_instance.startEngine, [config])
        else:
            java_handler(self._server_instance.startEngine, [conversion.to_java_map(config)])

    def update_pgx_config(self, config: Union[str, Mapping[str, Any]]) -> None:
        """Replace the current PGX config with the given configuration.

        This only affects static permissions (i.e. non-graph) and redaction rules for pre-loaded
        graphs. Existing permissions on graphs and frames will not be changed.

        :param config: path to json file or dict-like PGX config containing the new authorization
            config
        """

        if isinstance(config, str):
            java_handler(self._server_instance.updatePgxConfig, [config])
        else:
            java_handler(self._server_instance.updatePgxConfig, [conversion.to_java_map(config)])

    def get_pgx_generic_permissions(self) -> Optional[Set[PgxGenericPermission]]:
        """Get the static permissions of the current user i.e. file-location permissions and
        system permissions. Returns None in embedded mode.

        :returns: set containing the current user's static permissions
        """

        generic_permissions_java_set = java_handler(
            self._server_instance.getPgxGenericPermissions,
            []
        )

        if generic_permissions_java_set is not None:
            generic_permissions_set = set()
            for generic_permission in generic_permissions_java_set:
                generic_permissions_set.add(PgxGenericPermission(generic_permission))

            return generic_permissions_set

        else:
            return None

    def shutdown_engine(self) -> None:
        """Force the engine to stop and clean up resources"""
        java_handler(self._server_instance.shutdownEngineNowIfRunning, [])

    def __repr__(self) -> str:
        version = self.get_version().release_version
        if self.is_embedded_instance:
            return "{}(embedded: {}, version: {})".format(
                self.__class__.__name__, self.is_embedded_instance, version
            )
        else:
            return "{}(embedded: {}, base_url: {}, version: {})".format(
                self.__class__.__name__, self.is_embedded_instance, self.base_url, version
            )

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._server_instance.equals(other._server_instance)
