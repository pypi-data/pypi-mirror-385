#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils.error_handling import java_handler

from pypgx.api.frames import PgxFrame
from pypgx.api.mllib._edgewise_model import EdgeWiseModel
from pypgx.api.mllib._graphwise_dgi_layer_config import GraphWiseDgiLayerConfig
from pypgx._utils import conversion
from pypgx.api._pgx_entity import PgxEdge
from pypgx.api._pgx_graph import PgxGraph
from typing import List, Union, Iterable, Optional


class UnsupervisedEdgeWiseModel(EdgeWiseModel):
    """UnsupervisedEdgeWise model object."""

    _java_class = 'oracle.pgx.api.mllib.UnsupervisedEdgeWiseModel'

    def get_dgi_layer_config(self) -> GraphWiseDgiLayerConfig:
        """Get the configuration object for the dgi layer.

        :return: configuration
        :rtype: GraphWiseDgiLayerConfig
        """
        if 'dgi_layer_config' not in self.params:
            java_dgi_layer_config = self._model.getDgiLayerConfigs()
            self.params['dgi_layer_config'] = GraphWiseDgiLayerConfig(java_dgi_layer_config, {})
        return self.params['dgi_layer_config']

    def get_loss_function(self) -> str:
        """Get the loss function name.

        :return: loss function name: sigmoid_cross_entropy
        :rtype: str
        """
        if 'loss_fn' not in self.params:
            self.params['loss_fn'] = None
        return self.params['loss_fn']

    def get_target_edge_labels(self) -> List[str]:
        """Get the target edge labels

        :return: target edge labels
        :rtype: List[str]
        """
        if 'target_edge_labels' not in self.params:
            self.params['target_edge_labels'] = None
        return self.params['edge_target_property_name']

    def store(self, path: str, key: str, overwrite: bool = False) -> None:
        """Store the model in a file.

        :param path: Path where to store the model
        :type path: str
        :param key: Encryption key
        :type key: str
        :param overwrite: Whether or not to overwrite pre-existing file
        :type overwrite: bool

        :return: None
        """
        self._check_is_fitted()
        java_handler(self._model.store, [path, key, overwrite])

    def fit(self, graph: PgxGraph, validation_graph: Optional[PgxGraph] = None) -> None:
        """Fit the model on the graph while validating on the validation_graph.

        :param graph: Graph to fit on
        :type graph: PgxGraph
        :param validation_graph: Graph to validate on
        :type validation_graph: PgxGraph

        :return: None
        """
        if validation_graph is None:
            java_handler(self._model.fit, [graph._graph])
        else:
            java_handler(self._model.fit, [graph._graph, validation_graph._graph])
        self._is_fitted = True
        self.loss = self._model.getTrainingLoss()

    def infer_embeddings(
        self, graph: PgxGraph, edges: Union[Iterable[PgxEdge], Iterable[int]]
    ) -> PgxFrame:
        """Infer the embeddings for the specified edges

        :param graph: the graph
        :type graph: PgxGraph
        :param edges: the edges to infer embeddings for. Can be a list of edges or their
            IDs.

        :returns: PgxFrame containing the embeddings for each edge
        :rtype: PgxFrame
        """
        self._check_is_fitted()
        vids = conversion.to_java_list(conversion.to_java_edge(graph, v) for v in edges)
        return PgxFrame(java_handler(self._model.inferEmbeddings, [graph._graph, vids]))
