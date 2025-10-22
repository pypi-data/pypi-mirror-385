#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from typing import Optional, Any
from pypgx._utils.error_handling import java_handler


class GraphWiseBaseConvLayerConfig:
    """GraphWise conv layer base configuration."""

    _java_class = "oracle.pgx.config.mllib.GraphWiseBaseConvLayerConfig"

    def __init__(self, java_config, params) -> None:
        self._config = java_config
        self.params = params

    @property
    def num_sampled_neighbors(self) -> int:
        """Get the number of sampled neighbors."""
        return java_handler(self._config.getNumSampledNeighbors, [])

    @property
    def activation_fn(self) -> Any:
        """Get the activation function."""
        return java_handler(self._config.getActivationFunction, [])

    @property
    def weight_init_scheme(self) -> Any:
        """Get the weight initialization scheme."""
        return java_handler(self._config.getWeightInitScheme, [])

    @property
    def vertex_to_edge_connection(self) -> Optional[bool]:
        """Get the vertex to edge connection."""
        connection = java_handler(self._config.getVertexToEdgeConnection, [])
        if connection is None:
            return None
        return bool(connection)

    @property
    def vertex_to_vertex_connection(self) -> Optional[bool]:
        """Get the vertex to vertex connection."""
        connection = java_handler(self._config.getVertexToVertexConnection, [])
        if connection is None:
            return None
        return bool(connection)

    @property
    def edge_to_vertex_connection(self) -> Optional[bool]:
        """Get the edge to vertex connection."""
        connection = java_handler(self._config.getEdgeToVertexConnection, [])
        if connection is None:
            return None
        return bool(connection)

    @property
    def edge_to_edge_connection(self) -> Optional[bool]:
        """Get the edge to edge connection."""
        connection = java_handler(self._config.getEdgeToEdgeConnection, [])
        if connection is None:
            return None
        return bool(connection)

    def __repr__(self) -> str:
        attributes = []
        for param in self.params:
            if param != "self":
                attributes.append("%s: %s" % (param, self.params[param]))
        return "%s(%s)" % (self.__class__.__name__, ", ".join(attributes))

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._config.equals(other._config)


class GraphWiseConvLayerConfig(GraphWiseBaseConvLayerConfig):
    """GraphWise conv layer configuration."""

    _java_class = "oracle.pgx.config.mllib.GraphWiseConvLayerConfig"

    def __init__(self, java_config, params) -> None:
        super().__init__(java_config, params)

    @property
    def neighbor_weight_property_name(self) -> str:
        """Get the name of the property that stores the weight of the edge."""
        return java_handler(self._config.getNeighborWeightPropertyName, [])


class GraphWiseAttentionLayerConfig(GraphWiseBaseConvLayerConfig):
    """GraphWise attention layer configuration."""

    _java_class = "oracle.pgx.config.mllib.GraphWiseAttentionLayerConfig"

    def __init__(self, java_config, params) -> None:
        super().__init__(java_config, params)

    @property
    def num_heads(self) -> int:
        """Get the number of heads."""
        return java_handler(self._config.getNumHeads, [])

    @property
    def head_aggregation(self) -> Any:
        """Get the aggregation operation for heads."""
        return java_handler(self._config.getHeadAggregation, [])
