#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils.error_handling import java_handler

from pypgx.api.frames import PgxFrame
from pypgx.api.mllib._unsupervised_graphwise_model import UnsupervisedGraphWiseModel
from pypgx._utils import conversion
from pypgx._utils.error_messages import PROPERTY_NOT_FOUND
from pypgx.api._pgx_entity import PgxVertex
from pypgx.api._pgx_graph import PgxGraph
from typing import Union, Iterable


class UnsupervisedAnomalyDetectionGraphWiseModel(UnsupervisedGraphWiseModel):
    """UnsupervisedGraphWise model object."""

    _java_class = 'oracle.pgx.api.mllib.UnsupervisedAnomalyDetectionGraphWiseModel'

    def infer_anomaly_scores(
        self, graph: PgxGraph, vertices: Union[Iterable[PgxVertex], Iterable[int], Iterable[str]]
    ) -> PgxFrame:
        """Infer the anomaly scores for the specified vertices.

        :param graph: the graph
        :param vertices: the vertices to infer on
        :return: PgxFrame containing the anomaly scores for each vertex.
        :rtype: PgxFrame
        """
        self.check_is_fitted()
        vids = conversion.to_java_list(conversion.to_java_vertex(graph, v) for v in vertices)
        return PgxFrame(java_handler(self._model.inferAnomalyScores, [graph._graph, vids]))

    def find_anomaly_threshold(
        self, graph: PgxGraph, vertices: Union[Iterable[PgxVertex], Iterable[int], Iterable[str]],
        contamination_factor: float
    ) -> float:
        """Find an appropriate anomaly threshold for labeling the input vertices as anomalies,
        respecting the proportion given by the contamination factor

        :param graph: the graph
        :param vertices: the vertices to infer on
        :param contamination_factor: the contamination factor
        :return: the threshold
        :rtype: float
        """
        self.check_is_fitted()
        vids = conversion.to_java_list(conversion.to_java_vertex(graph, v) for v in vertices)
        return float(java_handler(self._model.findAnomalyThreshold,
                                  [graph._graph, vids, contamination_factor]))

    def infer_anomaly_labels(
        self, graph: PgxGraph, vertices: Union[Iterable[PgxVertex], Iterable[int], Iterable[str]],
        threshold: float
    ) -> PgxFrame:
        """Infer the anomaly labels for the specified vertices.

        :param graph: the graph
        :param vertices: the vertices to infer on
        :param threshold: the anomaly threshold
        :return: PgxFrame containing the anomaly labels for each vertex.
        :rtype: PgxFrame
        """
        self.check_is_fitted()
        vids = conversion.to_java_list(conversion.to_java_vertex(graph, v) for v in vertices)
        return PgxFrame(java_handler(self._model.inferAnomalyLabels,
                                     [graph._graph, vids, threshold]))

    def evaluate_anomaly_labels(
        self, graph: PgxGraph, vertices: Union[Iterable[PgxVertex], Iterable[int], Iterable[str]],
        vertex_anomaly_property_name: str, anomaly_property_value: object, threshold: float
    ):
        """Evaluate anomaly detection performance statistics for the specified vertices.

        :param graph: the graph
        :param vertices: the vertices to evaluate on
        :param vertex_anomaly_property_name: the name of the property containing the anomaly
        :param anomaly_property_value: the value indicating an anomaly
                in vertex_anomaly_property_name property
        :param threshold: the anomaly threshold
        :raises LookupError: if the property is not found
        :return: PgxFrame containing the evaluation results.
        :rtype: PgxFrame
        """
        self.check_is_fitted()
        vids = conversion.to_java_list(conversion.to_java_vertex(graph, v) for v in vertices)
        property = graph.get_vertex_property(vertex_anomaly_property_name)
        if property is None:
            raise LookupError(PROPERTY_NOT_FOUND.format(prop=vertex_anomaly_property_name))
        property_type = property.type
        java_anomaly_property_value = conversion.property_to_java(
            anomaly_property_value, property_type)
        return PgxFrame(java_handler(
            self._model.evaluateAnomalyLabels,
            [graph._graph, vids, vertex_anomaly_property_name,
             java_anomaly_property_value, threshold]))
