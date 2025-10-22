#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

import warnings
from pypgx._utils.error_handling import java_handler

from pypgx.api.frames import PgxFrame
from pypgx.api.mllib._unsupervised_gnn_explainer import UnsupervisedGnnExplainer
from pypgx.api.mllib._gnn_explanation import GnnExplanation
from pypgx.api.mllib._graphwise_model import GraphWiseModel
from pypgx.api.mllib._graphwise_dgi_layer_config import GraphWiseDgiLayerConfig
from pypgx.api.mllib._graphwise_embedding_config import GraphWiseEmbeddingConfig
from pypgx._utils import conversion
from pypgx.api._pgx_entity import PgxVertex
from pypgx.api._pgx_graph import PgxGraph
from typing import Union, Iterable, Optional


class UnsupervisedGraphWiseModel(GraphWiseModel):
    """UnsupervisedGraphWise model object."""

    _java_class = 'oracle.pgx.api.mllib.UnsupervisedGraphWiseModel'

    def get_dgi_layer_config(self) -> GraphWiseDgiLayerConfig:
        """Get the configuration object for the dgi layer.

        :return: configuration
        :rtype: GraphWiseDgiLayerConfig
        """
        warnings.warn(
            "get_dgi_layer_config is deprecated since 23.2, use `get_embedding_config()` instead",
            DeprecationWarning
        )
        if 'dgi_layer_config' not in self.params:
            java_dgi_layer_config = self._model.getDgiLayerConfigs()
            self.params['dgi_layer_config'] = GraphWiseDgiLayerConfig(java_dgi_layer_config, {})
        return self.params['dgi_layer_config']

    def get_embedding_config(self) -> GraphWiseEmbeddingConfig:
        """Get the configuration object for the embedding method

        :return: configuration
        :rtype: GraphWiseEmbeddingConfig
        """
        if 'embedding_config' not in self.params:
            return self.get_dgi_layer_config()
        return self.params['embedding_config']

    def get_loss_function(self) -> str:
        """Get the loss function name.

        :return: loss function name. Can only be sigmoid_cross_entropy
        :rtype: str
        """
        if 'loss_fn' not in self.params:
            self.params['loss_fn'] = None
        return self.params['loss_fn']

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
        self.check_is_fitted()
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

    def infer_embeddings(
        self, graph: PgxGraph, vertices: Union[Iterable[PgxVertex], Iterable[int], Iterable[str]]
    ) -> PgxFrame:
        """Infer the embeddings for the specified vertices.

        :return: PgxFrame containing the embeddings for each vertex.
        :rtype: PgxFrame
        """
        self.check_is_fitted()
        vids = conversion.to_java_list(conversion.to_java_vertex(graph, v) for v in vertices)
        return PgxFrame(java_handler(self._model.inferEmbeddings, [graph._graph, vids]))

    def infer_and_get_explanation(
        self,
        graph: PgxGraph,
        vertex: Union[PgxVertex, int],
        num_clusters: int = 50,
        num_samples: int = 10000,
        num_optimization_steps: int = 200,
        learning_rate: float = 0.05,
        marginalize: bool = False
    ) -> GnnExplanation:
        """Perform inference on the specified vertex and generate an explanation that contains
        scores of how important each property and each vertex in the computation graph is for the
        embeddings position relative to embeddings of other vertices in the graph.

        :param graph: the graph
        :param vertex: the vertex
        :param num_clusters: the number of semantic vertex clusters expected in the graph,
            must be greater than 1
        :returns: explanation containing feature importance and vertex importance.
        """
        return self.gnn_explainer(
            num_optimization_steps=num_optimization_steps,
            learning_rate=learning_rate,
            marginalize=marginalize,
            num_clusters=num_clusters,
            num_samples=num_samples
        ).infer_and_explain(graph, vertex)

    def gnn_explainer(
        self,
        num_optimization_steps: int = 200,
        learning_rate: float = 0.05,
        marginalize: bool = False,
        num_clusters: int = 50,
        num_samples: int = 10000
    ) -> UnsupervisedGnnExplainer:
        """Configure and return the GnnExplainer object of this model that can be used to
        request explanations of predictions.

        :param num_optimization_steps: optimization steps for the explainer, defaults to 200
        :type num_optimization_steps: int, optional
        :param learning_rate: learning rate for the explainer, defaults to 0.05
        :type learning_rate: float, optional
        :param marginalize: marginalize the loss over features, defaults to False
        :type marginalize: bool, optional
        :param num_clusters: number of clusters to use, defaults to 50
        :type num_clusters: int, optional
        :param num_samples: number of samples to use, defaults to 10000
        :type num_samples: int, optional
        :return: UnsupervisedGnnExplainer object of this model
        :rtype: UnsupervisedGnnExplainer
        """
        return UnsupervisedGnnExplainer(self._model.gnnExplainer()
                                        .numOptimizationSteps(num_optimization_steps)
                                        .learningRate(learning_rate)
                                        .marginalize(marginalize)
                                        .numClusters(num_clusters)
                                        .numSamples(num_samples))
