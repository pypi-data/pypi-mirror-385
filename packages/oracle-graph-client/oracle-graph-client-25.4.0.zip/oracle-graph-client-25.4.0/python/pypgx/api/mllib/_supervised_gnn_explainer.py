#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils.error_handling import java_handler

from pypgx.api._pgx_graph import PgxGraph
from pypgx.api._pgx_entity import PgxVertex
from pypgx.api.mllib._gnn_explainer import GnnExplainer
from pypgx.api.mllib._gnn_explanation import SupervisedGnnExplanation
from pypgx._utils import conversion

from typing import Union


class SupervisedGnnExplainer(GnnExplainer):
    """SupervisedGnnExplainer used to request explanations from supervised model predictions."""

    _java_class = 'oracle.pgx.api.mllib.SupervisedGnnExplainer'

    def __init__(self, java_explainer, bool_label: bool):
        super().__init__(java_explainer)
        self.bool_label = bool_label

    def infer_and_explain(
        self, graph: PgxGraph, vertex: Union[PgxVertex, int, str], threshold: float = 0.0
    ) -> SupervisedGnnExplanation:
        """Perform inference on the specified vertex and generate an explanation that contains
        scores of how important each property and each vertex in the computation graph is for the
        prediction.

        :param graph: the graph
        :type graph: PgxGraph
        :param vertex: the vertex or its ID
        :type vertex: PgxVertex or int
        :param threshold: decision threshold
        :type threshold: float

        :returns: explanation containing feature importance and vertex importance.
        :rtype: SupervisedGnnExplanation
        """
        java_vertex = conversion.to_java_vertex(graph, vertex)
        return SupervisedGnnExplanation(
            java_handler(
                self._explainer.inferAndExplain,
                [graph._graph, java_vertex, threshold],
            ),
            bool_label=self.bool_label,
        )
