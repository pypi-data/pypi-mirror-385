#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx.api._graph_config import GraphConfig
from pypgx.api._graph_config_interfaces import TwoTablesGraphConfig
from typing import Dict, List, Any, Union, Optional
from pypgx._utils.error_handling import java_handler
from pypgx._utils import conversion


class FileGraphConfig(GraphConfig):
    """A class for representing File graph configurations"""

    _java_class = "oracle.pgx.config.FileGraphConfig"

    def get_vertex_uris(self) -> List[str]:
        """Get the unified resource identifiers for the files with the graph vertex data.

        :returns: the list of URIs
        """
        uris = java_handler(self._graph_config.getVertexUris, [])
        return conversion.collection_to_python_list(uris)

    def get_edge_uris(self) -> List[str]:
        """Get the unified resource identifiers for the files with the graph edge data.

        :returns: the list of URIs
        """
        uris = java_handler(self._graph_config.getEdgeUris, [])
        return conversion.collection_to_python_list(uris)

    def get_separator(self) -> str:
        """Get the separator of this graph configuration.

        :returns: the separator
        """
        return java_handler(self._graph_config.getSeparator, [])

    def is_detect_gzip(self) -> bool:
        """Whether GZip file automatic detection is enabled or not.

        :returns: True if GZip file automatic detection is enabled, false otherwise.
        """
        return bool(java_handler(self._graph_config.isDetectGzip, []))

    def is_header(self) -> bool:
        """Whether the file has a header.

        i.e. first line of file is meant for headers,
        e.g. 'EdgeId, SourceId, DestId, EdgeProp1, EdgeProp2'

        :returns: Whether the file has a header or not
        """
        return bool(java_handler(self._graph_config.isHeader, []))

    def get_vertex_id_column(self) -> Optional[Union[str, int]]:
        """Get the name or index (starting from 1) of column corresponding
        to vertex id (for CSV format only).

        :returns: name or index of column corresponding to vertex id
        """
        return java_handler(self._graph_config.getVertexIdColumn, [])

    def get_vertex_labels_column(self) -> Optional[Union[str, int]]:
        """Get the name or index (starting from 1) of column corresponding
        to vertex labels (for CSV format only).

        :returns: name or index of column corresponding to vertex labels
        """
        return java_handler(self._graph_config.getVertexLabelsColumn, [])

    def get_edge_id_column(self) -> Optional[Union[str, int]]:
        """Get the name or index (starting from 1) of column corresponding
        to edge id (for CSV format only).

        :returns: name or index of column corresponding to edge id
        """
        return java_handler(self._graph_config.getEdgeIdColumn, [])

    def get_edge_source_column(self) -> Optional[Union[str, int]]:
        """Get the name or index (starting from 1) of column corresponding
        to edge source (for CSV format only).

        :returns: name or index of column corresponding to edge source
        """
        return java_handler(self._graph_config.getEdgeSourceColumn, [])

    def get_edge_destination_column(self) -> Optional[Union[str, int]]:
        """Get the name or index (starting from 1) of column corresponding
        to edge destination (for CSV format only).

        :returns: name or index of column corresponding to edge destination
        """
        return java_handler(self._graph_config.getEdgeDestinationColumn, [])

    def get_edge_label_column(self) -> Optional[Union[str, int]]:
        """Get the name or index (starting from 1) of column corresponding
        to edge label (for CSV format only).

        :returns: name or index of column corresponding to edge label
        """
        return java_handler(self._graph_config.getEdgeLabelColumn, [])

    def get_storing(self) -> Dict[str, Any]:
        """Get the storing-specific configuration.

        :returns: the storing configuration
        """
        storing = java_handler(self._graph_config.getStoring, [])
        return conversion.config_to_python_dict(storing)

    def get_uri(self) -> str:
        """Get the unified resource identifier for the file with the graph data.

        :return: the unified resource identifier
        """
        return java_handler(self._graph_config.getUri, [])

    def get_uris(self) -> List[str]:
        """Get the unified resource identifiers for the files with the graph data.

        :return: the unified resource identifiers
        """
        uris = java_handler(self._graph_config.getUris, [])
        return conversion.collection_to_python_list(uris)

    def get_storing_options(self) -> Dict[str, Any]:
        """Get the storing configuration.

        :return: the storing configuration
        """
        storing_options = java_handler(self._graph_config.getStoringOptions, [])
        return conversion.config_to_python_dict(storing_options)


class TwoTablesTextGraphConfig(FileGraphConfig, TwoTablesGraphConfig):
    """A class for representing Two tables text graph configurations"""

    _java_class = "oracle.pgx.config.TwoTablesTextGraphConfig"
