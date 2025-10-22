#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from collections.abc import Iterable
from jnius import autoclass, JavaException
from pypgx._utils.error_handling import java_handler
from pypgx._utils.error_messages import MODEL_NOT_FITTED, VERTEX_ID_OR_COLLECTION_OF_IDS

from pypgx.api.frames import PgxFrame
from pypgx.api.mllib._model import Model
from pypgx._utils.pyjnius_helper import PyjniusHelper
from pypgx.api._pgx_graph import PgxGraph
from typing import List, Optional, Union


class DeepWalkModel(Model):
    """DeepWalk model object."""

    _java_class = 'oracle.pgx.api.mllib.DeepWalkModel'

    def __init__(self, java_deepwalk_model) -> None:
        self._model = java_deepwalk_model
        super().__init__(self._model)
        self.graph: Optional[PgxGraph] = None

        # Determining whether the model has been fitted is relevant especially for
        # models that are being loaded from a file.

    def is_fitted(self) -> bool:
        """Whether or not the model has been fitted."""
        return self.loss is not None

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
        """Get the number of walks per vertex."""
        return self._model.getWalksPerVertex()

    @property
    def sample_rate(self) -> float:
        """Get the sample rate."""
        return self._model.getSampleRate()

    @property
    def negative_sample(self) -> int:
        """Get the negative sample."""
        return self._model.getNegativeSample()

    @property
    def enable_accelerator(self) -> bool:
        """Get whether the accelerator is used if available."""
        return self._model.isEnableAccelerator()

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
    def trained_vectors(self) -> PgxFrame:
        """Get the trained vertex vectors for the current DeepWalk model.

        :returns: PgxFrame object with the trained vertex vectors
        :rtype: PgxFrame
        """
        if not self.is_fitted():
            raise RuntimeError(MODEL_NOT_FITTED)
        return PgxFrame(java_handler(self._model.getTrainedVertexVectors, []))

    def compute_similars(self, v: Union[int, str, List[int], List[str]], k: int) -> PgxFrame:
        """Compute the top-k similar vertices for a given vertex.

        :param v: id of the vertex or list of vertex ids for which to compute the similar vertices
        :param k: number of similar vertices to return
        """
        if not self.is_fitted():
            raise RuntimeError(MODEL_NOT_FITTED)
        if isinstance(v, (int, str)):
            # Pass on `v` and `k` directly to Java.
            v = str(v)
            return self._compute_similars(v, k)
        if isinstance(v, Iterable):
            # Convert `v` from a Python iterable to a Java ArrayList before passing it on.
            vids = autoclass('java.util.ArrayList')()
            for i in v:
                if not isinstance(i, (int, str)):
                    raise TypeError(VERTEX_ID_OR_COLLECTION_OF_IDS.format(var='v'))
                vids.add(str(i))
            return self._compute_similars_list(vids, k)
        raise TypeError(VERTEX_ID_OR_COLLECTION_OF_IDS.format(var='v'))

    def _compute_similars(self, v, k: int) -> PgxFrame:
        return PgxFrame(java_handler(self._model.computeSimilars, [v, k]))

    def _compute_similars_list(self, v, k: int):
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
