#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from typing import TYPE_CHECKING

from pypgx._utils.error_handling import java_handler
from pypgx.api._graph_delta import GraphDelta

if TYPE_CHECKING:
    # Don't import at runtime, to avoid circular imports.
    from pypgx.api._pgx_graph import PgxGraph
    from pypgx.api._pgx_session import PgxSession


class Synchronizer:
    """A class for synchronizing changes in an external data source with a PGX graph."""

    _java_class = 'oracle.pgx.api.Synchronizer'

    def __init__(self, java_synchronizer, session: "PgxSession") -> None:
        self._synchronizer = java_synchronizer
        self._session = session

    def apply(self) -> "PgxGraph":
        """Apply the changes to the underlying PGX graph.

        :returns: The graph with changes.
        :type: PgxGraph
        """
        from pypgx.api._pgx_graph import PgxGraph

        java_graph = java_handler(self._synchronizer.apply, [])
        return PgxGraph(self._session, java_graph)

    def fetch(self) -> None:
        """Fetch the changes from the external data source.
        You can call this multiple times to accumulate deltas. The deltas reset once you call
        `apply()`.
        """
        java_handler(self._synchronizer.fetch, [])

    def get_graph_delta(self) -> "GraphDelta":
        """Get the description of the delta between current snapshot and the fetched changes.
        Can be used to make a decision for when to apply the delta.

        :returns: The delta between the current snapshot and the fetched changes.
        :type: GraphDelta
        """
        java_graph_delta = java_handler(self._synchronizer.getGraphDelta, [])
        return GraphDelta(java_graph_delta)

    def sync(self) -> "PgxGraph":
        """Synchronize changes from the external data source and return the new snapshot
        of the graph with the fetched changes applied.

        :returns: The new snapshot of the graph.
        :type: PgxGraph
        """
        from pypgx.api._pgx_graph import PgxGraph

        java_graph = java_handler(self._synchronizer.sync, [])
        return PgxGraph(self._session, java_graph)
