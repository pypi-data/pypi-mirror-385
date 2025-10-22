#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils.error_handling import java_handler

from pypgx.api.frames import PgxFrame
from pypgx.api.mllib import GraphWisePredictionLayerConfig
from pypgx.api.mllib._supervised_gnn_explainer import SupervisedGnnExplainer
from pypgx.api.mllib._gnn_explanation import SupervisedGnnExplanation
from pypgx.api.mllib._graphwise_model import GraphWiseModel
from pypgx.api.mllib._loss_function import LossFunction
from pypgx._utils import conversion
from pypgx._utils.pgx_types import SUPERVISED_LOSS_FUNCTIONS
from jnius import autoclass, cast
from pypgx.api._pgx_entity import PgxVertex
from pypgx.api._pgx_graph import PgxGraph
from typing import List, Union, Dict, Iterable, Optional


class SupervisedGraphWiseModel(GraphWiseModel):
    """SupervisedGraphWise model object."""

    _java_class = 'oracle.pgx.api.mllib.SupervisedGraphWiseModel'

    def get_prediction_layer_configs(self) -> GraphWisePredictionLayerConfig:
        """Get the configuration objects for the prediction layers.

        :return: configuration of the prediction layer
        :rtype: GraphWisePredictionLayerConfig
        """
        if 'pred_layer_config' not in self.params:
            self.params['pred_layer_config'] = None
        return self.params['pred_layer_config']

    def get_loss_function(self) -> str:
        """Get the loss function name.

        :return: loss function name. Can be one of softmax_cross_entropy, sigmoid_cross_entropy,
            devnet
        :rtype: str
        """
        if 'loss_fn' not in self.params:
            self.params['loss_fn'] = None
        return self.params['loss_fn']

    def get_loss_function_class(self) -> LossFunction:
        """Get the loss function.

        :return: loss function
        :rtype: LossFunction
        """

        loss_fn_runtime_error = RuntimeError('Loss function is not set for this class')
        if 'loss_fn' not in self.params:
            raise loss_fn_runtime_error
        loss_fn = None
        if isinstance(self.params['loss_fn'], str):
            loss_fn_name = self.params['loss_fn']
            if loss_fn_name not in SUPERVISED_LOSS_FUNCTIONS.keys():
                raise ValueError(
                    'Loss function string (%s) must be of the following types: %s'
                    % (loss_fn_name, ', '.join(SUPERVISED_LOSS_FUNCTIONS.keys()))
                )
            for subclass in LossFunction.__subclasses__():
                if subclass.__name__ is SUPERVISED_LOSS_FUNCTIONS[loss_fn_name]:
                    loss_fn = subclass()
        elif isinstance(self.params['loss_fn'], LossFunction):
            loss_fn = self.params['loss_fn']

        if loss_fn is not None:
            return loss_fn
        raise loss_fn_runtime_error

    def get_class_weights(self) -> Dict:
        """Get the class weights.

        :return: a dictionary mapping classes to their weights.
        :rtype: dict
        """
        if 'class_weights' not in self.params:
            self.params['class_weights'] = None
        return self.params['class_weights']

    def get_vertex_target_property_name(self) -> str:
        """Get the target property name

        :return: target property name
        :rtype: str
        """
        if 'vertex_target_property_name' not in self.params:
            self.params['vertex_target_property_name'] = self._model.getVertexTargetPropertyName()
        return self.params['vertex_target_property_name']

    def get_target_vertex_labels(self) -> List[str]:
        """Get the target vertex labels

        :return: target vertex labels
        :rtype: List[str]
        """
        if 'target_vertex_labels' not in self.params:
            self.params['target_vertex_labels'] = None
        return self.params['vertex_target_property_name']

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

    def infer(
        self, graph: PgxGraph, vertices: Union[Iterable[PgxVertex], Iterable[int], Iterable[str]],
        threshold: float = 0.0
    ) -> PgxFrame:
        """Infer the predictions for the specified vertices

        :param graph: the graph
        :type graph: PgxGraph
        :param vertices: the vertices to infer embeddings for. Can be a list of vertices or their
            IDs.
        :param threshold: decision threshold for classification (unused for regression)

        :returns: PgxFrame containing the inference results for each vertex
        :rtype: PgxFrame
        """
        self.check_is_fitted()
        vids = conversion.to_java_list(conversion.to_java_vertex(graph, v) for v in vertices)
        return PgxFrame(java_handler(self._model.infer, [graph._graph, vids, threshold]))

    def infer_embeddings(
        self, graph: PgxGraph, vertices: Union[Iterable[PgxVertex], Iterable[int], Iterable[str]]
    ) -> PgxFrame:
        """Infer the embeddings for the specified vertices

        :param graph: the graph
        :type graph: PgxGraph
        :param vertices: the vertices to infer embeddings for. Can be a list of vertices or their
            IDs.

        :returns: PgxFrame containing the embeddings for each vertex
        :rtype: PgxFrame
        """
        self.check_is_fitted()
        vids = conversion.to_java_list(conversion.to_java_vertex(graph, v) for v in vertices)
        return PgxFrame(java_handler(self._model.inferEmbeddings, [graph._graph, vids]))

    def infer_logits(
        self, graph: PgxGraph, vertices: Union[Iterable[PgxVertex], Iterable[int], Iterable[str]]
    ) -> PgxFrame:
        """Infer the prediction logits for the specified vertices

        :param graph: the graph
        :type graph: PgxGraph
        :param vertices: the vertices to infer logits for. Can be a list of vertices or their
            IDs.

        :returns: PgxFrame containing the logits for each vertex
        :rtype: PgxFrame
        """
        self.check_is_fitted()
        vids = conversion.to_java_list(conversion.to_java_vertex(graph, v) for v in vertices)
        return PgxFrame(java_handler(self._model.inferLogits, [graph._graph, vids]))

    def infer_labels(
        self, graph: PgxGraph, vertices: Union[Iterable[PgxVertex], Iterable[int], Iterable[str]],
        threshold: float = 0.0
    ) -> PgxFrame:
        """Infer the labels for the specified vertices

        :param graph: the graph
        :type graph: PgxGraph
        :param vertices: the vertices to infer labels for. Can be a list of vertices or their
            IDs.
        :param threshold: decision threshold for classification (unused for regression)

        :returns: PgxFrame containing the labels for each vertex
        :rtype: PgxFrame
        """
        self.check_is_fitted()
        vids = conversion.to_java_list(conversion.to_java_vertex(graph, v) for v in vertices)
        return PgxFrame(java_handler(self._model.inferLabels, [graph._graph, vids, threshold]))

    def evaluate(
        self, graph: PgxGraph, vertices: Union[Iterable[PgxVertex], Iterable[int], Iterable[str]],
        threshold: float = 0.0
    ) -> PgxFrame:
        """Evaluate performance statistics for the specified vertices.

        :param graph: the graph
        :type graph: PgxGraph
        :param vertices: the vertices to evaluate on. Can be a list of vertices or their
            IDs.
        :param threshold: decision threshold for classification (unused for regression)

        :returns: PgxFrame containing the metrics
        :rtype: PgxFrame
        """
        self.check_is_fitted()
        vids = conversion.to_java_list(conversion.to_java_vertex(graph, v) for v in vertices)
        return PgxFrame(java_handler(self._model.evaluate, [graph._graph, vids, threshold]))

    def evaluate_labels(
        self, graph: PgxGraph, vertices: Union[Iterable[PgxVertex], Iterable[int], Iterable[str]],
        threshold: float = 0.0
    ) -> PgxFrame:
        """Evaluate (macro averaged) classification performance statistics for the specified
        vertices.

        :param graph: the graph
        :type graph: PgxGraph
        :param vertices: the vertices to evaluate on. Can be a list of vertices or their
            IDs.
        :param threshold: decision threshold for classification (unused for regression)

        :returns: PgxFrame containing the metrics
        :rtype: PgxFrame
        """
        self.check_is_fitted()
        vids = conversion.to_java_list(conversion.to_java_vertex(graph, v) for v in vertices)
        return PgxFrame(java_handler(self._model.evaluateLabels, [graph._graph, vids, threshold]))

    def infer_and_get_explanation(
        self,
        graph: PgxGraph,
        vertex: Union[PgxVertex, int],
        num_optimization_steps: int = 200,
        learning_rate: float = 0.05,
        marginalize: bool = False,
        threshold: float = 0.0
    ) -> SupervisedGnnExplanation:
        """Perform inference on the specified vertex and generate an explanation that contains
        scores of how important each property and each vertex in the computation graph is for the
        prediction.

        :param graph: the graph
        :type graph: PgxGraph
        :param vertex: the vertex or its ID
        :type vertex: PgxVertex or int
        :param threshold: decision threshold for classification (unused for regression)

        :returns: explanation containing feature importance and vertex importance.
        :rtype: SupervisedGnnExplanation
        """
        return self.gnn_explainer(
            num_optimization_steps=num_optimization_steps,
            learning_rate=learning_rate,
            marginalize=marginalize
        ).infer_and_explain(graph, vertex, threshold)

    def gnn_explainer(
        self,
        num_optimization_steps: int = 200,
        learning_rate: float = 0.05,
        marginalize: bool = False
    ) -> SupervisedGnnExplainer:
        """Configure and return the GnnExplainer object of this model that can be used to
        request explanations of predictions.

        :param num_optimization_steps: optimization steps for the explainer, defaults to 200
        :type num_optimization_steps: int, optional
        :param learning_rate: learning rate for the explainer, defaults to 0.05
        :type learning_rate: float, optional
        :param marginalize: marginalize the loss over features, defaults to False
        :type marginalize: bool, optional
        :return: SupervisedGnnExplainer object of this model
        :rtype: SupervisedGnnExplainer
        """
        # fix for edge case GM-27791
        # pyjnius converts java Booleans to integers. In order to cast them back to bools in
        # explanation.get_label, we need to pass the information whether the label should be bool
        java_bool_property_type = autoclass('oracle.pgx.common.types.PropertyType').BOOLEAN
        model_config = cast('oracle.pgx.config.mllib.SupervisedGraphWiseModelConfig',
                            self._model.getConfig())
        bool_label = model_config.getLabelType() == java_bool_property_type

        return SupervisedGnnExplainer(self._model.gnnExplainer()
                                      .numOptimizationSteps(num_optimization_steps)
                                      .learningRate(learning_rate)
                                      .marginalize(marginalize),
                                      bool_label=bool_label)
