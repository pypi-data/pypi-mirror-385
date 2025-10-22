#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#
from pypgx._utils.error_handling import java_handler


class GraphDelta:
    """Represents a delta since the last synchronization operation"""

    _java_class = "oracle.pgx.api.GraphDelta"

    def __init__(self, java_graph_delta) -> None:
        self._graph_delta = java_graph_delta

    @property
    def total_num_changes(self) -> int:
        """Get the total number of changes

        :returns: total number of changes
        :rtype: int
        """
        return java_handler(self._graph_delta.getTotalNumberOfChanges, [])

    @property
    def num_added_vertices(self) -> int:
        """Get the number of added vertices

        :returns: number of added vertices
        :rtype: int
        """
        return java_handler(self._graph_delta.getNumberOfAddedVertices, [])

    @property
    def num_removed_vertices(self) -> int:
        """Get the number of removed vertices

        :returns: number of removed vertices
        :rtype: int
        """
        return java_handler(self._graph_delta.getNumberOfRemovedVertices, [])

    @property
    def num_updated_vertices(self) -> int:
        """Get the number of updated vertices

        :returns: number of updated vertices
        :rtype: int
        """
        return java_handler(self._graph_delta.getNumberOfUpdatedVertices, [])

    @property
    def num_added_edges(self) -> int:
        """Get the number of added edges

        :returns: number of added edges
        :rtype: int
        """
        return java_handler(self._graph_delta.getNumberOfAddedEdges, [])

    @property
    def num_removed_edges(self) -> int:
        """Get the number of removed edges

        :returns: number of removed edges
        :rtype: int
        """
        return java_handler(self._graph_delta.getNumberOfRemovedEdges, [])

    @property
    def num_updated_edges(self) -> int:
        """Get the number of updated edges

        :returns: number of updated edges
        :rtype: int
        """
        return java_handler(self._graph_delta.getNumberOfUpdatedEdges, [])
