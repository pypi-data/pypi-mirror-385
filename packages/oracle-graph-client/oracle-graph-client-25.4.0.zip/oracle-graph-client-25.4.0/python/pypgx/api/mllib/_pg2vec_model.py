#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

import collections.abc
from jnius import autoclass, JavaException
from pypgx._utils.error_handling import java_handler
from pypgx._utils.error_messages import MODEL_NOT_FITTED, VERTEX_ID_OR_COLLECTION_OF_IDS

from pypgx.api.frames import PgxFrame
from pypgx.api.mllib._model import Model
from pypgx._utils.pyjnius_helper import PyjniusHelper
from pypgx.api._pgx_graph import PgxGraph
from typing import Optional, Union, Iterable, List


class Pg2vecModel(Model):
    """Pg2Vec model object."""

    _java_class = 'oracle.pgx.api.mllib.Pg2vecModel'

    def __init__(self, java_pg2vec_model) -> None:
        self._model = java_pg2vec_model
        super().__init__(self._model)
        self.graph: Optional[PgxGraph] = None

        # Determining whether the model has been fitted is relevant especially for
        # models that are being loaded from a file.

    @property
    def loss(self) -> Optional[float]:
        """Get the loss of the model."""
        try:
            return self._model.getLoss()
        except JavaException:
            return None

    @property
    def seed(self) -> Optional[int]:
        """Get the seed."""
        try:
            return self._model.getSeed()
        except JavaException:
            return None

    def is_fitted(self) -> bool:
        """Whether or not the model has been fitted."""
        return self.loss is not None

    @property
    def graphlet_id_property_name(self) -> str:
        """Get the graphlet id property name."""
        return self._model.getGraphLetIdPropertyName()

    @property
    def vertex_property_names(self) -> List[str]:
        """Get the vertex property names."""
        return self._model.getVertexPropertyNames()

    @property
    def min_word_frequency(self) -> int:
        """Get the minimum word frequency."""
        return self._model.getMinWordFrequency()

    @property
    def batch_size(self) -> int:
        """Get the batch size."""
        return self._model.getBatchSize()

    @property
    def num_epochs(self) -> int:
        """Get the number of epochs."""
        return self._model.getNumEpochs()

    @property
    def layer_size(self) -> int:
        """Get the layer size."""
        return self._model.getLayerSize()

    @property
    def learning_rate(self) -> float:
        """Get the learning rate."""
        return self._model.getLearningRate()

    @property
    def min_learning_rate(self) -> float:
        """Get the minimum learning rate."""
        return self._model.getMinLearningRate()

    @property
    def window_size(self) -> int:
        """Get the window size."""
        return self._model.getWindowSize()

    @property
    def walk_length(self) -> int:
        """Get the walk length."""
        return self._model.getWalkLength()

    @property
    def walks_per_vertex(self) -> int:
        """Get the walks per vertex."""
        return self._model.getWalksPerVertex()

    @property
    def use_graphlet_size(self) -> bool:
        """Get the use graphlet size."""
        return self._model.getUseGraphletSize()

    @property
    def enable_accelerator(self) -> bool:
        """Get whether the accelerator is used if available."""
        return self._model.isEnableAccelerator()

    @property
    def graphlet_size_property_name(self) -> str:
        """Get the graphlet size property name."""
        return self._model.getGraphletSizePropertyName()

    def store(self, path: str, key: Optional[str], overwrite: bool = False) -> None:
        """Store the model in a file.

        :param path: Path where to store the model
        :param key: Encryption key
        :param overwrite: Whether or not to overwrite pre-existing file
        """
        if not self.is_fitted():
            raise RuntimeError(MODEL_NOT_FITTED)
        java_handler(self._model.store, [path, key, overwrite])

    def fit(self, graph: PgxGraph) -> None:
        """Fit the model on a graph.

        :param graph: Graph to fit on
        """
        java_handler(self._model.fit, [graph._graph])
        self.graph = graph

    @property
    def trained_graphlet_vectors(self) -> PgxFrame:
        """Get the trained graphlet vectors for the current pg2vec model.

        :returns: PgxFrame containing the trained graphlet vectors
        """
        if not self.is_fitted():
            raise RuntimeError(MODEL_NOT_FITTED)
        return PgxFrame(java_handler(self._model.getTrainedGraphletVectors, []))

    def infer_graphlet_vector(self, graph: PgxGraph) -> PgxFrame:
        """Return the inferred vector of the input graphlet as a PgxFrame.

        :param graph: graphlet for which to infer a vector
        """
        if not self.is_fitted():
            raise RuntimeError(MODEL_NOT_FITTED)
        return PgxFrame(java_handler(self._model.inferGraphletVector, [graph._graph]))

    def infer_graphlet_vector_batched(self, graph: PgxGraph) -> PgxFrame:
        """Return the inferred vectors of the input graphlets as a PgxFrame.

        :param graph: graphlets (as a single graph but different graphlet-id) for which to infer
            vectors
        """
        if not self.is_fitted():
            raise RuntimeError(MODEL_NOT_FITTED)
        return PgxFrame(java_handler(self._model.inferGraphletVectorBatched, [graph._graph]))

    def compute_similars(
        self, graphlet_id: Union[Iterable[Union[int, str]], int, str], k: int
    ) -> PgxFrame:
        """Compute the top-k similar graphlets for a list of input graphlets.

        :param graphlet_id: graphletIds or iterable of graphletIds
        :param k: number of similars to return
        """
        if not self.is_fitted():
            raise RuntimeError(MODEL_NOT_FITTED)
        if isinstance(graphlet_id, (int, str)):
            # Pass on `graphlet_id` and `k` directly to Java.
            return self._compute_similars(str(graphlet_id), k)
        if isinstance(graphlet_id, collections.abc.Iterable):
            # Convert `graphlet_id` from a Python iterable to a Java ArrayList before passing it on.
            ids = autoclass('java.util.ArrayList')()
            for i in graphlet_id:
                if not isinstance(i, (int, str)):
                    raise TypeError(VERTEX_ID_OR_COLLECTION_OF_IDS.format(var='graphlet_id'))
                ids.add(str(i))
            return self._compute_similars_list(ids, k)
        raise TypeError(VERTEX_ID_OR_COLLECTION_OF_IDS.format(var='graphlet_id'))

    def _compute_similars(self, v, k: int) -> PgxFrame:
        return PgxFrame(java_handler(self._model.computeSimilars, [v, k]))

    def _compute_similars_list(self, v, k: int) -> PgxFrame:
        return PgxFrame(java_handler(PyjniusHelper.computeSimilarsList, [self._model, v, k]))

    def __repr__(self) -> str:
        if self.graph is not None:
            return "{}(graph: {}, loss: {}, vector dimension: {})".format(
                self.__class__.__name__, self.graph.name, self.loss, self.layer_size
            )
        else:
            return self.__class__.__name__

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._model.equals(other._model)
