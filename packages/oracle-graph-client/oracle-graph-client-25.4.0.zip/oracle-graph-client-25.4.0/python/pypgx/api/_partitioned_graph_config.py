#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx.api._graph_config import GraphConfig
from pypgx.api._graph_config_interfaces import DbConnectionConfig
from pypgx.api.redaction import PgxRedactionRuleConfig
from typing import List, Any, Optional, Dict
from pypgx._utils.error_handling import java_handler
from pypgx._utils import conversion


class PartitionedGraphConfig(GraphConfig, DbConnectionConfig):
    """A class for representing partitioned graph configurations"""

    _java_class = "oracle.pgx.config.PartitionedGraphConfig"

    def get_redaction_rules(self) -> List[PgxRedactionRuleConfig]:
        """Get the redaction rules from this graph configuration.

        :returns: the list of PgxRedactionRuleConfig
        """
        rules = java_handler(self._graph_config.getRedactionRules, [])
        return conversion.collection_to_python_list(rules)

    def get_rules_mapping(self) -> List[Dict[str, Any]]:
        """Get the mapping between redaction rules and users/roles.

        :returns: the list of PgxRedactionRuleMappingConfig
        """
        rules = java_handler(self._graph_config.getRulesMapping, [])
        return conversion.collection_to_python_list(rules)

    def get_vertex_providers(self) -> List[Dict[str, Any]]:
        """Get the vertex providers of this graph configuration.

        :returns: the list of URIs
        """
        rules = java_handler(self._graph_config.getVertexProviders, [])
        return conversion.collection_to_python_list(rules)

    def get_edge_providers(self) -> List[Dict[str, Any]]:
        """Get the edge providers of this graph configuration.

        :returns: the list of URIs
        """
        rules = java_handler(self._graph_config.getEdgeProviders, [])
        return conversion.collection_to_python_list(rules)

    def get_num_connections(self) -> int:
        """Get the number of connections to read/write data from/to the RDBMS table.

        :returns: the number of connections
        """
        return java_handler(self._graph_config.getNumConnections, [])

    def get_es_url(self) -> Optional[str]:
        """Get the ES URL pointing to an ES instance.

        :returns: the ES URL
        """
        return java_handler(self._graph_config.getEsUrl, [])

    def get_es_index_name(self) -> Optional[str]:
        """Get the ES Index name.

        :returns: the ES Index
        """
        return java_handler(self._graph_config.getEsUrl, [])

    def get_scroll_time(self) -> str:
        """Get the ES scroll time.

        :returns: the ES scroll time
        """
        return java_handler(self._graph_config.getScrollTime, [])

    def get_proxy_url(self) -> Optional[str]:
        """Get the proxy server URL to be used for connection to es_url.

        :returns: the proxy URL
        """
        return java_handler(self._graph_config.getProxyUrl, [])

    def get_username(self) -> Optional[str]:
        """Get the username to use when connecting to an ES instance.

        :returns: the username
        """
        return java_handler(self._graph_config.getUsername, [])

    def get_max_batch_size(self) -> int:
        """Get the maximum number of docs requested during each ES request, this is the ES default.

        :returns: the maximum number of requested docs
        """
        return java_handler(self._graph_config.getMaxBatchSize, [])

    def get_pg_view_name(self) -> Optional[str]:
        """Get the name of the PG view in the database to load the graph from.

        :return: the name of the PG view
        """
        return java_handler(self._graph_config.getPgViewName, [])

    def get_prepared_queries(self) -> Optional[List[Dict[str, Any]]]:
        """Get an additional list of prepared queries with arguments, working in the same way as
        'queries'.

        :return: the list of prepared queries
        """
        queries = java_handler(self._graph_config.getPreparedQueries, [])
        return conversion.collection_to_python_list(queries)

    def get_queries(self) -> Optional[List[str]]:
        """Get a list of queries used to determine which data to load from the database.

        :return: a list of queries
        """
        queries = java_handler(self._graph_config.getQueries, [])
        return conversion.collection_to_python_list(queries)
