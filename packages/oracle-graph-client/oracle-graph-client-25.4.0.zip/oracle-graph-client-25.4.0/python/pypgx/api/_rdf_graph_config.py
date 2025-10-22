#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx.api._graph_config import GraphConfig
from typing import List, Optional, Dict, Any
from pypgx._utils.error_handling import java_handler
from pypgx._utils import conversion


class RdfGraphConfig(GraphConfig):
    """A class for representing RDF graph configurations"""

    _java_class = "oracle.pgx.config.RdfGraphConfig"

    def get_accepted_predicates(self) -> List[str]:
        """Get predicates of triples that are transformed to edges.

        :returns: the accepted predicates
        """
        accepted_predicates = java_handler(self._graph_config.getAcceptedPredicates, [])
        return conversion.collection_to_python_list(accepted_predicates)

    def get_ignored_predicates(self) -> List[str]:
        """Get predicates of triples that are ignored.

        :returns: the ignore predicates
        """
        ignored_predicates = java_handler(self._graph_config.getIgnoredPredicates, [])
        return conversion.collection_to_python_list(ignored_predicates)

    def get_prefixes(self) -> List[Dict[str, Any]]:
        """Get the IRI prefixes.

        :returns: the IRI prefixes
        """
        prefixes = []
        prefix_list = java_handler(self._graph_config.getPrefixes, [])
        for prefix in prefix_list:
            prefixes.append(conversion.config_to_python_dict(prefix))
        return prefixes

    def get_vertex_label_predicates(self) -> List[str]:
        """Get the predicates of triples that are transformed to vertex labels.

        :returns: the predicates of triples
        """
        vertex_label_predicates = java_handler(self._graph_config.getVertexLabelPredicates, [])
        return conversion.collection_to_python_list(vertex_label_predicates)

    def get_jdbc_url(self) -> Optional[str]:
        """Get the JDBC URL pointing to an RDBMS instance.

        :returns: the JDBC URL
        """
        return java_handler(self._graph_config.getJdbcUrl, [])

    def get_username(self) -> Optional[str]:
        """Get the username to use when connecting to an RDBMS instance.

        :returns: the username
        """
        return java_handler(self._graph_config.getUsername, [])

    def get_data_source_id(self) -> Optional[str]:
        """Get data source id to use to connect to an RDBMS instance

        :returns: the data source id
        """
        return java_handler(self._graph_config.getDataSourceId, [])

    def get_max_prefetched_rows(self) -> int:
        """Get the maximum number of rows prefetched during each round trip resultset-database.

        :returns: the maximum number of prefetched rows
        """
        return java_handler(self._graph_config.getMaxPrefetchedRows, [])

    def is_black_list_mode(self) -> bool:
        """Whether this GraphConfig is in black list mode.

        :returns: True if black list mode
        """
        return bool(java_handler(self._graph_config.isBlackListMode, []))

    def get_network_name(self) -> Optional[str]:
        """Get RDF network name.

        :returns: the RDF network name
        """
        return java_handler(self._graph_config.getNetworkName, [])

    def get_network_owner(self) -> Optional[str]:
        """Get owner of the RDF network.

        :returns: owner of the RDF network
        """
        return java_handler(self._graph_config.getNetworkOwner, [])

    def use_prefix(self) -> Optional[bool]:
        """Get whether prefixes should be used instead of uri

        :returns: True if prefixes should be used instead of uri
        """
        return java_handler(self._graph_config.usePrefix, [])

    def get_parallel_hint_degree(self) -> int:
        """Get the parallel hint degree to use for internal queries.
        If the value is negative, the parallel hint will be omitted.
        If the value is zero, a parallel hint without degree is generated.

        :returns: the parallel hint degree to use
        """
        return java_handler(self._graph_config.getParallelHintDegree, [])
