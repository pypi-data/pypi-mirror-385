#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from typing import TYPE_CHECKING, Any, Iterable, List, Mapping, NoReturn, Optional, Tuple, Union

from jnius import autoclass

import pypgx._utils.algorithms_metadata as alg_metadata
from pypgx._utils import pgx_types
from pypgx._utils.arguments_validator import validate_arguments
from pypgx._utils.error_handling import java_handler
from pypgx._utils.error_messages import PROPERTY_NOT_FOUND, UNHASHABLE_TYPE
from pypgx.api._all_paths import AllPaths
from pypgx.api._matrix_factorization_model import MatrixFactorizationModel
from pypgx.api._partition import PgxPartition
from pypgx.api._pgx_collection import EdgeSequence, EdgeSet, VertexSequence, VertexSet
from pypgx.api._pgx_entity import PgxVertex
from pypgx.api._pgx_graph import BipartiteGraph, PgxGraph
from pypgx.api._pgx_map import PgxMap
from pypgx.api._pgx_path import PgxPath
from pypgx.api._property import EdgeProperty, VertexProperty
from pypgx.api.filters import EdgeFilter, VertexFilter
from pypgx.api.mllib import (
    CorruptionFunction,
    DeepWalkModel,
    EmbeddingTableConfig,
    GraphWiseAttentionLayerConfig,
    GraphWiseConvLayerConfig,
    GraphWiseDgiLayerConfig,
    GraphWiseDominantLayerConfig,
    GraphWiseEmbeddingConfig,
    GraphWisePredictionLayerConfig,
    GraphWiseValidationConfig,
    InputPropertyConfig,
    OneHotEncodingConfig,
    PermutationCorruption,
    Pg2vecModel,
    SupervisedEdgeWiseModel,
    SupervisedGraphWiseModel,
    UnsupervisedAnomalyDetectionGraphWiseModel,
    UnsupervisedEdgeWiseModel,
    UnsupervisedGraphWiseModel,
)
from pypgx.api.mllib._edge_combination_method import (
    ConcatEdgeCombinationMethod,
    ProductEdgeCombinationMethod,
)
from pypgx.api.mllib._loss_function import LossFunction, _get_loss_function
from pypgx.api.mllib._model_repo_builder import ModelRepositoryBuilder
from pypgx.api.mllib._model_utils import ModelLoader

if TYPE_CHECKING:
    # Don't import at runtime, to avoid circular imports.
    from pypgx.api._pgx_session import PgxSession


class Analyst:
    """The Analyst gives access to all built-in algorithms of PGX.

    Unlike some of the other classes inside this package, the Analyst is not stateless. It
    creates session-bound transient data to hold the result of algorithms and keeps track of them.
    """

    _java_class = "oracle.pgx.api.Analyst"

    def __init__(self, session: "PgxSession", java_analyst) -> None:
        self._analyst = java_analyst
        self.session = session

    def __repr__(self) -> str:
        return "{}(session id: {})".format(self.__class__.__name__, self.session.id)

    def __str__(self) -> str:
        return repr(self)

    def close(self) -> None:
        """Destroy without waiting for completion."""
        java_handler(self._analyst.close, [])

    def destroy(self) -> None:
        """Destroy with waiting for completion."""
        java_handler(self._analyst.destroy, [])

    def model_repository(self) -> ModelRepositoryBuilder:
        """Get model repository builder for CRUD access to model stores."""
        return ModelRepositoryBuilder(java_handler(self._analyst.modelRepository, []))

    def pg2vec_builder(
        self,
        graphlet_id_property_name: str,
        vertex_property_names: List[str],
        min_word_frequency: int = 1,
        batch_size: int = 128,
        num_epochs: int = 5,
        layer_size: int = 200,
        learning_rate: float = 0.04,
        min_learning_rate: float = 0.0001,
        window_size: int = 4,
        walk_length: int = 8,
        walks_per_vertex: int = 5,
        graphlet_size_property_name: str = "graphletSize-Pg2vec",
        use_graphlet_size: bool = True,
        seed: Optional[int] = None,
        enable_accelerator: bool = True,
    ) -> Pg2vecModel:
        """Build a pg2Vec model and return it.

        :param graphlet_id_property_name: Property name of the graphlet-id in the input graph
        :param vertex_property_names: Property names to consider for pg2vec model training
        :param min_word_frequency:  Minimum word frequency to consider before pruning
        :param batch_size:  Batch size for training the model
        :param num_epochs:  Number of epochs to train the model
        :param layer_size:  Number of dimensions for the output vectors
        :param learning_rate:  Initial learning rate
        :param min_learning_rate:  Minimum learning rate
        :param window_size:  Window size to consider while training the model
        :param walk_length:  Length of the walks
        :param walks_per_vertex:  Number of walks to consider per vertex
        :param graphlet_size_property_name: Property name for graphlet size
        :param use_graphlet_size:  Whether to use or not the graphlet size
        :param seed:  Seed
        :param enable_accelerator: Whether to use the accelerator if available
        :returns: Built Pg2Vec Model
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.pg2vec_builder)

        properties = autoclass("java.util.ArrayList")()
        for p in vertex_property_names:
            if not isinstance(p, str):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=p))
            properties.add(p)

        builder = self._analyst.pg2vecModelBuilder()
        java_handler(builder.setGraphLetIdPropertyName, [graphlet_id_property_name])
        java_handler(builder.setVertexPropertyNames, [properties])
        java_handler(builder.setMinWordFrequency, [min_word_frequency])
        java_handler(builder.setBatchSize, [batch_size])
        java_handler(builder.setNumEpochs, [num_epochs])
        java_handler(builder.setLayerSize, [layer_size])
        java_handler(builder.setLearningRate, [learning_rate])
        java_handler(builder.setMinLearningRate, [min_learning_rate])
        java_handler(builder.setWindowSize, [window_size])
        java_handler(builder.setWalkLength, [walk_length])
        java_handler(builder.setWalksPerVertex, [walks_per_vertex])
        java_handler(builder.setUseGraphletSize, [use_graphlet_size])
        java_handler(builder.setGraphletSizePropertyName, [graphlet_size_property_name])
        java_handler(builder.setEnableAccelerator, [enable_accelerator])
        if seed is not None:
            java_handler(builder.setSeed, [pgx_types.Long(seed)])
        model = java_handler(builder.build, [])
        return Pg2vecModel(model)

    def load_pg2vec_model(self, path: str, key: Optional[str]) -> Pg2vecModel:
        """Load an encrypted pg2vec model.

        :param path: Path to model
        :param key: The decryption key, or None if no encryption was used
        :returns: Loaded model
        """
        model = java_handler(self._analyst.loadPg2vecModel, [path, key])
        return Pg2vecModel(model)

    def get_pg2vec_model_loader(self) -> ModelLoader:
        """Return a ModelLoader that can be used for loading a Pg2vecModel.

        :returns: ModelLoader
        """
        return ModelLoader(
            self,
            self._analyst.loadPg2vecModel,
            lambda x: Pg2vecModel(x),
            "oracle.pgx.api.mllib.Pg2vecModel",
        )

    def deepwalk_builder(
        self,
        min_word_frequency: int = 1,
        batch_size: int = 128,
        num_epochs: int = 2,
        layer_size: int = 200,
        learning_rate: float = 0.025,
        min_learning_rate: float = 0.0001,
        window_size: int = 5,
        walk_length: int = 5,
        walks_per_vertex: int = 4,
        sample_rate: float = 0.0,
        negative_sample: int = 10,
        *,
        seed: Optional[int] = None,
        ignore_isolated: bool = True,
        enable_accelerator: bool = True,
    ) -> DeepWalkModel:
        """Build a DeepWalk model and return it.

        :param min_word_frequency: Minimum word frequency to consider before pruning
        :param batch_size:  Batch size for training the model
        :param num_epochs:  Number of epochs to train the model
        :param layer_size:  Number of dimensions for the output vectors
        :param learning_rate:  Initial learning rate
        :param min_learning_rate:  Minimum learning rate
        :param window_size:  Window size to consider while training the model
        :param walk_length:  Length of the walks
        :param walks_per_vertex:  Number of walks to consider per vertex
        :param sample_rate:  Sample rate
        :param negative_sample:  Number of negative samples
        :param seed:  Random seed for training the model
        :param ignore_isolated:   Whether to ignore isolated vertices. If false, pseudo-walks
            consisting of only the node itself will be inserted into the dataset.
        :param enable_accelerator: Whether to use the accelerator if available
        :returns: Built DeepWalk model

        .. versionchanged:: 23.4
            The ``ignore_isolated`` parameter has been added.
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.deepwalk_builder)

        builder = self._analyst.deepWalkModelBuilder()
        java_handler(builder.setMinWordFrequency, [min_word_frequency])
        java_handler(builder.setBatchSize, [batch_size])
        java_handler(builder.setNumEpochs, [num_epochs])
        java_handler(builder.setLayerSize, [layer_size])
        java_handler(builder.setLearningRate, [learning_rate])
        java_handler(builder.setMinLearningRate, [min_learning_rate])
        java_handler(builder.setWindowSize, [window_size])
        java_handler(builder.setWalkLength, [walk_length])
        java_handler(builder.setWalksPerVertex, [walks_per_vertex])
        java_handler(builder.setSampleRate, [sample_rate])
        java_handler(builder.setNegativeSample, [negative_sample])
        java_handler(builder.setIgnoreIsolated, [ignore_isolated])
        java_handler(builder.setEnableAccelerator, [enable_accelerator])
        if seed is not None:
            java_handler(builder.setSeed, [pgx_types.Long(seed)])
        model = java_handler(builder.build, [])
        return DeepWalkModel(model)

    def load_deepwalk_model(self, path: str, key: Optional[str]) -> DeepWalkModel:
        """Load an encrypted DeepWalk model.

        :param path: Path to model
        :param key: The decryption key, or None if no encryption was used
        :returns: Loaded model
        """
        model = java_handler(self._analyst.loadDeepWalkModel, [path, key])
        return DeepWalkModel(model)

    def get_deepwalk_model_loader(self) -> ModelLoader:
        """Return a ModelLoader that can be used for loading a DeepWalkModel.

        :returns: ModelLoader
        """
        return ModelLoader(
            self,
            self._analyst.loadDeepWalkModel,
            lambda x: DeepWalkModel(x),
            "oracle.pgx.api.mllib.DeepWalkModel",
        )

    def supervised_graphwise_builder(
        self,
        vertex_target_property_name: str,
        vertex_input_property_names: List[str] = [],
        edge_input_property_names: List[str] = [],
        target_vertex_labels: List[str] = [],
        loss_fn: Union[LossFunction, str] = "softmax_cross_entropy",
        batch_gen: str = "standard",
        batch_gen_params: List[Any] = [],
        pred_layer_config: Optional[Iterable[GraphWisePredictionLayerConfig]] = None,
        conv_layer_config: Optional[
            Union[Iterable[GraphWiseConvLayerConfig], Iterable[GraphWiseAttentionLayerConfig]]
        ] = None,
        vertex_input_property_configs: Optional[Iterable[InputPropertyConfig]] = None,
        edge_input_property_configs: Optional[Iterable[InputPropertyConfig]] = None,
        batch_size: int = 128,
        num_epochs: int = 3,
        learning_rate: float = 0.01,
        layer_size: int = 128,
        class_weights: Optional[Union[Mapping[str, float], Mapping[int, float]]] = None,
        seed: Optional[int] = None,
        weight_decay: float = 0.0,
        standardize: bool = False,
        normalize: bool = True,
        enable_accelerator: bool = True,
        validation_config: Optional[GraphWiseValidationConfig] = None,
    ) -> SupervisedGraphWiseModel:
        """Build a SupervisedGraphWise model and return it.

        :param vertex_target_property_name: Target property name
        :param vertex_input_property_names: Vertices Input feature names
        :param edge_input_property_names: Edges Input feature names
        :param target_vertex_labels: Set the target vertex labels for the algorithm.
            Only the related vertices need to have the target property.
            Training and inference will be done on the vertices with those labels
        :param loss_fn: Loss function. Supported: String ('softmax_cross_entropy',
            'sigmoid_cross_entropy') or LossFunction object
        :param batch_gen: Batch generator. Supported: 'standard', 'stratified_oversampling'
        :param batch_gen_params: List of parameters passed to the batch generator
        :param pred_layer_config: Prediction layer configuration as list of PredLayerConfig,
            or default if None
        :param conv_layer_config: Conv layer configuration as list of ConvLayerConfig,
            or default if None
        :param vertex_input_property_configs: Vertex input property configuration
            as list of InputPropertyConfig, or default if None
        :param edge_input_property_configs: Edge input property configuration
            as list of InputPropertyConfig, or default if None
        :param batch_size:  Batch size for training the model
        :param num_epochs:  Number of epochs to train the model
        :param learning_rate: Learning rate
        :param layer_size: Number of dimensions for the output vectors
        :param class_weights: Class weights to be used in the loss function.
            The loss for the corresponding class will be multiplied by the factor given in this map.
            If null, uniform class weights will be used.
        :param seed: Seed
        :param weight_decay: Weight decay
        :param standardize: apply batch normalization
        :param normalize: apply l2 normalization after each convolutional layer
        :param enable_accelerator: Whether to use the accelerator if available
        :param validation_config: Validation config, there will be no validation if None (Default)
        :returns: Built SupervisedGraphWise model
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.supervised_graphwise_builder)

        # create default config, useful when printing the model to see the config
        if pred_layer_config is None:
            pred_layer_config = [self.graphwise_pred_layer_config()]
            arguments["pred_layer_config"] = pred_layer_config
        if conv_layer_config is None:
            conv_layer_config = [self.graphwise_conv_layer_config()]
            arguments["conv_layer_config"] = conv_layer_config

        # convert vertices input properties to Java ArrayList<String>
        vertex_input_properties = autoclass("java.util.ArrayList")()
        for vertex_input_property_name in vertex_input_property_names:
            if not isinstance(vertex_input_property_name, str):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=vertex_input_property_name))
            vertex_input_properties.add(vertex_input_property_name)
        # convert edges input properties to Java ArrayList<String>
        edge_input_properties = autoclass("java.util.ArrayList")()
        for edge_input_property_name in edge_input_property_names:
            if not isinstance(edge_input_property_name, str):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=edge_input_property_name))
            edge_input_properties.add(edge_input_property_name)
        # convert vertex target labels to Java ArrayList<String>
        vertex_target_label_names = autoclass("java.util.ArrayList")()
        for target_vertex_label in target_vertex_labels:
            if not isinstance(target_vertex_label, str):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=target_vertex_label))
            vertex_target_label_names.add(target_vertex_label)

        builder = self._analyst.supervisedGraphWiseModelBuilder()

        # create a list of the Java objects of the pred layer configs
        pred_layer_configs = []
        for p_layer_config in pred_layer_config:
            if not isinstance(p_layer_config, GraphWisePredictionLayerConfig):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=p_layer_config))
            pred_layer_configs.append(p_layer_config._config)
        java_handler(builder.setPredictionLayerConfigs, pred_layer_configs)

        # create a list of the Java objects of the conv layer configs
        conv_layer_configs = []
        for c_layer_config in conv_layer_config:
            if not isinstance(c_layer_config, GraphWiseConvLayerConfig) and not isinstance(
                c_layer_config, GraphWiseAttentionLayerConfig
            ):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=c_layer_config))
            conv_layer_configs.append(c_layer_config._config)
        java_handler(builder.setConvLayerConfigs, conv_layer_configs)

        # create a list of the Java objects of the vertex input property configs
        if vertex_input_property_configs is not None:
            java_vertex_input_property_configs = []
            for v_input_config in vertex_input_property_configs:
                if not isinstance(v_input_config, InputPropertyConfig):
                    raise TypeError(PROPERTY_NOT_FOUND.format(prop=v_input_config))
                java_vertex_input_property_configs.append(v_input_config._config)
            java_handler(builder.setVertexInputPropertyConfigs, java_vertex_input_property_configs)

        # create a list of the Java objects of the edge input property configs
        if edge_input_property_configs is not None:
            java_edge_input_property_configs = []
            for e_input_config in edge_input_property_configs:
                if not isinstance(e_input_config, InputPropertyConfig):
                    raise TypeError(PROPERTY_NOT_FOUND.format(prop=e_input_config))
                java_edge_input_property_configs.append(e_input_config._config)
            java_handler(builder.setEdgeInputPropertyConfigs, java_edge_input_property_configs)

        if validation_config is not None:
            if not isinstance(validation_config, GraphWiseValidationConfig):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=validation_config))
            java_handler(builder.setValidationConfig, [validation_config._config])

        if isinstance(loss_fn, str):
            loss_fn = _get_loss_function(loss_fn)
        loss_fn_java_obj = autoclass(loss_fn._java_class)(*loss_fn._java_arg_list)
        java_handler(builder.setLossFunction, [loss_fn_java_obj])

        batch_gen_java_obj = pgx_types._check_and_get_value(
            "batch_gen", batch_gen, pgx_types.BATCH_GENERATORS
        )
        java_handler(builder.setBatchGenerator, [batch_gen_java_obj(*batch_gen_params)])

        # set the remaining parameters
        java_handler(builder.setBatchSize, [batch_size])
        java_handler(builder.setNumEpochs, [num_epochs])
        java_handler(builder.setLearningRate, [learning_rate])
        java_handler(builder.setWeightDecay, [weight_decay])
        java_handler(builder.setEmbeddingDim, [layer_size])
        java_handler(builder.setVertexInputPropertyNames, [vertex_input_properties])
        java_handler(builder.setEnableAccelerator, [enable_accelerator])
        if edge_input_property_names:
            java_handler(builder.setEdgeInputPropertyNames, [edge_input_properties])
        if target_vertex_labels:
            java_handler(builder.setTargetVertexLabels, [vertex_target_label_names])
        java_handler(builder.setVertexTargetPropertyName, [vertex_target_property_name])

        # convert the class weights to Map<?, Float> where the type of the key depends
        # on the type on the Python side
        if class_weights is not None:
            types = set()
            for _class in class_weights:
                types.add(type(_class))
            if len(types) > 1:
                raise ValueError("Keys in class weights have different types")

            class_type = list(types)[0]
            type_to_class = {
                int: pgx_types.Integer,
                bool: pgx_types.Boolean,
                str: pgx_types.String,
            }
            if class_type not in type_to_class:
                raise ValueError(
                    "Class weight (%s) not supported. Only %s are supported"
                    % (class_type, ", ".join(map(str, type_to_class.keys())))
                )

            java_class_weights = autoclass("java.util.HashMap")()
            for _class, _weight in class_weights.items():
                java_class = type_to_class[class_type](_class)
                java_weight = pgx_types.Float(_weight)
                java_handler(java_class_weights.put, [java_class, java_weight])
            java_handler(builder.setClassWeights, [java_class_weights])

        if seed is not None:
            java_handler(builder.setSeed, [pgx_types.Integer(seed)])
        java_handler(builder.setStandardize, [standardize])
        java_handler(builder.setNormalize, [normalize])
        model = java_handler(builder.build, [])
        return SupervisedGraphWiseModel(model, arguments)

    def supervised_edgewise_builder(
        self,
        edge_target_property_name: str,
        *,
        vertex_input_property_names: List[str] = [],
        edge_input_property_names: List[str] = [],
        target_edge_labels: List[str] = [],
        loss_fn: Union[LossFunction, str] = "softmax_cross_entropy",
        batch_gen: str = "standard",
        batch_gen_params: List[Any] = [],
        pred_layer_config: Optional[Iterable[GraphWisePredictionLayerConfig]] = None,
        conv_layer_config: Optional[
            Union[Iterable[GraphWiseConvLayerConfig], Iterable[GraphWiseAttentionLayerConfig]]
        ] = None,
        vertex_input_property_configs: Optional[Iterable[InputPropertyConfig]] = None,
        edge_input_property_configs: Optional[Iterable[InputPropertyConfig]] = None,
        batch_size: int = 128,
        num_epochs: int = 3,
        learning_rate: float = 0.01,
        layer_size: int = 128,
        class_weights: Optional[Union[Mapping[str, float], Mapping[int, float]]] = None,
        seed: Optional[int] = None,
        weight_decay: float = 0.0,
        standardize: bool = False,
        normalize: bool = True,
        edge_combination_method: Optional[
            Union[
                ConcatEdgeCombinationMethod,
                ProductEdgeCombinationMethod,
            ]
        ] = None,
        enable_accelerator: bool = True,
        validation_config: Optional[GraphWiseValidationConfig] = None,
    ) -> SupervisedEdgeWiseModel:
        """Build a SupervisedEdgeWise model and return it.

        :param edge_target_property_name: Target property name
        :param vertex_input_property_names: Vertices Input feature names
        :param edge_input_property_names: Edges Input feature names
        :param target_edge_labels: Set the target edge labels for the algorithm.
            Only the related edges need to have the target property.
            Training and inference will be done on the edges with those labels
        :param loss_fn: Loss function. Supported: String ('softmax_cross_entropy',
            'sigmoid_cross_entropy') or LossFunction object
        :param batch_gen: Batch generator. Supported: 'standard', 'stratified_oversampling'
        :param batch_gen_params: List of parameters passed to the batch generator
        :param pred_layer_config: Prediction layer configuration as list of PredLayerConfig,
            or default if None
        :param conv_layer_config: Conv layer configuration as list of ConvLayerConfig,
            or default if None
        :param vertex_input_property_configs: Vertex input property configuration as
            list of InputPropertyConfig, or default if None
        :param edge_input_property_configs: Edge input property configuration as
            list of InputPropertyConfig, or default if None
        :param batch_size:  Batch size for training the model
        :param num_epochs:  Number of epochs to train the model
        :param learning_rate: Learning rate
        :param layer_size: Number of dimensions for the output vectors
        :param class_weights: Class weights to be used in the loss function.
            The loss for the corresponding class will be multiplied by the factor given in this map.
            If None, uniform class weights will be used.
        :param seed: Seed
        :param weight_decay: Weight decay
        :param standardize: apply batch normalization
        :param normalize: apply l2 normalization after each convolutional layer
        :param edge_combination_method: combination method to apply to vertex embeddings and edge
            features to compute the edge embedding
        :param enable_accelerator: Whether to use the accelerator if available
        :param validation_config: Validation config, there will be no validation if None (Default)
        :returns: Built SupervisedEdgeWise model
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.supervised_edgewise_builder)

        # create default config, useful when printing the model to see the config
        if pred_layer_config is None:
            pred_layer_config = [self.graphwise_pred_layer_config()]
            arguments["pred_layer_config"] = pred_layer_config
        if conv_layer_config is None:
            conv_layer_config = [self.graphwise_conv_layer_config()]
            arguments["conv_layer_config"] = conv_layer_config

        # convert vertices input properties to Java ArrayList<String>
        vertex_input_properties = autoclass("java.util.ArrayList")()
        for vertex_input_property_name in vertex_input_property_names:
            if not isinstance(vertex_input_property_name, str):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=vertex_input_property_name))
            vertex_input_properties.add(vertex_input_property_name)
        # convert edges input properties to Java ArrayList<String>
        edge_input_properties = autoclass("java.util.ArrayList")()
        for edge_input_property_name in edge_input_property_names:
            if not isinstance(edge_input_property_name, str):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=edge_input_property_name))
            edge_input_properties.add(edge_input_property_name)
        # convert edge target labels to Java ArrayList<String>
        edge_target_label_names = autoclass("java.util.ArrayList")()
        for target_edge_label in target_edge_labels:
            if not isinstance(target_edge_label, str):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=target_edge_label))
            edge_target_label_names.add(target_edge_label)

        builder = self._analyst.supervisedEdgeWiseModelBuilder()

        # create a list of the Java objects of the pred layer configs
        pred_layer_configs = []
        for p_layer_config in pred_layer_config:
            if not isinstance(p_layer_config, GraphWisePredictionLayerConfig):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=p_layer_config))
            pred_layer_configs.append(p_layer_config._config)
        java_handler(builder.setPredictionLayerConfigs, pred_layer_configs)

        # create a list of the Java objects of the conv layer configs
        conv_layer_configs = []
        for c_layer_config in conv_layer_config:
            if not isinstance(c_layer_config, GraphWiseConvLayerConfig) and not isinstance(
                c_layer_config, GraphWiseAttentionLayerConfig
            ):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=c_layer_config))
            conv_layer_configs.append(c_layer_config._config)
        java_handler(builder.setConvLayerConfigs, conv_layer_configs)

        # create a list of the Java objects of the vertex input property configs
        if vertex_input_property_configs is not None:
            java_vertex_input_property_configs = []
            for v_input_config in vertex_input_property_configs:
                if not isinstance(v_input_config, InputPropertyConfig):
                    raise TypeError(PROPERTY_NOT_FOUND.format(prop=v_input_config))
                java_vertex_input_property_configs.append(v_input_config._config)
            java_handler(builder.setVertexInputPropertyConfigs, java_vertex_input_property_configs)

        # create a list of the Java objects of the edge input property configs
        if edge_input_property_configs is not None:
            java_edge_input_property_configs = []
            for e_input_config in edge_input_property_configs:
                if not isinstance(e_input_config, InputPropertyConfig):
                    raise TypeError(PROPERTY_NOT_FOUND.format(prop=e_input_config))
                java_edge_input_property_configs.append(e_input_config._config)
            java_handler(builder.setEdgeInputPropertyConfigs, java_edge_input_property_configs)

        if validation_config is not None:
            if not isinstance(validation_config, GraphWiseValidationConfig):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=validation_config))
            java_handler(builder.setValidationConfig, [validation_config._config])

        if isinstance(loss_fn, str):
            loss_fn = _get_loss_function(loss_fn)
        loss_fn_java_obj = autoclass(loss_fn._java_class)(*loss_fn._java_arg_list)
        java_handler(builder.setLossFunction, [loss_fn_java_obj])

        batch_gen_java_obj = pgx_types._check_and_get_value(
            "batch_gen", batch_gen, pgx_types.BATCH_GENERATORS
        )
        java_handler(builder.setBatchGenerator, [batch_gen_java_obj(*batch_gen_params)])

        # set the remaining parameters
        java_handler(builder.setBatchSize, [batch_size])
        java_handler(builder.setNumEpochs, [num_epochs])
        java_handler(builder.setLearningRate, [learning_rate])
        java_handler(builder.setWeightDecay, [weight_decay])
        java_handler(builder.setEmbeddingDim, [layer_size])
        java_handler(builder.setVertexInputPropertyNames, [vertex_input_properties])
        if edge_input_property_names:
            java_handler(builder.setEdgeInputPropertyNames, [edge_input_properties])
        if target_edge_labels:
            java_handler(builder.setTargetEdgeLabels, [edge_target_label_names])
        java_handler(builder.setEdgeTargetPropertyName, [edge_target_property_name])
        java_handler(builder.setEnableAccelerator, [enable_accelerator])

        # convert the class weights to Map<?, Float> where the type of the key depends
        # on the type on the Python side
        if class_weights is not None:
            types = set()
            for _class in class_weights:
                types.add(type(_class))
            if len(types) > 1:
                raise ValueError("Keys in class weights have different types")

            class_type = list(types)[0]
            type_to_class = {
                int: pgx_types.Integer,
                bool: pgx_types.Boolean,
                str: pgx_types.String,
            }
            if class_type not in type_to_class:
                raise ValueError(
                    "Class weight (%s) not supported. Only %s are supported"
                    % (class_type, ", ".join(map(str, type_to_class.keys())))
                )

            java_class_weights = autoclass("java.util.HashMap")()
            for _class, _weight in class_weights.items():
                java_class = type_to_class[class_type](_class)
                java_weight = pgx_types.Float(_weight)
                java_handler(java_class_weights.put, [java_class, java_weight])
            java_handler(builder.setClassWeights, [java_class_weights])

        if seed is not None:
            java_handler(builder.setSeed, [pgx_types.Integer(seed)])
        java_handler(builder.setStandardize, [standardize])
        java_handler(builder.setNormalize, [normalize])

        if edge_combination_method:
            if not isinstance(
                edge_combination_method, (ConcatEdgeCombinationMethod, ProductEdgeCombinationMethod)
            ):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=edge_combination_method))
            comb_method_java_obj = autoclass(edge_combination_method._java_class)(
                *edge_combination_method._java_arg_list
            )
            java_handler(builder.setEdgeCombinationMethod, [comb_method_java_obj])

        model = java_handler(builder.build, [])
        return SupervisedEdgeWiseModel(model, arguments)

    def load_supervised_graphwise_model(
        self, path: str, key: Optional[str]
    ) -> SupervisedGraphWiseModel:
        """Load an encrypted SupervisedGraphWise model.

        :param path: Path to model
        :param key: The decryption key, or None if no encryption was used
        :returns: Loaded model
        """
        model = java_handler(self._analyst.loadSupervisedGraphWiseModel, [path, key])
        return SupervisedGraphWiseModel(model)

    def load_supervised_edgewise_model(
        self, path: str, key: Optional[str]
    ) -> SupervisedEdgeWiseModel:
        """Load an encrypted SupervisedEdgeWise model.

        :param path: Path to model
        :param key: The decryption key, or None if no encryption was used
        :returns: Loaded model
        """
        model = java_handler(self._analyst.loadSupervisedEdgeWiseModel, [path, key])
        return SupervisedEdgeWiseModel(model)

    def get_supervised_graphwise_model_loader(self) -> ModelLoader:
        """Return a ModelLoader that can be used for loading a SupervisedGraphWiseModel.

        :returns: ModelLoader
        """
        return ModelLoader(
            self,
            self._analyst.loadSupervisedGraphWiseModel,
            lambda x: SupervisedGraphWiseModel(x),
            "oracle.pgx.api.mllib.SupervisedGraphWiseModel",
        )

    def get_supervised_edgewise_model_loader(self) -> ModelLoader:
        """Return a ModelLoader that can be used for loading a SupervisedEdgeWiseModel.

        :returns: ModelLoader
        """
        return ModelLoader(
            self,
            self._analyst.loadSupervisedEdgeWiseModel,
            lambda x: SupervisedEdgeWiseModel(x),
            "oracle.pgx.api.mllib.SupervisedEdgeWiseModel",
        )

    def unsupervised_edgewise_builder(
        self,
        *,
        vertex_input_property_names: List[str] = [],
        edge_input_property_names: List[str] = [],
        target_edge_labels: List[str] = [],
        loss_fn: str = "sigmoid_cross_entropy",
        conv_layer_config: Optional[
            Union[Iterable[GraphWiseConvLayerConfig], Iterable[GraphWiseAttentionLayerConfig]]
        ] = None,
        vertex_input_property_configs: Optional[Iterable[InputPropertyConfig]] = None,
        edge_input_property_configs: Optional[Iterable[InputPropertyConfig]] = None,
        batch_size: int = 128,
        num_epochs: int = 3,
        learning_rate: float = 0.01,
        layer_size: int = 128,
        dgi_layer_config: Optional[GraphWiseDgiLayerConfig] = None,
        seed: Optional[int] = None,
        weight_decay: float = 0.0,
        standardize: bool = False,
        normalize: bool = True,
        edge_combination_method: Optional[
            Union[
                ConcatEdgeCombinationMethod,
                ProductEdgeCombinationMethod,
            ]
        ] = None,
        enable_accelerator: bool = True,
        validation_config: Optional[GraphWiseValidationConfig] = None,
    ) -> UnsupervisedEdgeWiseModel:
        """Build a UnsupervisedEdgeWise model and return it.

        :param vertex_input_property_names: Vertices Input feature names
        :param edge_input_property_names: Edges Input feature names
        :param target_edge_labels: Set the target edge labels for the algorithm.
            Only the related edges need to have the target property.
            Training and inference will be done on the edges with those labels
        :param loss_fn: Loss function. Supported: String ('sigmoid_cross_entropy')
        :param conv_layer_config: Conv layer configuration as list of ConvLayerConfig,
            or default if None
        :param vertex_input_property_configs: Vertex input property configuration as
            list of InputPropertyConfig, or default if None
        :param edge_input_property_configs: Edge input property configuration as
            list of InputPropertyConfig, or default if None
        :param batch_size:  Batch size for training the model
        :param num_epochs:  Number of epochs to train the model
        :param learning_rate: Learning rate
        :param layer_size: Number of dimensions for the output vectors
        :param dgi_layer_config: Dgi layer configuration as DgiLayerConfig object,
            or default if None
        :param seed: Seed
        :param weight_decay: Weight decay
        :param standardize: apply batch normalization
        :param normalize: apply l2 normalization after each convolutional layer
        :param edge_combination_method: combination method to apply to vertex embeddings and edge
            features to compute the edge embedding
        :param enable_accelerator: Whether to use the accelerator if available
        :param validation_config: Validation config, there will be no validation if None (Default)
        :returns: Built SupervisedEdgeWise model
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.unsupervised_edgewise_builder)

        # create default config, useful when printing the model to see the config
        if conv_layer_config is None:
            conv_layer_config = [self.graphwise_conv_layer_config()]
            arguments["conv_layer_config"] = conv_layer_config

        if dgi_layer_config is None:
            dgi_layer_config = self.graphwise_dgi_layer_config()
            arguments["dgi_layer_config"] = dgi_layer_config

        # convert vertices input properties to Java ArrayList<String>
        vertex_input_properties = autoclass("java.util.ArrayList")()
        for vertex_input_property_name in vertex_input_property_names:
            if not isinstance(vertex_input_property_name, str):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=vertex_input_property_name))
            vertex_input_properties.add(vertex_input_property_name)
        # convert edges input properties to Java ArrayList<String>
        edge_input_properties = autoclass("java.util.ArrayList")()
        for edge_input_property_name in edge_input_property_names:
            if not isinstance(edge_input_property_name, str):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=edge_input_property_name))
            edge_input_properties.add(edge_input_property_name)
        # convert edge target labels to Java ArrayList<String>
        edge_target_label_names = autoclass("java.util.ArrayList")()
        for target_edge_label in target_edge_labels:
            if not isinstance(target_edge_label, str):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=target_edge_label))
            edge_target_label_names.add(target_edge_label)

        builder = self._analyst.unsupervisedEdgeWiseModelBuilder()

        # Set the dgi layer config
        if not isinstance(dgi_layer_config, GraphWiseDgiLayerConfig):
            raise TypeError(PROPERTY_NOT_FOUND.format(prop=dgi_layer_config))
        java_handler(builder.setDgiLayerConfig, [dgi_layer_config._config])

        # create a list of the Java objects of the conv layer configs
        conv_layer_configs = []
        for c_layer_config in conv_layer_config:
            if not isinstance(c_layer_config, GraphWiseConvLayerConfig) and not isinstance(
                c_layer_config, GraphWiseAttentionLayerConfig
            ):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=c_layer_config))
            conv_layer_configs.append(c_layer_config._config)
        java_handler(builder.setConvLayerConfigs, conv_layer_configs)

        # create a list of the Java objects of the vertex input property configs
        if vertex_input_property_configs is not None:
            java_vertex_input_property_configs = []
            for v_input_config in vertex_input_property_configs:
                if not isinstance(v_input_config, InputPropertyConfig):
                    raise TypeError(PROPERTY_NOT_FOUND.format(prop=v_input_config))
                java_vertex_input_property_configs.append(v_input_config._config)
            java_handler(builder.setVertexInputPropertyConfigs, java_vertex_input_property_configs)

        # create a list of the Java objects of the edge input property configs
        if edge_input_property_configs is not None:
            java_edge_input_property_configs = []
            for e_input_config in edge_input_property_configs:
                if not isinstance(e_input_config, InputPropertyConfig):
                    raise TypeError(PROPERTY_NOT_FOUND.format(prop=e_input_config))
                java_edge_input_property_configs.append(e_input_config._config)
            java_handler(builder.setEdgeInputPropertyConfigs, java_edge_input_property_configs)

        if validation_config is not None:
            if not isinstance(validation_config, GraphWiseValidationConfig):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=validation_config))
            java_handler(builder.setValidationConfig, [validation_config._config])

        loss_fn_java_obj = pgx_types._check_and_get_value(
            "loss_fn", loss_fn, pgx_types.UNSUPERVISED_EDGEWISE_LOSS_FUNCTIONS
        )
        java_handler(builder.setLossFunction, [loss_fn_java_obj])

        # set the remaining parameters
        java_handler(builder.setBatchSize, [batch_size])
        java_handler(builder.setNumEpochs, [num_epochs])
        java_handler(builder.setLearningRate, [learning_rate])
        java_handler(builder.setWeightDecay, [weight_decay])
        java_handler(builder.setEmbeddingDim, [layer_size])
        java_handler(builder.setVertexInputPropertyNames, [vertex_input_properties])
        if edge_input_property_names:
            java_handler(builder.setEdgeInputPropertyNames, [edge_input_properties])
        if target_edge_labels:
            java_handler(builder.setTargetEdgeLabels, [edge_target_label_names])

        if seed is not None:
            java_handler(builder.setSeed, [pgx_types.Integer(seed)])
        java_handler(builder.setStandardize, [standardize])
        java_handler(builder.setNormalize, [normalize])
        java_handler(builder.setEnableAccelerator, [enable_accelerator])

        if edge_combination_method:
            if not isinstance(
                edge_combination_method, (ConcatEdgeCombinationMethod, ProductEdgeCombinationMethod)
            ):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=edge_combination_method))
            comb_method_java_obj = autoclass(edge_combination_method._java_class)(
                *edge_combination_method._java_arg_list
            )
            java_handler(builder.setEdgeCombinationMethod, [comb_method_java_obj])

        model = java_handler(builder.build, [])
        return UnsupervisedEdgeWiseModel(model, arguments)

    def load_unsupervised_edgewise_model(
        self, path: str, key: Optional[str]
    ) -> UnsupervisedEdgeWiseModel:
        """Load an encrypted UnsupervisedEdgeWise model.

        :param path: Path to model
        :param key: The decryption key, or None if no encryption was used
        :returns: Loaded model
        """
        model = java_handler(self._analyst.loadUnsupervisedEdgeWiseModel, [path, key])
        return UnsupervisedEdgeWiseModel(model)

    def get_unsupervised_edgewise_model_loader(self) -> ModelLoader:
        """Return a ModelLoader that can be used for loading a UnsupervisedEdgeWiseModel.

        :returns: ModelLoader
        """
        return ModelLoader(
            self,
            self._analyst.loadUnsupervisedEdgeWiseModel,
            lambda x: UnsupervisedEdgeWiseModel(x),
            "oracle.pgx.api.mllib.UnsupervisedEdgeWiseModel",
        )

    def unsupervised_graphwise_builder(
        self,
        vertex_input_property_names: List[str] = [],
        edge_input_property_names: List[str] = [],
        target_vertex_labels: List[str] = [],
        loss_fn: str = "sigmoid_cross_entropy",
        conv_layer_config: Optional[
            Union[Iterable[GraphWiseConvLayerConfig], Iterable[GraphWiseAttentionLayerConfig]]
        ] = None,
        vertex_input_property_configs: Optional[Iterable[InputPropertyConfig]] = None,
        edge_input_property_configs: Optional[Iterable[InputPropertyConfig]] = None,
        batch_size: int = 128,
        num_epochs: int = 3,
        learning_rate: float = 0.001,
        layer_size: int = 128,
        seed: Optional[int] = None,
        dgi_layer_config: Optional[GraphWiseDgiLayerConfig] = None,
        weight_decay: float = 0.0,
        standardize: bool = False,
        embedding_config: Optional[GraphWiseEmbeddingConfig] = None,
        normalize: bool = True,
        enable_accelerator: bool = True,
        validation_config: Optional[GraphWiseValidationConfig] = None,
    ) -> UnsupervisedGraphWiseModel:
        """Build a UnsupervisedGraphWise model and return it.

        :param vertex_input_property_names: Vertices Input feature names
        :param edge_input_property_names: Edges Input feature names
        :param target_vertex_labels: Set the target vertex labels for the algorithm.
            Only the related vertices need to have the target property.
            Training and inference will be done on the vertices with those labels
        :param loss_fn: Loss function. Supported: sigmoid_cross_entropy
        :param conv_layer_config: Conv layer configuration as list of ConvLayerConfig,
            or default if None
        :param vertex_input_property_configs: Vertex input property configuration as
            list of InputPropertyConfig, or default if None
        :param edge_input_property_configs: Edge input property configuration as
            list of InputPropertyConfig, or default if None
        :param batch_size:  Batch size for training the model
        :param num_epochs:  Number of epochs to train the model
        :param learning_rate: Learning rate
        :param layer_size: Number of dimensions for the output vectors
        :param seed: Seed
        :param dgi_layer_config: Dgi layer configuration as DgiLayerConfig object,
            or default if None
        :param weight_decay: weight decay
        :param standardize: apply batch normalization
        :param embedding_config: te embedding configuration as a GraphWiseEmbeddingConfig object,
            default is None
        :param normalize: apply l2 normalization after each convolutional layer
        :param enable_accelerator: Whether to use the accelerator if available
        :param validation_config: Validation config, there will be no validation if None (Default)
        :returns: Built UnsupervisedGraphWise model
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.unsupervised_graphwise_builder)

        # create default config, useful when printing the model to see the config

        if dgi_layer_config is None:
            dgi_layer_config = self.graphwise_dgi_layer_config()
            arguments["dgi_layer_config"] = dgi_layer_config

        if embedding_config is None:
            embedding_config = self.graphwise_dgi_layer_config()
            arguments["embedding_config"] = embedding_config

        if conv_layer_config is None:
            conv_layer_config = [self.graphwise_conv_layer_config()]
            arguments["conv_layer_config"] = conv_layer_config

        # convert vertices input properties to Java ArrayList<String>
        input_properties = autoclass("java.util.ArrayList")()
        for p in vertex_input_property_names:
            if not isinstance(p, str):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=p))
            input_properties.add(p)

        # convert edges input properties to Java ArrayList<String>
        edge_input_properties = autoclass("java.util.ArrayList")()
        for p in edge_input_property_names:
            if not isinstance(p, str):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=p))
            edge_input_properties.add(p)
        # convert vertex target labels to Java ArrayList<String>
        vertex_target_label_names = autoclass("java.util.ArrayList")()
        for p in target_vertex_labels:
            if not isinstance(p, str):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=p))
            vertex_target_label_names.add(p)

        builder = self._analyst.unsupervisedGraphWiseModelBuilder()

        # Set the dgi layer config
        if not isinstance(dgi_layer_config, GraphWiseDgiLayerConfig):
            raise TypeError(PROPERTY_NOT_FOUND.format(prop=dgi_layer_config))
        java_handler(builder.setDgiLayerConfig, [dgi_layer_config._config])
        java_handler(builder.setEmbeddingConfig, [embedding_config._get_config()])

        # create a list of the Java objects of the conv layer configs
        conv_layer_configs = []
        for c_layer_config in conv_layer_config:
            if not isinstance(c_layer_config, GraphWiseConvLayerConfig) and not isinstance(
                c_layer_config, GraphWiseAttentionLayerConfig
            ):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=c_layer_config))
            conv_layer_configs.append(c_layer_config._config)
        java_handler(builder.setConvLayerConfigs, conv_layer_configs)

        # create a list of the Java objects of the vertex input property configs
        if vertex_input_property_configs is not None:
            java_vertex_input_property_configs = []
            for v_input_config in vertex_input_property_configs:
                if not isinstance(v_input_config, InputPropertyConfig):
                    raise TypeError(PROPERTY_NOT_FOUND.format(prop=v_input_config))
                java_vertex_input_property_configs.append(v_input_config._config)
            java_handler(builder.setVertexInputPropertyConfigs, java_vertex_input_property_configs)

        # create a list of the Java objects of the edge input property configs
        if edge_input_property_configs is not None:
            java_edge_input_property_configs = []
            for e_input_config in edge_input_property_configs:
                if not isinstance(e_input_config, InputPropertyConfig):
                    raise TypeError(PROPERTY_NOT_FOUND.format(prop=e_input_config))
                java_edge_input_property_configs.append(e_input_config._config)
            java_handler(builder.setEdgeInputPropertyConfigs, java_edge_input_property_configs)

        if validation_config is not None:
            if not isinstance(validation_config, GraphWiseValidationConfig):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=validation_config))
            java_handler(builder.setValidationConfig, [validation_config._config])

        loss_fn_java_obj = pgx_types._check_and_get_value(
            "loss_fn", loss_fn, pgx_types.UNSUPERVISED_LOSS_FUNCTIONS
        )
        java_handler(builder.setLossFunction, [loss_fn_java_obj])

        # set the remaining parameters
        java_handler(builder.setBatchSize, [batch_size])
        java_handler(builder.setNumEpochs, [num_epochs])
        java_handler(builder.setLearningRate, [learning_rate])
        java_handler(builder.setWeightDecay, [weight_decay])
        java_handler(builder.setEmbeddingDim, [layer_size])
        java_handler(builder.setVertexInputPropertyNames, [input_properties])
        if edge_input_property_names:
            java_handler(builder.setEdgeInputPropertyNames, [edge_input_properties])
        if target_vertex_labels:
            java_handler(builder.setTargetVertexLabels, [vertex_target_label_names])

        if seed is not None:
            java_handler(builder.setSeed, [pgx_types.Integer(seed)])
        java_handler(builder.setStandardize, [standardize])
        java_handler(builder.setNormalize, [normalize])
        java_handler(builder.setEnableAccelerator, [enable_accelerator])
        model = java_handler(builder.build, [])
        return UnsupervisedGraphWiseModel(model, arguments)

    def unsupervised_anomaly_detection_graphwise_builder(
        self,
        vertex_input_property_names: List[str] = [],
        edge_input_property_names: List[str] = [],
        target_vertex_labels: List[str] = [],
        loss_fn: str = "sigmoid_cross_entropy",
        conv_layer_config: Optional[Iterable[GraphWiseConvLayerConfig]] = None,
        vertex_input_property_configs: Optional[Iterable[InputPropertyConfig]] = None,
        edge_input_property_configs: Optional[Iterable[InputPropertyConfig]] = None,
        batch_size: int = 128,
        num_epochs: int = 3,
        learning_rate: float = 0.001,
        layer_size: int = 128,
        seed: Optional[int] = None,
        weight_decay: float = 0.0,
        standardize: bool = False,
        embedding_config: Optional[GraphWiseEmbeddingConfig] = None,
        enable_accelerator: bool = True,
    ) -> UnsupervisedAnomalyDetectionGraphWiseModel:
        """Build a UnsupervisedAnomalyDetectionGraphWiseModel model and return it.

        :param vertex_input_property_names: Vertices Input feature names
        :param edge_input_property_names: Edges Input feature names
        :param target_vertex_labels: Set the target vertex labels for the algorithm.
            Only the related vertices need to have the target property.
            Training and inference will be done on the vertices with those labels
        :param loss_fn: Loss function. Supported: sigmoid_cross_entropy
        :param conv_layer_config: Conv layer configuration as list of ConvLayerConfig,
            or default if None
        :param vertex_input_property_configs: Vertex input property configuration as
            list of InputPropertyConfig, or default if None
        :param edge_input_property_configs: Edge input property configuration as
            list of InputPropertyConfig, or default if None
        :param batch_size:  Batch size for training the model
        :param num_epochs:  Number of epochs to train the model
        :param learning_rate: Learning rate
        :param layer_size: Number of dimensions for the output vectors
        :param seed: Seed
        :param weight_decay: weight decay
        :param standardize: apply batch normalization
        :param embedding_config: te embedding configuration as a GraphWiseEmbeddingConfig object,
            default is None
        :param enable_accelerator: Whether to use the accelerator if available
        :returns: Built UnsupervisedAnomalyDetectionGraphWiseModel model
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.unsupervised_graphwise_builder)

        # create default config, useful when printing the model to see the config

        if embedding_config is None:
            embedding_config = self.graphwise_dgi_layer_config()
            arguments["embedding_config"] = embedding_config

        if conv_layer_config is None:
            conv_layer_config = [self.graphwise_conv_layer_config()]
            arguments["conv_layer_config"] = conv_layer_config

        # convert vertices input properties to Java ArrayList<String>
        input_properties = autoclass("java.util.ArrayList")()
        for p in vertex_input_property_names:
            if not isinstance(p, str):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=p))
            input_properties.add(p)

        # convert edges input properties to Java ArrayList<String>
        edge_input_properties = autoclass("java.util.ArrayList")()
        for p in edge_input_property_names:
            if not isinstance(p, str):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=p))
            edge_input_properties.add(p)
        # convert vertex target labels to Java ArrayList<String>
        vertex_target_label_names = autoclass("java.util.ArrayList")()
        for p in target_vertex_labels:
            if not isinstance(p, str):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=p))
            vertex_target_label_names.add(p)

        builder = self._analyst.unsupervisedAnomalyDetectionGraphWiseModelBuilder()

        # create a list of the Java objects of the conv layer configs
        conv_layer_configs = []
        for layer_config in conv_layer_config:
            if not isinstance(layer_config, GraphWiseConvLayerConfig):
                raise TypeError(PROPERTY_NOT_FOUND.format(prop=layer_config))
            conv_layer_configs.append(layer_config._config)
        java_handler(builder.setConvLayerConfigs, conv_layer_configs)

        # create a list of the Java objects of the vertex input property configs
        if vertex_input_property_configs is not None:
            java_vertex_input_property_configs = []
            for v_input_config in vertex_input_property_configs:
                if not isinstance(v_input_config, InputPropertyConfig):
                    raise TypeError(PROPERTY_NOT_FOUND.format(prop=v_input_config))
                java_vertex_input_property_configs.append(v_input_config._config)
            java_handler(builder.setVertexInputPropertyConfigs, java_vertex_input_property_configs)

        # create a list of the Java objects of the edge input property configs
        if edge_input_property_configs is not None:
            java_edge_input_property_configs = []
            for e_input_config in edge_input_property_configs:
                if not isinstance(e_input_config, InputPropertyConfig):
                    raise TypeError(PROPERTY_NOT_FOUND.format(prop=e_input_config))
                java_edge_input_property_configs.append(e_input_config._config)
            java_handler(builder.setEdgeInputPropertyConfigs, java_edge_input_property_configs)

        loss_fn_java_obj = pgx_types._check_and_get_value(
            "loss_fn", loss_fn, pgx_types.UNSUPERVISED_LOSS_FUNCTIONS
        )
        java_handler(builder.setLossFunction, [loss_fn_java_obj])

        # set the remaining parameters
        java_handler(builder.setBatchSize, [batch_size])
        java_handler(builder.setNumEpochs, [num_epochs])
        java_handler(builder.setLearningRate, [learning_rate])
        java_handler(builder.setWeightDecay, [weight_decay])
        java_handler(builder.setEmbeddingDim, [layer_size])
        java_handler(builder.setVertexInputPropertyNames, [input_properties])
        if edge_input_property_names:
            java_handler(builder.setEdgeInputPropertyNames, [edge_input_properties])
        if target_vertex_labels:
            java_handler(builder.setTargetVertexLabels, [vertex_target_label_names])

        if seed is not None:
            java_handler(builder.setSeed, [pgx_types.Integer(seed)])
        java_handler(builder.setStandardize, [standardize])
        java_handler(builder.setEnableAccelerator, [enable_accelerator])
        model = java_handler(builder.build, [])
        return UnsupervisedAnomalyDetectionGraphWiseModel(model, arguments)

    def get_unsupervised_anomaly_detection_graphwise_loader(self) -> ModelLoader:
        """Return a ModelLoader that can be used for loading a UnsupervisedAnomalyDetectionGraphWiseModel.

        :returns: ModelLoader
        """
        return ModelLoader(
            self,
            self._analyst.loadUnsupervisedAnomalyDetectionGraphWiseModel,
            lambda x: UnsupervisedAnomalyDetectionGraphWiseModel(x),
            "oracle.pgx.api.mllib.UnsupervisedAnomalyDetectionGraphWiseModel",
        )

    def load_unsupervised_graphwise_model(self, path: str, key: str) -> UnsupervisedGraphWiseModel:
        """Load an encrypted UnsupervisedGraphWise model.

        :param path: Path to model
        :param key: The decryption key, or null if no encryption was used
        :returns: Loaded model
        """
        model = java_handler(self._analyst.loadUnsupervisedGraphWiseModel, [path, key])
        return UnsupervisedGraphWiseModel(model)

    def get_unsupervised_graphwise_model_loader(self) -> ModelLoader:
        """Return a ModelLoader that can be used for loading a UnsupervisedGraphWiseModel.

        :returns: ModelLoader
        """
        return ModelLoader(
            self,
            self._analyst.loadUnsupervisedGraphWiseModel,
            lambda x: UnsupervisedGraphWiseModel(x),
            "oracle.pgx.api.mllib.UnsupervisedGraphWiseModel",
        )

    def graphwise_validation_config(
        self,
        evaluation_frequency: int = 1,
        evaluation_frequency_scale: str = "epoch",
    ) -> GraphWiseValidationConfig:
        """Build a GraphWise validation configuration and return it.

        :param evaluation_frequency: Specifies how often the validation is performed.
        :param evaluation_frequency_scale: Decides the scale of the frequency value.
            Supported values are epoch and step.
        :returns: Built GraphWiseValidationConfig
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.graphwise_validation_config)

        builder = self._analyst.graphWiseValidationConfigBuilder()

        java_handler(builder.setEvaluationFrequency, [evaluation_frequency])

        eval_freq_scale_java_obj = pgx_types._check_and_get_value(
            "evaluation_frequency_scale",
            evaluation_frequency_scale,
            pgx_types.EVALUATION_FREQUENCY_SCALE
        )
        java_handler(builder.setEvaluationFrequencyScale, [eval_freq_scale_java_obj])

        config = java_handler(builder.build, [])
        return GraphWiseValidationConfig(config, arguments)

    def graphwise_pred_layer_config(
        self,
        hidden_dim: Optional[int] = None,
        activation_fn: str = "relu",
        weight_init_scheme: str = "xavier_uniform",
        dropout_rate: float = 0.0,
    ) -> GraphWisePredictionLayerConfig:
        """Build a GraphWise prediction layer configuration and return it.

        :param hidden_dim: Hidden dimension. If this is the last layer, this setting
            will be ignored and replaced by the number of classes.
        :param activation_fn: Activation function.
            Supported functions: relu, leaky_relu, tanh, linear.
            If this is the last layer, this setting will be ignored and replaced by
            the activation function of the loss function, e.g softmax or sigmoid.
        :param weight_init_scheme: Initialization scheme for the weights in the layer.
            Supportes schemes: xavier, xavier_uniform, ones, zeros.
            Note that biases are always initialized with zeros.
        :param dropout_rate: probability to drop each neuron.
        :returns: Built GraphWisePredictionLayerConfig
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.graphwise_pred_layer_config)

        builder = self._analyst.graphWisePredictionLayerConfigBuilder()

        if hidden_dim is not None:
            java_handler(builder.setHiddenDimension, [hidden_dim])

        activation_fn_java_obj = pgx_types._check_and_get_value(
            "activation_fn", activation_fn, pgx_types.ACTIVATION_FUNCTIONS
        )
        java_handler(builder.setActivationFunction, [activation_fn_java_obj])

        weight_init_scheme_java_obj = pgx_types._check_and_get_value(
            "weight_init_scheme", weight_init_scheme, pgx_types.WEIGHT_INIT_SCHEMES
        )
        java_handler(builder.setWeightInitScheme, [weight_init_scheme_java_obj])

        java_handler(builder.setDropoutRate, [dropout_rate])

        config = java_handler(builder.build, [])
        return GraphWisePredictionLayerConfig(config, arguments)

    def graphwise_conv_layer_config(
        self,
        num_sampled_neighbors: int = 10,
        neighbor_weight_property_name: Optional[str] = None,
        activation_fn: str = "relu",
        weight_init_scheme: str = "xavier_uniform",
        vertex_to_vertex_connection: bool = None,
        edge_to_vertex_connection: bool = None,
        vertex_to_edge_connection: bool = None,
        edge_to_edge_connection: bool = None,
        dropout_rate: float = 0.0,
    ) -> GraphWiseConvLayerConfig:
        """Build a GraphWise conv layer configuration and return it.

        :param num_sampled_neighbors: Number of neighbors to sample
        :param neighbor_weight_property_name: Neighbor weight property name.
        :param activation_fn: Activation function.
            Supported functions: relu, leaky_relu, tanh, linear.
            If this is the last layer, this setting will be ignored and replaced by
            the activation function of the loss function, e.g softmax or sigmoid.
        :param weight_init_scheme: Initialization scheme for the weights in the layer.
            Supported schemes: xavier, xavier_uniform, ones, zeros.
            Note that biases are always initialized with zeros.
        :param vertex_to_vertex_connection: Use the connection between vertices to vertices.
            Should be used only on heterogeneous graphs
        :param edge_to_vertex_connection: Use the connection between edges to vertices.
            Should be used only on heterogeneous graphs
        :param vertex_to_edge_connection: Use the connection between vertices to edges.
            Should be used only on heterogeneous graphs
        :param edge_to_edge_connection: Use the connection between edges to edges.
            Should be used only on heterogeneous graphs
        :param dropout_rate: probability to drop each neuron
        :returns: Built GraphWiseConvLayerConfig
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.graphwise_conv_layer_config)

        builder = self._analyst.graphWiseConvLayerConfigBuilder()

        java_handler(builder.setNumSampledNeighbors, [num_sampled_neighbors])
        if neighbor_weight_property_name is not None:
            java_handler(builder.setWeightedAggregationProperty, [neighbor_weight_property_name])

        activation_fn_java_obj = pgx_types._check_and_get_value(
            "activation_fn", activation_fn, pgx_types.ACTIVATION_FUNCTIONS
        )
        java_handler(builder.setActivationFunction, [activation_fn_java_obj])

        weight_init_scheme_java_obj = pgx_types._check_and_get_value(
            "weight_init_scheme", weight_init_scheme, pgx_types.WEIGHT_INIT_SCHEMES
        )
        java_handler(builder.setWeightInitScheme, [weight_init_scheme_java_obj])

        java_handler(builder.setDropoutRate, [dropout_rate])

        if vertex_to_edge_connection is not None:
            java_handler(builder.useVertexToEdgeConnection, [vertex_to_edge_connection])
        if edge_to_vertex_connection is not None:
            java_handler(builder.useEdgeToVertexConnection, [edge_to_vertex_connection])
        if vertex_to_vertex_connection is not None:
            java_handler(builder.useVertexToVertexConnection, [vertex_to_vertex_connection])
        if edge_to_edge_connection is not None:
            java_handler(builder.useEdgeToEdgeConnection, [edge_to_edge_connection])

        config = java_handler(builder.build, [])
        return GraphWiseConvLayerConfig(config, arguments)

    def learned_embedding_categorical_property_config(
        self,
        property_name: str = None,
        shared: bool = True,
        max_vocabulary_size: int = 10000,
        embedding_dim: int = None,
        oov_probability: float = 0.0,
    ) -> EmbeddingTableConfig:
        """Build a learned embedding table configuration for a categorical feature and return it.

        :param property_name: Name of the feature that the config will apply to
        :param shared: whether the feature is treated as shared globally among vertex/edge types
            or considered as separate features per type.
        :param max_vocabulary_size: Maximum vocabulary size for categories. The most frequent
            categories numbering "max_vocabulary_size"  are kept. Category values below
            this cutoff are not recorded and set to the OOV token.
        :param embedding_dim: the dimension of the vectors encoding categories
            in the embedding table.
        :param oov_probability: the probability to set category values in the input data
            to the OOV token randomly during training to learn a meaningful OOV embedding.
            This procedure is disabled during inference.
        :returns: Built EmbeddingTableConfig
        """
        arguments = locals()

        builder = java_handler(
            self._analyst.categoricalPropertyConfigBuilder, [property_name]
        ).embeddingTable()
        # any categorical properties
        java_handler(builder.setShared, [shared])
        java_handler(builder.setMaxVocabularySize, [max_vocabulary_size])
        # embedding table specific properties
        java_handler(builder.setOutOfVocabularyProbability, [oov_probability])
        if embedding_dim is not None:
            java_handler(builder.setEmbeddingDimension, [embedding_dim])

        config = java_handler(builder.build, [])
        return EmbeddingTableConfig(config, arguments)

    def one_hot_encoding_categorical_property_config(
        self,
        property_name: str = None,
        shared: bool = True,
        max_vocabulary_size: int = 10000,
    ) -> OneHotEncodingConfig:
        """Build a learned embedding table configuration for a categorical feature and return it.

        :param property_name: Name of the feature that the config will apply to
        :param shared: whether the feature is treated as shared globally among vertex/edge types
            or considered as separate features per type.
        :param max_vocabulary_size: Maximum vocabulary size for categories.
            The most frequent categories numbering "max_vocabulary_size" are kept.
            Category values below this cutoff are not recorded and set to the OOV token.
        :returns: Built OneHotEncodingConfig
        """
        arguments = locals()

        builder = java_handler(
            self._analyst.categoricalPropertyConfigBuilder, [property_name]
        ).oneHotEncoding()
        # any categorical properties
        java_handler(builder.setMaxVocabularySize, [max_vocabulary_size])
        java_handler(builder.setShared, [shared])

        config = java_handler(builder.build, [])
        return OneHotEncodingConfig(config, arguments)

    def graphwise_attention_layer_config(
        self,
        num_sampled_neighbors: int = 10,
        num_heads: int = 3,
        head_aggregation: str = "mean",
        activation_fn: str = "leaky_relu",
        weight_init_scheme: str = "xavier_uniform",
        vertex_to_vertex_connection: bool = None,
        edge_to_vertex_connection: bool = None,
        vertex_to_edge_connection: bool = None,
        edge_to_edge_connection: bool = None,
        dropout_rate: float = 0.0,
    ) -> GraphWiseAttentionLayerConfig:
        """Build a GraphWise attention layer configuration and return it.

        :param num_sampled_neighbors: Number of neighbors to sample
        :param num_heads: Number of heads to be used in this layer
        :param head_aggregation: Aggregation operation to be used in this layer
        :param activation_fn: Activation function.
            Supported functions: relu, leaky_relu, tanh, linear.
            If this is the last layer, this setting will be ignored and replaced by
            the activation function of the loss function, e.g softmax or sigmoid.
        :param weight_init_scheme: Initialization scheme for the weights in the layer.
            Supported schemes: xavier, xavier_uniform, ones, zeros.
            Note that biases are always initialized with zeros.
        :param vertex_to_vertex_connection: Use the connection between vertices to vertices.
            Should be used only on heterogeneous graphs
        :param edge_to_vertex_connection: Use the connection between edges to vertices.
            Should be used only on heterogeneous graphs
        :param vertex_to_edge_connection: Use the connection between vertices to edges.
            Should be used only on heterogeneous graphs
        :param edge_to_edge_connection: Use the connection between edges to edges.
            Should be used only on heterogeneous graphs
        :param dropout_rate: probability to drop each neuron
        :returns: Built GraphWiseAttentionLayerConfig
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.graphwise_attention_layer_config)

        builder = self._analyst.graphWiseAttentionLayerConfigBuilder()

        java_handler(builder.setNumSampledNeighbors, [num_sampled_neighbors])
        java_handler(builder.setNumHeads, [num_heads])

        activation_fn_java_obj = pgx_types._check_and_get_value(
            "activation_fn", activation_fn, pgx_types.ACTIVATION_FUNCTIONS
        )
        java_handler(builder.setActivationFunction, [activation_fn_java_obj])

        weight_init_scheme_java_obj = pgx_types._check_and_get_value(
            "weight_init_scheme", weight_init_scheme, pgx_types.WEIGHT_INIT_SCHEMES
        )
        java_handler(builder.setWeightInitScheme, [weight_init_scheme_java_obj])

        head_aggregation_java_obj = pgx_types._check_and_get_value(
            "head_aggregation", head_aggregation, pgx_types.AGGREGATION_OPERATION
        )
        java_handler(builder.setHeadAggregation, [head_aggregation_java_obj])

        java_handler(builder.setDropoutRate, [dropout_rate])

        if vertex_to_edge_connection is not None:
            java_handler(builder.useVertexToEdgeConnection, [vertex_to_edge_connection])
        if edge_to_vertex_connection is not None:
            java_handler(builder.useEdgeToVertexConnection, [edge_to_vertex_connection])
        if vertex_to_vertex_connection is not None:
            java_handler(builder.useVertexToVertexConnection, [vertex_to_vertex_connection])
        if edge_to_edge_connection is not None:
            java_handler(builder.useEdgeToEdgeConnection, [edge_to_edge_connection])

        config = java_handler(builder.build, [])
        return GraphWiseAttentionLayerConfig(config, arguments)

    def graphwise_dgi_layer_config(
        self,
        corruption_function: Optional[CorruptionFunction] = None,
        readout_function: str = "mean",
        discriminator: str = "bilinear",
    ) -> GraphWiseDgiLayerConfig:
        """Build a GraphWise DGI layer configuration and return it.

        :param corruption_function: Corruption Function to use
        :param readout_function: Neighbor weight property name.
            Supported functions: mean
        :param discriminator: discriminator function.
            Supported functions: bilinear
        :returns: GraphWiseDgiLayerConfig object
        """
        arguments = locals()

        if corruption_function is None:
            java_permutation_corruption = autoclass(
                "oracle.pgx.config.mllib.corruption.PermutationCorruption"
            )()
            corruption_function = PermutationCorruption(java_permutation_corruption)
            arguments["corruption_function"] = corruption_function

        validate_arguments(arguments, alg_metadata.graphwise_dgi_layer_config)

        builder = self._analyst.graphWiseDgiLayerConfigBuilder()

        java_handler(builder.setCorruptionFunction, [corruption_function._corruption_function])

        readout_function_java_obj = pgx_types._check_and_get_value(
            "readout_function", readout_function, pgx_types.READOUT_FUNCTIONS
        )
        java_handler(builder.setReadoutFunction, [readout_function_java_obj])

        discriminator_java_obj = pgx_types._check_and_get_value(
            "discriminator", discriminator, pgx_types.DISCRIMINATOR_FUNCTIONS
        )
        java_handler(builder.setDiscriminator, [discriminator_java_obj])

        config = java_handler(builder.build, [])
        return GraphWiseDgiLayerConfig(config, arguments)

    def graphwise_dominant_layer_config(
        self,
        alpha: float = 0.5,
        decoder_layer_config: Optional[Iterable[GraphWisePredictionLayerConfig]] = None,
    ):
        """Build a GraphWise Dominant layer configuration and return it.

        :param alpha: alpha parameter to balance feature reconstruction weight
        :param decoder_layer_config: Decoder layer configuration as list of PredLayerConfig,
            or default if None

        :returns: GraphWiseDgiLayerConfig object
        """
        arguments = locals()

        if not isinstance(alpha, float):
            alpha = 0.5
        # create a list of the Java objects of the pred layer configs
        pred_layer_configs = []
        if decoder_layer_config is not None:
            for p_layer_config in decoder_layer_config:
                if not isinstance(p_layer_config, GraphWisePredictionLayerConfig):
                    raise TypeError(PROPERTY_NOT_FOUND.format(prop=p_layer_config))
                pred_layer_configs.append(p_layer_config._config)
        builder = self._analyst.graphWiseDominantLayerConfigBuilder()

        java_handler(builder.setAlpha, [alpha])
        if len(pred_layer_configs) > 0:
            java_handler(builder.setDecoderLayerConfigs, pred_layer_configs)

        config = java_handler(builder.build, [])
        return GraphWiseDominantLayerConfig(config, arguments)

    def pagerank(
        self,
        graph: PgxGraph,
        tol: float = 0.001,
        damping: float = 0.85,
        max_iter: int = 100,
        norm: bool = False,
        rank: Union[VertexProperty, str] = "pagerank",
    ) -> VertexProperty:
        """
        :param graph: Input graph
        :param tol: Maximum tolerated error value. The algorithm will stop once the sum of
            the error values of all vertices becomes smaller than this value.
        :param damping: Damping factor
        :param max_iter: Maximum number of iterations that will be performed
        :param norm: Determine whether the algorithm will take into account dangling vertices
            for the ranking scores.
        :param rank: Vertex property holding the PageRank value for each vertex, or name for a new
            property
        :returns: Vertex property holding the PageRank value for each vertex
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                pagerank = analyst.pagerank(graph, rank='pagerank')
                result_set = graph.query_pgql(
                    "SELECT x, x.pagerank MATCH (x)"
                    " ORDER BY x.pagerank DESC")
                result_set.print()

        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.pagerank)

        if isinstance(rank, str):
            rank = graph.create_vertex_property("double", rank)

        java_handler(
            self._analyst.pagerank, [graph._graph, tol, damping, max_iter, norm, rank._prop]
        )
        return rank

    def articlerank(
        self,
        graph: PgxGraph,
        tol: float = 0.001,
        damping: float = 0.85,
        max_iter: int = 100,
        norm: bool = False,
        rank: Union[VertexProperty, str] = "articlerank",
    ) -> VertexProperty:
        """
        :param graph: Input graph
        :param tol: Maximum tolerated error value. The algorithm will stop once the sum of
            the error values of all vertices becomes smaller than this value.
        :param damping: Damping factor
        :param max_iter: Maximum number of iterations that will be performed
        :param norm: Determine whether the algorithm will take into account dangling vertices
            for the ranking scores.
        :param rank: Vertex property holding the ArticleRank value for each vertex, or name for a
            new property
        :returns: Vertex property holding the ArticleRank value for each vertex
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                articlerank = analyst.articlerank(graph, rank='articlerank')
                result_set = graph.query_pgql(
                    "SELECT x, x.articlerank MATCH (x)"
                    " ORDER BY x.articlerank DESC")
                result_set.print()

        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.articlerank)

        if isinstance(rank, str):
            rank = graph.create_vertex_property("double", rank)

        java_handler(
            self._analyst.articleRank, [graph._graph, tol, damping, max_iter, norm, rank._prop]
        )
        return rank

    def pagerank_approximate(
        self,
        graph: PgxGraph,
        tol: float = 0.001,
        damping: float = 0.85,
        max_iter: int = 100,
        rank: Union[VertexProperty, str] = "approx_pagerank",
    ) -> VertexProperty:
        """
        :param graph: Input graph
        :param tol: Maximum tolerated error value. The algorithm will stop once the sum of the
            error values of all vertices becomes smaller than this value.
        :param damping: Damping factor
        :param max_iter: Maximum number of iterations that will be performed
        :param rank: Vertex property holding the PageRank value for each vertex
        :returns: Vertex property holding the PageRank value for each vertex
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                pagerank = analyst.pagerank_approximate(
                    graph, rank='approx_pagerank')
                result_set = graph.query_pgql(
                    "SELECT x, x.approx_pagerank MATCH (x) "
                    "ORDER BY x.approx_pagerank DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.pagerank_approximate)

        if isinstance(rank, str):
            rank = graph.create_vertex_property("double", rank)

        java_handler(
            self._analyst.pagerankApproximate, [graph._graph, tol, damping, max_iter, rank._prop]
        )
        return rank

    def weighted_pagerank(
        self,
        graph: PgxGraph,
        weight: EdgeProperty,
        tol: float = 0.001,
        damping: float = 0.85,
        max_iter: int = 100,
        norm: bool = False,
        rank: Union[VertexProperty, str] = "weighted_pagerank",
    ) -> VertexProperty:
        """
        :param graph: Input graph
        :param weight: Edge property holding the weight of each edge in the graph
        :param tol: Maximum tolerated error value. The algorithm will stop once the sum of the
            error values of all vertices becomes smaller than this value.
        :param damping: Damping factor
        :param max_iter: Maximum number of iterations that will be performed
        :param norm: Boolean flag to determine whether
            the algorithm will take into account dangling vertices for the ranking scores.
        :param rank: Vertex property holding the PageRank value for each vertex
        :returns: Vertex property holding the computed the PageRank value
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                cost = graph.get_or_create_edge_property("double", "cost")
                pagerank = analyst.weighted_pagerank(
                    graph, cost, norm=False, rank="weighted_pagerank")
                result_set = graph.query_pgql(
                    "SELECT x, x.weighted_pagerank "
                    "MATCH (x) ORDER BY x.weighted_pagerank DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.weighted_pagerank)

        if isinstance(rank, str):
            rank = graph.create_vertex_property("double", rank)

        java_handler(
            self._analyst.weightedPagerank,
            [graph._graph, tol, damping, max_iter, norm, weight._prop, rank._prop],
        )
        return rank

    def personalized_pagerank(
        self,
        graph: PgxGraph,
        v: Union[VertexSet, PgxVertex],
        tol: float = 0.001,
        damping: float = 0.85,
        max_iter: int = 100,
        norm: bool = False,
        rank: Union[VertexProperty, str] = "personalized_pagerank",
    ) -> VertexProperty:
        """Personalized PageRank for a vertex of interest.

        Compares and spots out important vertices in a graph.

        :param graph: Input graph
        :param v: The chosen vertex from the graph for personalization
        :param tol: Maximum tolerated error value. The algorithm will stop once the sum of
            the error values of all vertices becomes smaller than this value.
        :param damping: Damping factor
        :param max_iter: Maximum number of iterations that will be performed
        :param norm: Boolean flag to determine whether
            the algorithm will take into account dangling vertices for the ranking scores.
        :param rank: Vertex property holding the PageRank value for each vertex
        :returns: Vertex property holding the computed scores
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                vertex = graph.get_vertex("1")
                pagerank = analyst.personalized_pagerank(
                    graph, vertex, rank='perso_pagerank')
                result_set = graph.query_pgql(
                    "SELECT x, x.perso_pagerank MATCH (x) "
                    "ORDER BY x.perso_pagerank DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.personalized_pagerank)

        if isinstance(rank, str):
            rank = graph.create_vertex_property("double", rank)

        if isinstance(v, PgxVertex):
            java_handler(
                self._analyst.personalizedPagerank,
                [graph._graph, v._vertex, tol, damping, max_iter, norm, rank._prop],
            )
        if isinstance(v, VertexSet):
            java_handler(
                self._analyst.personalizedPagerank,
                [graph._graph, v._collection, tol, damping, max_iter, norm, rank._prop],
            )
        return rank

    def personalized_weighted_pagerank(
        self,
        graph: PgxGraph,
        v: Union[VertexSet, PgxVertex],
        weight: EdgeProperty,
        tol: float = 0.001,
        damping: float = 0.85,
        max_iter: int = 100,
        norm: bool = False,
        rank: Union[VertexProperty, str] = "personalized_weighted_pagerank",
    ) -> VertexProperty:
        """
        :param graph: Input graph
        :param v: The chosen vertex from the graph for personalization
        :param weight: Edge property holding the weight of each edge in the graph
        :param tol: Maximum tolerated error value. The algorithm will stop once the sum of
            the error values of all vertices becomes smaller than this value.
        :param damping: Damping factor
        :param max_iter: Maximum number of iterations that will be performed
        :param norm: Boolean flag to determine whether the algorithm will take into account
            dangling vertices for the ranking scores
        :param rank: Vertex property holding the PageRank value for each vertex
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                vertex = graph.get_vertex("1")
                cost = graph.get_or_create_edge_property("double", "cost")
                pagerank = analyst.personalized_weighted_pagerank(
                    graph, vertex, cost, norm=False, rank="pagerank")
                result_set = graph.query_pgql(
                    "SELECT x, x.pagerank MATCH (x) ORDER BY x.pagerank DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.personalized_weighted_pagerank)

        if isinstance(rank, str):
            rank = graph.create_vertex_property("double", rank)

        if isinstance(v, PgxVertex):
            java_handler(
                self._analyst.personalizedWeightedPagerank,
                [graph._graph, v._vertex, tol, damping, max_iter, norm, weight._prop, rank._prop],
            )
        if isinstance(v, VertexSet):
            java_handler(
                self._analyst.personalizedWeightedPagerank,
                [
                    graph._graph,
                    v._collection,
                    tol,
                    damping,
                    max_iter,
                    norm,
                    weight._prop,
                    rank._prop,
                ],
            )
        return rank

    def vertex_betweenness_centrality(
        self, graph: PgxGraph, bc: Union[VertexProperty, str] = "betweenness"
    ) -> VertexProperty:
        """
        :param graph: Input graph
        :param bc: Vertex property holding the betweenness centrality value for each vertex
        :returns: Vertex property holding the computed scores
        :example:

            .. code-block:: python
                    :linenos:

                    graph = ....
                    betweenness = analyst.vertex_betweenness_centrality(
                        graph, bc='betweenness')
                    result_set = graph.query_pgql(
                        "SELECT x, x.betweenness MATCH (x) "
                        "ORDER BY x.betweenness DESC")
                    result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.vertex_betweenness_centrality)

        if isinstance(bc, str):
            bc = graph.create_vertex_property("double", bc)

        java_handler(self._analyst.vertexBetweennessCentrality, [graph._graph, bc._prop])
        return bc

    def approximate_vertex_betweenness_centrality(
        self,
        graph: PgxGraph,
        seeds: Union[VertexSet, int],
        bc: Union[VertexProperty, str] = "approx_betweenness",
    ) -> VertexProperty:
        """
        :param graph: Input graph
        :param seeds: The (unique) chosen nodes to be used to compute the approximated betweenness
            centrality coefficients
        :param bc: Vertex property holding the betweenness centrality value for each vertex
        :returns: Vertex property holding the computed scores
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                betweenness = analyst.approximate_vertex_betweenness_centrality(
                    graph, 100, 'bc')
                result_set = graph.query_pgql(
                    "SELECT x, x.bc MATCH (x) ORDER BY x.bc DESC")
                result_set.print()
        """
        args = locals()
        validate_arguments(args, alg_metadata.approximate_vertex_betweenness_centrality)

        if isinstance(bc, str):
            bc = graph.create_vertex_property("double", bc)

        if isinstance(seeds, VertexSet):
            arguments = [graph._graph, bc._prop]
            for s in seeds:
                arguments.append(s._vertex)
            java_handler(self._analyst.approximateVertexBetweennessCentralityFromSeeds, arguments)
        elif isinstance(seeds, int):
            java_handler(
                self._analyst.approximateVertexBetweennessCentrality,
                [graph._graph, seeds, bc._prop],
            )
        return bc

    def closeness_centrality(
        self, graph: PgxGraph, cc: Union[VertexProperty, str] = "closeness"
    ) -> VertexProperty:
        """
        :param graph: Input graph
        :param cc: Vertex property holding the closeness centrality
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                closeness = analyst.closeness_centrality(graph, "closeness")
                result_set = graph.query_pgql(
                    "SELECT x, x.closeness MATCH (x) ORDER BY x.closeness DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.closeness_centrality)

        if isinstance(cc, str):
            cc = graph.create_vertex_property("double", cc)

        java_handler(self._analyst.closenessCentralityUnitLength, [graph._graph, cc._prop])
        return cc

    def weighted_closeness_centrality(
        self,
        graph: PgxGraph,
        weight: EdgeProperty,
        cc: Union[VertexProperty, str] = "weighted_closeness",
    ) -> VertexProperty:
        """Measure the centrality of the vertices based on weighted distances, allowing to find
        well-connected vertices.

        :param graph: Input graph
        :param weight: Edge property holding the weight of each edge in the graph
        :param cc: (Out argument) vertex property holding the closeness centrality value for each
            vertex
        :returns: Vertex property holding the computed scores
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.weighted_closeness_centrality)

        if isinstance(cc, str):
            cc = graph.create_vertex_property("double", cc)

        java_handler(
            self._analyst.closenessCentralityDoubleLength, [graph._graph, weight._prop, cc._prop]
        )
        return cc

    def hits(
        self,
        graph: PgxGraph,
        max_iter: int = 100,
        auth: Union[VertexProperty, str] = "authorities",
        hubs: Union[VertexProperty, str] = "hubs",
    ) -> Tuple[VertexProperty, VertexProperty]:
        """Hyperlink-Induced Topic Search (HITS) assigns ranking scores to the vertices,
        aimed to assess the quality of information and references in linked structures.

        :param graph: Input graph
        :param max_iter: Number of iterations that will be performed
        :param auth: Vertex property holding the authority score for each vertex
        :param hubs: Vertex property holding the hub score for each vertex
        :returns: Two vertex properties holding the computed scores
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                hits = analyst.hits(graph, auth='authorities', hubs='hubs')
                result_set = graph.query_pgql(
                    "SELECT x, x.authorities, x.hubs "
                    "MATCH (x) ORDER BY x.authorities DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.hits)

        if auth is None or isinstance(auth, str):
            auth = graph.create_vertex_property("double", auth)

        if hubs is None or isinstance(hubs, str):
            hubs = graph.create_vertex_property("double", hubs)

        java_handler(self._analyst.hits, [graph._graph, max_iter, auth._prop, hubs._prop])
        return (auth, hubs)

    def eigenvector_centrality(
        self,
        graph: PgxGraph,
        tol: float = 0.001,
        max_iter: int = 100,
        l2_norm: bool = False,
        in_edges: bool = False,
        ec: Union[VertexProperty, str] = "eigenvector",
    ) -> VertexProperty:
        """Eigenvector centrality gets the centrality of the vertices in an intrincated way using
        neighbors, allowing to find well-connected vertices.

        :param graph: Input graph
        :param tol: Maximum tolerated error value. The algorithm will stop once the sum of the
            error values of all vertices becomes smaller than this value.
        :param max_iter: Maximum iteration number
        :param l2_norm: Boolean flag to determine whether the algorithm will use the l2 norm
            (Euclidean norm) or the l1 norm (absolute value) to normalize the centrality scores
        :param in_edges: Boolean flag to determine whether the algorithm will use the incoming
            or the outgoing edges in the graph for the computations
        :param ec: Vertex property holding the resulting score for each vertex
        :returns: Vertex property holding the computed scores
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                eigenvector = analyst.eigenvector_centrality(
                    graph, ec='eigenvector')
                result_set = graph.query_pgql(
                    "SELECT x, x.eigenvector MATCH (x) "
                    "ORDER BY x.eigenvector DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.eigenvector_centrality)

        if isinstance(ec, str):
            ec = graph.create_vertex_property("double", ec)

        java_handler(
            self._analyst.eigenvectorCentrality,
            [graph._graph, max_iter, tol, l2_norm, in_edges, ec._prop],
        )
        return ec

    def out_degree_centrality(
        self, graph: PgxGraph, dc: Union[VertexProperty, str] = "out_degree"
    ) -> VertexProperty:
        """Measure the out-degree centrality of the vertices based on its degree.

        This lets you see how a vertex influences its neighborhood.

        :param graph: Input graph
        :param dc: Vertex property holding the degree centrality value for each vertex in the graph.
            Can be a string or a VertexProperty object.
        :returns: Vertex property holding the computed scores
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                degree = analyst.out_degree_centrality(
                    graph, dc='out_deg_centrality')
                result_set = graph.query_pgql(
                    "SELECT x, x.out_deg_centrality MATCH (x) "
                    "ORDER BY x.out_deg_centrality DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.out_degree_centrality)

        if isinstance(dc, str):
            dc = graph.create_vertex_property("integer", dc)

        java_handler(self._analyst.outDegreeCentrality, [graph._graph, dc._prop])
        return dc

    def in_degree_centrality(
        self, graph: PgxGraph, dc: Union[VertexProperty, str] = "in_degree"
    ) -> VertexProperty:
        """Measure the in-degree centrality of the vertices based on its degree.

        This lets you see how a vertex influences its neighborhood.

        :param graph: Input graph
        :param dc: Vertex property holding the degree centrality value for each vertex in the graph.
            Can be a string or a VertexProperty object.
        :returns: Vertex property holding the computed scores
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                degree = analyst.in_degree_centrality(
                    graph, dc='in_deg_centrality')
                result_set = graph.query_pgql(
                    "SELECT x, x.in_deg_centrality MATCH (x) "
                    "ORDER BY x.in_deg_centrality DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.in_degree_centrality)

        if isinstance(dc, str):
            dc = graph.create_vertex_property("integer", dc)

        java_handler(self._analyst.inDegreeCentrality, [graph._graph, dc._prop])
        return dc

    def degree_centrality(
        self, graph: PgxGraph, dc: Union[VertexProperty, str] = "degree"
    ) -> VertexProperty:
        """Measure the centrality of the vertices based on its degree.

        This lets you see how a vertex influences its neighborhood.

        :param graph: Input graph
        :param dc: Vertex property holding the degree centrality value for each vertex in the graph
            Can be a string or a VertexProperty object.
        :returns: Vertex property holding the computed scores
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                degree = analyst.degree_centrality(graph, 'degree')
                result_set = graph.query_pgql(
                    "SELECT x, x.degree MATCH (x) ORDER BY x.degree DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.degree_centrality)

        if isinstance(dc, str):
            dc = graph.create_vertex_property("integer", dc)

        java_handler(self._analyst.degreeCentrality, [graph._graph, dc._prop])
        return dc

    def harmonic_centrality(
        self, graph: PgxGraph, hc: Union[VertexProperty, str] = "harmonic_centrality"
    ) -> VertexProperty:
        """Measure the harmonic centrality of the vertices.

        This lets you see how a vertex influences its neighborhood.

        :param graph: Input graph
        :param hc: Vertex property holding the harmonic centrality value for each
            vertex in the graph. Can be a string or a VertexProperty object.
        :returns: Vertex property holding the computed scores
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                degree = analyst.harmonic_centrality(graph, 'hc')
                result_set = graph.query_pgql(
                    "SELECT x, x.hc MATCH (x) ORDER BY x.hc DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.harmonic_centrality)

        if isinstance(hc, str):
            hc = graph.create_vertex_property("double", hc)

        java_handler(self._analyst.harmonicCentrality, [graph._graph, hc._prop])
        return hc

    def adamic_adar_counting(
        self, graph: PgxGraph, aa: Union[EdgeProperty, str] = "adamic_adar"
    ) -> EdgeProperty:
        """Adamic-adar counting compares the amount of neighbors shared between vertices,
        this measure can be used with communities.

        :param graph: Input graph
        :param aa: Edge property holding the Adamic-Adar index for each edge in the graph.
            Can be a string or an EdgeProperty object.
        :returns: Edge property holding the computed scores
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                adamic_adar = analyst.adamic_adar_counting(
                    graph, aa='adamic_adar')
                result_set = graph.query_pgql(
                    "SELECT x, x.adamic_adar MATCH (x)"
                    "ORDER BY x.adamic_adar DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.adamic_adar_counting)

        if isinstance(aa, str):
            aa = graph.create_edge_property("double", aa)

        java_handler(self._analyst.adamicAdarCounting, [graph._graph, aa._prop])
        return aa

    def communities_label_propagation(
        self,
        graph: PgxGraph,
        max_iter: int = 100,
        label: Union[VertexProperty, str] = "label_propagation",
    ) -> PgxPartition:
        """Label propagation can find communities in a graph relatively fast.

        :param graph: Input graph
        :param max_iter: Maximum number of iterations that will be performed
        :param label: Vertex property holding the degree centrality value for each vertex in the
            graph. Can be a string or a VertexProperty object
        :returns: Partition holding the node collections corresponding to the communities found
            by the algorithm
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                conductance = analyst.communities_label_propagation(
                    graph, 100, 'label_propagation')
                result_set = graph.query_pgql(
                    "SELECT x, x.label_propagation MATCH (x) "
                    "ORDER BY x.label_propagation DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.communities_label_propagation)

        if isinstance(label, str):
            label = graph.create_vertex_property("long", label)

        java_partition = java_handler(
            self._analyst.communitiesLabelPropagation, [graph._graph, max_iter, label._prop]
        )
        return PgxPartition(graph, java_partition, label)

    def communities_conductance_minimization(
        self,
        graph: PgxGraph,
        max_iter: int = 100,
        label: Union[VertexProperty, str] = "conductance_minimization",
    ) -> PgxPartition:
        """Soman and Narang can find communities in a graph taking weighted edges into account.

        :param graph: Input graph
        :param max_iter: Maximum number of iterations that will be performed
        :param label: Vertex property holding the degree centrality value for each vertex in the
            graph. Can be a string or a VertexProperty object.
        :returns: Partition holding the node collections corresponding to the communities found
            by the algorithm
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                communities = analyst.communities_conductance_minimization(
                    graph, 100, 'conductance_min')
                result_set = graph.query_pgql(
                    "SELECT x, x.conductance_min MATCH (x) "
                    "ORDER BY x.conductance_min DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.communities_conductance_minimization)

        if isinstance(label, str):
            label = graph.create_vertex_property("long", label)

        java_partition = java_handler(
            self._analyst.communitiesConductanceMinimization, [graph._graph, max_iter, label._prop]
        )
        return PgxPartition(graph, java_partition, label)

    def communities_infomap(
        self,
        graph: PgxGraph,
        rank: VertexProperty,
        weight: EdgeProperty,
        tau: float = 0.15,
        tol: float = 0.0001,
        max_iter: int = 100,
        label: Union[VertexProperty, str] = "infomap",
    ) -> PgxPartition:
        """Infomap can find high quality communities in a graph.

        :param graph: Input graph
        :param rank: Vertex property holding the normalized PageRank value for each vertex
        :param weight: Ridge property holding the weight of each edge in the graph
        :param tau: Damping factor
        :param tol: Maximum tolerated error value. The algorithm will stop once the sum of the error
            values of all vertices becomes smaller than this value.
        :param max_iter: Maximum iteration number
        :param label: Vertex property holding the degree centrality value for each vertex in the
            graph. Can be a string or a VertexProperty object.
        :returns: Partition holding the node collections corresponding to the communities found
            by the algorithm
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                cost = graph.get_or_create_edge_property("double", "cost")
                pagerank = analyst.weighted_pagerank(
                    graph, cost, norm=False, rank="weighted_pagerank")
                partition = analyst.communities_infomap(graph, pagerank, cost)
                first_component = partition.get_partition_by_index(0)
                for vertex in first_component:
                    print(vertex)
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.communities_infomap)

        if isinstance(label, str):
            label = graph.create_vertex_property("long", label)

        java_partition = java_handler(
            self._analyst.communitiesInfomap,
            [graph._graph, rank._prop, weight._prop, tau, tol, max_iter, label._prop],
        )
        return PgxPartition(graph, java_partition, label)

    def louvain(
        self,
        graph: PgxGraph,
        weight: EdgeProperty,
        max_iter: int = 100,
        nbr_pass: int = 1,
        tol: float = 0.0001,
        community: Union[VertexProperty, str] = "community",
    ) -> PgxPartition:
        """Louvain to detect communities in a graph

        :param graph: Input graph.
        :param weight: Weights of the edges of the graph.
        :param max_iter: Maximum number of iterations that will be performed during each pass.
        :param nbr_pass: Number of passes that will be performed.
        :param tol: maximum tolerated error value, the algorithm will stop once the graph's
            total modularity gain becomes smaller than this value.
        :param community: Vertex property holding the community ID assigned to each vertex
        :returns: Community IDs vertex property
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                cost = graph.get_or_create_edge_property("double", "cost")
                partition = analyst.louvain(
                    graph, cost, community="community")
                result_set = graph.query_pgql(
                    "SELECT x, x.community MATCH (x) ORDER BY x.community DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.louvain)

        if isinstance(community, str):
            community = graph.create_vertex_property("long", community)

        java_partition = java_handler(
            self._analyst.louvain,
            [graph._graph, weight._prop, max_iter, nbr_pass, tol, community._prop],
        )
        return PgxPartition(graph, java_partition, community)

    def speaker_listener_label_propagation(
        self,
        graph: PgxGraph,
        labels: Union[VertexProperty, str],
        max_iter: int = 100,
        threshold: float = 0.0,
        delimiter: str = "|",
    ) -> VertexProperty:
        """SLLP to detect overlapping communities

        :param graph: Input graph.
        :param labels: Vertex property holding the value for each vertex in the graph.
            Can be a string or a VertexProperty object.
        :param max_iter: Maximum number of iterations that will be performed.
        :param threshold: The probability of droping a label during the post process.
        :param delimiter: Vertex property holding distinct nodes in the memory with
            probability greater than or equal to threshold.
        :returns: Vertex property holding distinct nodes in the memory with
            probability greater than or equal to threshold.
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                labels = analyst.speaker_listener_label_propagation(
                    graph, 'labels', max_iter, threshold, delimiter)

        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.speaker_listener_label_propagation)

        if isinstance(labels, str):
            labels = graph.create_vertex_property("string", labels)

        java_handler(
            self._analyst.speakerListenerLabelPropagation,
            [graph._graph, labels._prop, max_iter, threshold, delimiter],
        )
        return labels

    def weighted_speaker_listener_label_propagation(
        self,
        graph: PgxGraph,
        weight: EdgeProperty,
        labels: Union[VertexProperty, str],
        max_iter: int = 100,
        threshold: float = 0.0,
        delimiter: str = "|"
    ) -> VertexProperty:
        """WSLLP to detect overlapping communities

        :param graph: Input graph.
        :param weight: Edge property holding the weight of each edge in the graph
        :param labels: Vertex property holding the value for each vertex in the graph.
            Can be a string or a VertexProperty object.
        :param max_iter: Maximum number of iterations that will be performed.
        :param threshold: The probability of droping a label during the post process.
        :param delimiter: delimiter separating the labels in the output string.
        :returns: Vertex property holding distinct nodes in the memory with
            probability greater than or equal to threshold.
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                weight = graph.get_or_create_edge_property("double", "weight")
                labels = analyst.weighted_speaker_listener_label_propagation(
                    graph, weight, 'labels', max_iter, threshold, delimiter)

        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.weighted_speaker_listener_label_propagation)

        if isinstance(labels, str):
            labels = graph.create_vertex_property("string", labels)

        java_handler(
            self._analyst.weightedSpeakerListenerLabelPropagation,
            [graph._graph, labels._prop, max_iter, threshold, delimiter, weight],
        )
        return labels

    def filtered_speaker_listener_label_propagation(
        self,
        graph: PgxGraph,
        filter_expression: EdgeFilter,
        labels: Union[VertexProperty, str],
        max_iter: int = 100,
        threshold: float = 0.0,
        delimiter: str = "|"
    ) -> VertexProperty:
        """FSLLP to detect overlapping communities using an edge filter.

        :param graph: Input graph.
        :param filter_expression: The filter to be used on edges when listening to neighbors.
        :param labels: Vertex property holding the value for each vertex in the graph.
            Can be a string or a VertexProperty object.
        :param max_iter: Maximum number of iterations that will be performed.
        :param threshold: The probability of droping a label during the post process.
        :param delimiter: delimiter separating the labels in the output string.
        :returns: Vertex property holding distinct nodes in the memory with
            probability greater than or equal to threshold.
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                filter = EdgeFilter("edge.cost > 5")
                labels = analyst.filtered_speaker_listener_label_propagation(
                    graph, filter, 'labels', max_iter, threshold, delimiter)

        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.filtered_speaker_listener_label_propagation)

        if isinstance(labels, str):
            labels = graph.create_vertex_property("string", labels)

        java_handler(
            self._analyst.filteredSpeakerListenerLabelPropagation,
            [graph._graph, labels._prop, max_iter, threshold, delimiter, filter],
        )
        return labels

    def filtered_weighted_speaker_listener_label_propagation(
        self,
        graph: PgxGraph,
        filter_expression: EdgeFilter,
        weight: EdgeProperty,
        labels: Union[VertexProperty, str],
        max_iter: int = 100,
        threshold: float = 0.0,
        delimiter: str = "|"
    ) -> VertexProperty:
        """FWSLLP to detect overlapping communities using an edge filter.

        :param graph: Input graph.
        :param filter_expression: The filter to be used on edges when listening to neighbors.
        :param weight: Edge property holding the weight of each edge in the graph.
        :param labels: Vertex property holding the value for each vertex in the graph.
            Can be a string or a VertexProperty object.
        :param max_iter: Maximum number of iterations that will be performed.
        :param threshold: The probability of droping a label during the post process.
        :param delimiter: delimiter separating the labels in the output string.
        :returns: Vertex property holding distinct nodes in the memory with
            probability greater than or equal to threshold.
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                filter = EdgeFilter("edge.cost > 5")
                weight = graph.get_or_create_edge_property("double", "weight")
                labels = analyst.filtered_weighted_speaker_listener_label_propagation(
                    graph, filter, weight, 'labels', max_iter, threshold, delimiter)

        """
        arguments = locals()
        validate_arguments(
            arguments, alg_metadata.filtered_weighted_speaker_listener_label_propagation
        )

        if isinstance(labels, str):
            labels = graph.create_vertex_property("string", labels)

        java_handler(
            self._analyst.filteredWeightedSpeakerListenerLabelPropagation,
            [graph._graph, labels._prop, max_iter, threshold, delimiter, weight, filter],
        )
        return labels

    def conductance(self, graph: PgxGraph, partition: PgxPartition, partition_idx: int) -> float:
        """Conductance assesses the quality of a partition in a graph.

        :param graph: Input graph
        :param partition: Partition of the graph with the corresponding node collections
        :param partition_idx: Number of the component to be used for computing its conductance
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                partition = analyst.communities_conductance_minimization(graph)
                conductance = analyst.conductance(graph, partition, 0)
                print(conductance)
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.conductance)

        cond = java_handler(
            self._analyst.conductance, [graph._graph, partition._partition, partition_idx]
        )
        return cond.get()

    def partition_conductance(
        self, graph: PgxGraph, partition: PgxPartition
    ) -> Tuple[float, float]:
        """Partition conductance assesses the quality of many partitions in a graph.

        :param graph: Input graph
        :param partition: Partition of the graph with the corresponding node collections
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                partition = analyst.communities_conductance_minimization(graph)
                conductance = analyst.partition_conductance(graph, partition)
                print(conductance)
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.partition_conductance)

        pair = java_handler(
            self._analyst.partitionConductance, [graph._graph, partition._partition]
        )
        return (pair.getFirst().get(), pair.getSecond().get())

    def partition_modularity(self, graph: PgxGraph, partition: PgxPartition) -> float:
        """Modularity summarizes information about the quality of components in a graph.

        :param graph: Input graph
        :param partition: Partition of the graph with the corresponding node collections
        :returns: Scalar (double) to store the conductance value of the given cut
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                partition = analyst.communities_conductance_minimization(graph)
                modularity = analyst.partition_modularity(graph, partition)
                print(modularity)
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.partition_modularity)

        modularity = java_handler(
            self._analyst.partitionModularity, [graph._graph, partition._partition]
        )
        return modularity.get()

    def scc_kosaraju(
        self, graph: PgxGraph, label: Union[VertexProperty, str] = "scc_kosaraju"
    ) -> PgxPartition:
        """Kosaraju finds strongly connected components in a graph.

        :param graph: Input graph
        :param label: Vertex property holding the degree centrality value for each vertex in the
            graph. Can be a string or a VertexProperty object.
        :returns: Partition holding the node collections corresponding to the components found by
            the algorithm
        :example:

            .. code-block:: python
                    :linenos:

                    graph = ....
                    pd = graph.create_vertex_property(data_type="long")
                    scc = analyst.scc_kosaraju(graph, 'scc')
                    result_set = graph.query_pgql(
                        "SELECT x, x.scc MATCH (x) ORDER BY x.scc DESC")
                    result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.scc_kosaraju)

        if isinstance(label, str):
            label = graph.create_vertex_property("long", label)

        java_partition = java_handler(self._analyst.sccKosaraju, [graph._graph, label._prop])
        return PgxPartition(graph, java_partition, label)

    def scc_tarjan(
        self, graph: PgxGraph, label: Union[VertexProperty, str] = "scc_tarjan"
    ) -> PgxPartition:
        """Tarjan finds strongly connected components in a graph.

        :param graph: Input graph
        :param label: Vertex property holding the degree centrality value for each vertex in the
            graph. Can be a string or a VertexProperty object.
        :returns: Partition holding the node collections corresponding to the components found by
            the algorithm
        :example:

            .. code-block:: python
                    :linenos:

                    graph = ....
                    scc = analyst.scc_tarjan(graph, label='scc_tarjan')
                    result_set = graph.query_pgql(
                        "SELECT x, x.scc_tarjan MATCH (x) "
                        "ORDER BY x.scc_tarjan DESC")
                    result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.scc_tarjan)

        if isinstance(label, str):
            label = graph.create_vertex_property("long", label)

        java_partition = java_handler(self._analyst.sccTarjan, [graph._graph, label._prop])
        return PgxPartition(graph, java_partition, label)

    def wcc(self, graph: PgxGraph, label: Union[VertexProperty, str] = "wcc") -> PgxPartition:
        """Identify weakly connected components.

        This can be useful for clustering graph data.

        :param graph: Input graph
        :param label: Vertex property holding the value for each vertex in the graph.
            Can be a string or a VertexProperty object.
        :returns: Partition holding the node collections corresponding to the components found by
            the algorithm.
        :example:

            .. code-block:: python
                    :linenos:

                    graph = ....
                    wcc = analyst.wcc(graph, label='wcc')
                    result_set = graph.query_pgql(
                        "SELECT x, x.wcc MATCH (x) ORDER BY x.wcc DESC")
                    result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.wcc)

        if isinstance(label, str):
            label = graph.create_vertex_property("long", label)

        java_partition = java_handler(self._analyst.wcc, [graph._graph, label._prop])
        return PgxPartition(graph, java_partition, label)

    def salsa(
        self,
        bipartite_graph: BipartiteGraph,
        tol: float = 0.001,
        max_iter: int = 100,
        rank: Union[VertexProperty, str] = "salsa",
    ) -> VertexProperty:
        """Stochastic Approach for Link-Structure Analysis (SALSA) computes ranking scores.

        It assesses the quality of information and references in linked structures.

        .. note::

            The input graph must be a bipartite graph, you can use analyst.bipartite_check.

        :param bipartite_graph: Bipartite graph
        :param tol: Maximum tolerated error value. The algorithm will stop once the sum of the error
            values of all vertices becomes smaller than this value.
        :param max_iter: Maximum number of iterations that will be performed
        :param rank: Vertex property holding the value for each vertex in the graph
        :returns: Vertex property holding the computed scores
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                analyst.salsa(graph, rank='salsa')
                result_set = graph.query_pgql(
                    "SELECT x, x.salsa MATCH (x) ORDER BY x.salsa DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.salsa)

        if isinstance(rank, str):
            rank = bipartite_graph.create_vertex_property("double", rank)

        java_handler(self._analyst.salsa, [bipartite_graph._graph, tol, max_iter, rank._prop])
        return rank

    def personalized_salsa(
        self,
        bipartite_graph: BipartiteGraph,
        v: Union[VertexSet, PgxVertex],
        tol: float = 0.001,
        damping: float = 0.85,
        max_iter: int = 100,
        rank: Union[VertexProperty, str] = "personalized_salsa",
    ) -> VertexProperty:
        """Personalized SALSA for a vertex of interest.

        Assesses the quality of information and references in linked structures.

        .. note::

            The input graph must be a bipartite graph, you can use analyst.bipartite_check.

        :param bipartite_graph: Bipartite graph
        :param v: The chosen vertex from the graph for personalization
        :param tol: Maximum tolerated error value. The algorithm will stop once the sum of the
            error values of all vertices becomes smaller than this value.
        :param damping: Damping factor to modulate the degree of personalization of the scores by
            the algorithm
        :param max_iter: Maximum number of iterations that will be performed
        :param rank: (Out argument) vertex property holding the normalized authority/hub
            ranking score for each vertex
        :returns: Vertex property holding the computed scores
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                vertex = graph.get_vertex("1")
                salsa = analyst.personalized_salsa(
                    graph, vertex, rank='personalized_salsa')
                result_set = graph.query_pgql(
                    "SELECT x, x.personalized_salsa MATCH (x) "
                    "ORDER BY x.personalized_salsa DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.personalized_salsa)

        if isinstance(rank, str):
            rank = bipartite_graph.create_vertex_property("double", rank)

        if isinstance(v, PgxVertex):
            java_handler(
                self._analyst.personalizedSalsa,
                [bipartite_graph._graph, v._vertex, damping, max_iter, tol, rank._prop],
            )
        if isinstance(v, VertexSet):
            java_handler(
                self._analyst.personalizedSalsa,
                [bipartite_graph._graph, v._collection, damping, max_iter, tol, rank._prop],
            )
        return rank

    def whom_to_follow(
        self,
        graph: PgxGraph,
        v: PgxVertex,
        top_k: int = 100,
        size_circle_of_trust: int = 500,
        tol: float = 0.001,
        damping: float = 0.85,
        max_iter: int = 100,
        salsa_tol: float = 0.001,
        salsa_max_iter: int = 100,
        hubs: Optional[Union[VertexSequence, str]] = None,
        auth: Optional[Union[VertexSequence, str]] = None,
    ) -> Tuple[VertexSequence, VertexSequence]:
        """Whom-to-follow (WTF) is a recommendation algorithm.

        It returns two vertex sequences: one of similar users (hubs) and a second one with users
        to follow (auth).

        :param graph: Input graph
        :param v: The chosen vertex from the graph for personalization of the recommendations
        :param top_k: The maximum number of recommendations that will be returned
        :param size_circle_of_trust: The maximum size of the circle of trust
        :param tol: Maximum tolerated error value. The algorithm will stop once the sum of the error
            values of all vertices becomes smaller than this value.
        :param damping: Damping factor for the Pagerank stage
        :param max_iter: Maximum number of iterations that will be performed for the Pagerank stage
        :param salsa_tol: Maximum tolerated error value for the SALSA stage
        :param salsa_max_iter: Maximum number of iterations that will be performed for the SALSA
            stage
        :param hubs: (Out argument) vertex sequence holding the top rated hub vertices (similar
            users) for the recommendations
        :param auth: (Out argument) vertex sequence holding the top rated authority vertices
            (users to follow) for the recommendations
        :returns: Vertex properties holding hubs and auth
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                vertex = graph.get_vertex("1")
                hubs, auths = analyst.whom_to_follow(graph, vertex)
                for hub in hubs:
                    print(hub)
                for auth in auths:
                    print(auth)
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.whom_to_follow)

        if hubs is None or isinstance(hubs, str):
            hubs = graph.create_vertex_sequence(hubs)

        if auth is None or isinstance(auth, str):
            auth = graph.create_vertex_sequence(auth)

        java_handler(
            self._analyst.whomToFollow,
            [
                graph._graph,
                v._vertex,
                top_k,
                size_circle_of_trust,
                max_iter,
                tol,
                damping,
                salsa_max_iter,
                salsa_tol,
                hubs._collection,
                auth._collection,
            ],
        )
        return (hubs, auth)

    def matrix_factorization_gradient_descent(
        self,
        bipartite_graph: BipartiteGraph,
        weight: EdgeProperty,
        learning_rate: float = 0.001,
        change_per_step: float = 1.0,
        lbd: float = 0.15,
        max_iter: int = 100,
        vector_length: int = 10,
        features: Union[VertexProperty, str] = "features",
    ) -> MatrixFactorizationModel:
        """
        .. note::

            The input graph must be a bipartite graph, you can use analyst.bipartite_check.

        :param bipartite_graph: Input graph
            between 1 and 5, the result will become inaccurate.
        :param weight: Edge property holding the weight of each edge in the graph
        :param learning_rate: Learning rate for the optimization process
        :param change_per_step: Parameter used to modulate the learning rate during the
            optimization process
        :param lbd: Penalization parameter to avoid over-fitting during optimization process
        :param max_iter: Maximum number of iterations that will be performed
        :param vector_length: Size of the feature vectors to be generated for the factorization
        :param features: Vertex property holding the generated feature vectors for each vertex.
            This function accepts names and VertexProperty objects.
        :returns: Matrix factorization model holding the feature vectors found by the algorithm
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                cost = graph.get_or_create_edge_property("double", "cost")
                model = analyst.matrix_factorization_gradient_descent(graph, cost)
                v = get_vertex("1")
                print(model.get_estimated_ratings(v))
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.matrix_factorization_gradient_descent)

        if isinstance(features, str):
            features = bipartite_graph.create_vertex_vector_property(
                "double", vector_length, features
            )

        mfm = java_handler(
            self._analyst.matrixFactorizationGradientDescent,
            [
                bipartite_graph._graph,
                weight._prop,
                learning_rate,
                change_per_step,
                lbd,
                max_iter,
                vector_length,
                features._prop,
            ],
        )
        return MatrixFactorizationModel(bipartite_graph, mfm, features)

    def fattest_path(
        self,
        graph: PgxGraph,
        root: PgxVertex,
        capacity: EdgeProperty,
        distance: Union[VertexProperty, str] = "fattest_path_distance",
        parent: Union[VertexProperty, str] = "fattest_path_parent",
        parent_edge: Union[VertexProperty, str] = "fattest_path_parent_edge",
        ignore_edge_direction: bool = False
    ) -> AllPaths:
        """Fattest path is a fast algorithm for finding a shortest path adding constraints for
        flowing related matters.

        :param graph: Input graph
        :param root: Fattest path is a fast algorithm for finding a shortest path adding constraints
            for flowing related matters
        :param capacity: Edge property holding the capacity of each edge in the graph
        :param distance: Vertex property holding the capacity value of the fattest path up to the
            current vertex
        :param parent: Vertex property holding the parent vertex of the each vertex in the
            fattest path
        :param parent_edge: Vertex property holding the edge ID linking the current vertex
            in the path with the previous vertex in the path
        :param ignore_edge_direction: Boolean flag for ignoring the direction of the edges during
            the search
        :returns: AllPaths object holding the information of the possible fattest paths from the
            source node
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                root = graph.get_vertex("1")
                cost = graph.get_or_create_edge_property("double", "cost")
                fattest_path = analyst.fattest_path(graph, root, cost)
                print(fattest_path)
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.fattest_path)

        if isinstance(distance, str):
            distance = graph.create_vertex_property("double", distance)
        if isinstance(parent, str):
            parent = graph.create_vertex_property("vertex", parent)
        if isinstance(parent_edge, str):
            parent_edge = graph.create_vertex_property("edge", parent_edge)

        paths = java_handler(
            self._analyst.fattestPath,
            [
                graph._graph,
                root._vertex,
                capacity._prop,
                distance._prop,
                parent._prop,
                parent_edge._prop,
                ignore_edge_direction
            ],
        )
        return AllPaths(graph, paths)

    def shortest_path_dijkstra(
        self,
        graph: PgxGraph,
        src: PgxVertex,
        dst: PgxVertex,
        weight: EdgeProperty,
        parent: Union[VertexProperty, str] = "dijkstra_parent",
        parent_edge: Union[VertexProperty, str] = "dijkstra_parent_edge",
        ignore_edge_direction: bool = False
    ) -> PgxPath:
        """
        :param graph: Input graph
        :param src: Source node
        :param dst: Destination node
        :param weight: Edge property holding the (positive) weight of each edge in the graph
        :param parent: (Out argument) vertex property holding the parent vertex of the each
            vertex in the shortest path
        :param parent_edge: (Out argument) vertex property holding the edge ID linking the
            current vertex in the path with the previous vertex in the path
        :param ignore_edge_direction: Boolean flag for ignoring the direction of the edges
        :returns: PgxPath holding the information of the shortest path, if it exists
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                src = graph.get_vertex("1")
                dst = graph.get_vertex("2")
                cost = graph.get_or_create_edge_property("double", "cost")
                path = analyst.shortest_path_dijkstra(
                    graph, src, dst, cost)
                print(path)
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.shortest_path_dijkstra)

        if isinstance(parent, str):
            parent = graph.create_vertex_property("vertex", parent)
        if isinstance(parent_edge, str):
            parent_edge = graph.create_vertex_property("edge", parent_edge)

        path = java_handler(
            self._analyst.shortestPathDijkstra,
            [graph._graph, src._vertex, dst._vertex, weight._prop, parent._prop, parent_edge._prop,
                ignore_edge_direction],
        )
        return PgxPath(graph, path)

    def shortest_path_dijkstra_multi_dest(
        self,
        graph: PgxGraph,
        src: PgxVertex,
        weight: EdgeProperty,
        distance: Union[VertexProperty, str] = "dijkstra_multi_dest__distance",
        parent: Union[VertexProperty, str] = "dijkstra_multi_dest__parent",
        parent_edge: Union[VertexProperty, str] = "dijkstra_multi_dest_parent_edge",
    ) -> AllPaths:
        """
        :param graph: Input graph
        :param src: Source node
        :param weight: Edge property holding the (positive) weight of each edge in the graph
        :param distance: (Out argument) vertex property holding the distance to the source vertex
            for each vertex in the graph
        :param parent: (Out argument) vertex property holding the parent vertex of the each
            vertex in the shortest path
        :param parent_edge: (Out argument) vertex property holding the edge ID linking the
            current vertex in the path with the previous vertex in the path
        :returns: AllPaths holding the information of the possible shortest paths from the source
            node
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                src = graph.get_vertex("1")
                cost = graph.get_or_create_edge_property("double", "cost")
                paths = analyst.shortestPathMultiDestinationDijkstra(
                graph, src, cost, distance="dijkstra_multi_dest_distance")
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.shortest_path_dijkstra_multi_dest)

        if isinstance(distance, str):
            distance = graph.create_vertex_property("double", distance)
        if isinstance(parent, str):
            parent = graph.create_vertex_property("vertex", parent)
        if isinstance(parent_edge, str):
            parent_edge = graph.create_vertex_property("edge", parent_edge)

        paths = java_handler(
            self._analyst.shortestPathMultiDestinationDijkstra,
            [
                graph._graph,
                src._vertex,
                weight._prop,
                distance._prop,
                parent._prop,
                parent_edge._prop
            ],
        )
        return AllPaths(graph, paths)

    def shortest_path_filtered_dijkstra(
        self,
        graph: PgxGraph,
        src: PgxVertex,
        dst: PgxVertex,
        weight: EdgeProperty,
        filter_expression: EdgeFilter,
        parent: Union[VertexProperty, str] = "dijkstra_parent",
        parent_edge: Union[VertexProperty, str] = "dijkstra_parent_edge",
        ignore_edge_direction: bool = False
    ) -> PgxPath:
        """
        :param graph: Input graph
        :param src: Source node
        :param dst: Destination node
        :param weight: Edge property holding the (positive) weight of each edge in the graph
        :param parent: (Out argument) vertex property holding the parent vertex of the each
            vertex in the shortest path
        :param parent_edge: (Out argument) vertex property holding the edge ID linking the
            current vertex in the path with the previous vertex in the path
        :param filter_expression: GraphFilter object for filtering
        :param ignore_edge_direction: Boolean flag for ignoring the direction of the edges
        :returns: PgxPath holding the information of the shortest path, if it exists
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                src = graph.get_vertex("1")
                dst = graph.get_vertex("2")
                cost = graph.get_or_create_edge_property("double", "cost")
                filter = EdgeFilter("edge.cost > 5")
                path = analyst.shortest_path_filtered_dijkstra(
                    graph, src, dst, cost, filter)
                print(path)
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.shortest_path_filtered_dijkstra)

        if isinstance(parent, str):
            parent = graph.create_vertex_property("vertex", parent)
        if isinstance(parent_edge, str):
            parent_edge = graph.create_vertex_property("edge", parent_edge)

        path = java_handler(
            self._analyst.shortestPathFilteredDijkstra,
            [
                graph._graph,
                src._vertex,
                dst._vertex,
                weight._prop,
                filter_expression._filter,
                parent._prop,
                parent_edge._prop,
                ignore_edge_direction,
            ],
        )
        return PgxPath(graph, path)

    def shortest_path_bidirectional_dijkstra(
        self,
        graph: PgxGraph,
        src: PgxVertex,
        dst: PgxVertex,
        weight: EdgeProperty,
        parent: Union[VertexProperty, str] = "bidirectional_dijkstra_parent",
        parent_edge: Union[VertexProperty, str] = "bidirectional_dijkstra_parent_edge",
        ignore_edge_direction: bool = False,
    ) -> PgxPath:
        """Bidirectional dijkstra is a fast algorithm for finding a shortest path in a graph.

        :param graph: Input graph
        :param src: Source node
        :param dst: Destination node
        :param weight: Edge property holding the (positive) weight of each edge in the graph
        :param parent: (Out argument) vertex property holding the parent vertex of the each
            vertex in the shortest path
        :param parent_edge: (Out argument) vertex property holding the edge ID linking the
            current vertex in the path with the previous vertex in the path
        :param ignore_edge_direction: Boolean flag for ignoring the direction of the edges
        :returns: PgxPath holding the information of the shortest path, if it exists
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                src = graph.get_vertex("1")
                dst = graph.get_vertex("2")
                cost = graph.get_or_create_edge_property("double", "cost")
                filter = EdgeFilter("edge.cost > 5")
                path = analyst.shortest_path_bidirectional_dijkstra(
                    graph, src, dst, cost, filter)
                print(path)
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.shortest_path_bidirectional_dijkstra)

        if isinstance(parent, str):
            parent = graph.create_vertex_property("vertex", parent)
        if isinstance(parent_edge, str):
            parent_edge = graph.create_vertex_property("edge", parent_edge)

        path = java_handler(
            self._analyst.shortestPathDijkstraBidirectional,
            [graph._graph, src._vertex, dst._vertex, weight._prop, parent._prop, parent_edge._prop,
                ignore_edge_direction],
        )
        return PgxPath(graph, path)

    def shortest_path_filtered_bidirectional_dijkstra(
        self,
        graph: PgxGraph,
        src: PgxVertex,
        dst: PgxVertex,
        weight: EdgeProperty,
        filter_expression: EdgeFilter,
        parent: Union[VertexProperty, str] = "bidirectional_dijkstra_parent",
        parent_edge: Union[VertexProperty, str] = "bidirectional_dijkstra_parent_edge",
        ignore_edge_direction: bool = False,
    ) -> PgxPath:
        """
        :param graph: Input graph
        :param src: Source node
        :param dst: Destination node
        :param weight: Edge property holding the (positive) weight of each edge in the graph
        :param parent: (Out argument) vertex property holding the parent vertex of the each
            vertex in the shortest path
        :param parent_edge: (Out argument) vertex property holding the edge ID linking the
            current vertex in the path with the previous vertex in the path
        :param filter_expression: graphFilter object for filtering
        :param ignore_edge_direction: Boolean flag for ignoring the direction of the edges
        :returns: PgxPath holding the information of the shortest path, if it exists
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.shortest_path_filtered_bidirectional_dijkstra)

        if isinstance(parent, str):
            parent = graph.create_vertex_property("vertex", parent)
        if isinstance(parent_edge, str):
            parent_edge = graph.create_vertex_property("edge", parent_edge)

        path = java_handler(
            self._analyst.shortestPathFilteredDijkstraBidirectional,
            [
                graph._graph,
                src._vertex,
                dst._vertex,
                weight._prop,
                filter_expression._filter,
                parent._prop,
                parent_edge._prop,
                ignore_edge_direction,
            ],
        )
        return PgxPath(graph, path)

    def shortest_path_bellman_ford(
        self,
        graph: PgxGraph,
        src: PgxVertex,
        weight: EdgeProperty,
        distance: Union[VertexProperty, str] = "bellman_ford_distance",
        parent: Union[VertexProperty, str] = "bellman_ford_parent",
        parent_edge: Union[VertexProperty, str] = "bellman_ford_parent_edge",
        ignore_edge_direction: bool = False
    ) -> AllPaths:
        """Bellman-Ford finds multiple shortest paths at the same time.

        :param graph: Input graph
        :param src: Source node
        :param distance: (Out argument) vertex property holding the distance to the source vertex
            for each vertex in the graph
        :param weight: Edge property holding the weight of each edge in the graph
        :param ignore_edge_direction: Boolean flag for ignoring the direction of the edges during
            the search
        :param parent: (Out argument) vertex property holding the parent vertex of the each
            vertex in the shortest path
        :param parent_edge: (Out argument) vertex property holding the edge ID linking the
            current vertex in the path with the previous vertex in the path
        :returns: AllPaths holding the information of the possible shortest paths from the source
            node
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                src = graph.get_vertex("1")
                cost = graph.get_or_create_edge_property("double", "cost")
                paths = analyst.shortest_path_bellman_ford(
                    graph, src, cost, distance="bellman_ford_distance")
                result_set = graph.query_pgql(
                    "SELECT x, x.bellman_ford_distance MATCH (x) "
                    "ORDER BY x.bellman_ford_distance DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.shortest_path_bellman_ford)

        if isinstance(distance, str):
            distance = graph.create_vertex_property("double", distance)
        if isinstance(parent, str):
            parent = graph.create_vertex_property("vertex", parent)
        if isinstance(parent_edge, str):
            parent_edge = graph.create_vertex_property("edge", parent_edge)

        paths = java_handler(
            self._analyst.shortestPathBellmanFord,
            [
                graph._graph,
                src._vertex,
                weight._prop,
                distance._prop,
                parent._prop,
                parent_edge._prop,
                ignore_edge_direction
            ],
        )
        return AllPaths(graph, paths)

    def shortest_path_bellman_ford_reversed(
        self,
        graph: PgxGraph,
        src: PgxVertex,
        weight: EdgeProperty,
        distance: Union[VertexProperty, str] = "bellman_ford_distance",
        parent: Union[VertexProperty, str] = "bellman_ford_parent",
        parent_edge: Union[VertexProperty, str] = "bellman_ford_parent_edge",
    ) -> AllPaths:
        """Reversed Bellman-Ford finds multiple shortest paths at the same time.

        :param graph: Input graph
        :param src: Source node
        :param distance: (Out argument) vertex property holding the distance to the source
            vertex for each vertex in the graph
        :param weight: Edge property holding the weight of each edge in the graph
        :param parent: (Out argument) vertex property holding the parent vertex of the each
            vertex in the shortest path.
        :param parent_edge: (Out argument) vertex property holding the edge ID linking the
            current vertex in the path with the previous vertex in the path.
        :returns: AllPaths holding the information of the possible shortest paths from the source
            node.
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.shortest_path_bellman_ford_reversed)

        if isinstance(distance, str):
            distance = graph.create_vertex_property("double", distance)
        if isinstance(parent, str):
            parent = graph.create_vertex_property("vertex", parent)
        if isinstance(parent_edge, str):
            parent_edge = graph.create_vertex_property("edge", parent_edge)

        paths = java_handler(
            self._analyst.shortestPathBellmanFordReverse,
            [
                graph._graph,
                src._vertex,
                weight._prop,
                distance._prop,
                parent._prop,
                parent_edge._prop,
            ],
        )
        return AllPaths(graph, paths)

    def shortest_path_bellman_ford_single_destination(
        self,
        graph: PgxGraph,
        src: PgxVertex,
        dst: PgxVertex,
        weight: EdgeProperty,
        parent: Union[VertexProperty, str] = "bellman_ford_single_dest_parent",
        parent_edge: Union[VertexProperty, str] = "bellman_ford_single_dest_parent_edge",
    ) -> PgxPath:
        """
        :param graph: Input graph
        :param src: Source node
        :param dst: Destination node
        :param weight: Edge property holding the (positive) weight of each edge in the graph
        :param parent: (Out argument) vertex property holding the parent vertex of the each
            vertex in the shortest path
        :param parent_edge: (Out argument) vertex property holding the edge ID linking the
            current vertex in the path with the previous vertex in the path
        :returns: PgxPath holding the information of the shortest path, if it exists
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                src = graph.get_vertex("1")
                dst = graph.get_vertex("2")
                cost = graph.get_or_create_edge_property("double", "cost")
                path = analyst.shortest_path_bellman_ford_single_destination(
                    graph, src, dst, cost)
                print(path)
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.shortest_path_bellman_ford_single_destination)

        if isinstance(parent, str):
            parent = graph.create_vertex_property("vertex", parent)
        if isinstance(parent_edge, str):
            parent_edge = graph.create_vertex_property("edge", parent_edge)

        path = java_handler(
            self._analyst.shortestPathBellmanFordSingleDestination,
            [
                graph._graph,
                src._vertex,
                dst._vertex,
                weight._prop,
                parent._prop,
                parent_edge._prop
            ],
        )
        return PgxPath(graph, path)

    def shortest_path_hop_distance(
        self,
        graph: PgxGraph,
        src: PgxVertex,
        distance: Union[VertexProperty, str] = "hop_dist_distance",
        parent: Union[VertexProperty, str] = "hop_dist_parent",
        parent_edge: Union[VertexProperty, str] = "hop_dist_edge",
    ) -> AllPaths:
        """Hop distance can give a relatively fast insight on the distances in a graph.

        :param graph: Input graph
        :param src: Source node
        :param distance: Out argument) vertex property holding the distance to the source vertex
            for each vertex in the graph
        :param parent: (Out argument) vertex property holding the parent vertex of the each
            vertex in the shortest path
        :param parent_edge: (Out argument) vertex property holding the edge ID linking the
            current vertex in the path with the previous vertex in the path
        :returns: AllPaths holding the information of the possible shortest paths from the source
            node
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.shortest_path_hop_distance)

        if isinstance(distance, str):
            distance = graph.create_vertex_property("double", distance)
        if isinstance(parent, str):
            parent = graph.create_vertex_property("vertex", parent)
        if isinstance(parent_edge, str):
            parent_edge = graph.create_vertex_property("edge", parent_edge)

        paths = java_handler(
            self._analyst.shortestPathHopDist,
            [graph._graph, src._vertex, distance._prop, parent._prop, parent_edge._prop],
        )
        return AllPaths(graph, paths)

    def shortest_path_hop_distance_reversed(
        self,
        graph: PgxGraph,
        src: PgxVertex,
        distance: Union[VertexProperty, str] = "hop_dist_distance",
        parent: Union[VertexProperty, str] = "hop_dist_parent",
        parent_edge: Union[VertexProperty, str] = "hop_dist_edge",
    ) -> AllPaths:
        """Backwards hop distance can give a relatively fast insight on the distances in a graph.

        :param graph: Input graph
        :param src: Source node
        :param distance: Out argument) vertex property holding the distance to the source vertex
            for each vertex in the graph
        :param parent: (Out argument) vertex property holding the parent vertex of the each
            vertex in the shortest path
        :param parent_edge: (Out argument) vertex property holding the edge ID linking the
            current vertex in the path with the previous vertex in the path
        :returns: AllPaths holding the information of the possible shortest paths from the source
            node
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.shortest_path_hop_distance_reversed)

        if isinstance(distance, str):
            distance = graph.create_vertex_property("double", distance)
        if isinstance(parent, str):
            parent = graph.create_vertex_property("vertex", parent)
        if isinstance(parent_edge, str):
            parent_edge = graph.create_vertex_property("edge", parent_edge)

        paths = java_handler(
            self._analyst.shortestPathHopDistReverse,
            [graph._graph, src._vertex, distance._prop, parent._prop, parent_edge._prop],
        )
        return AllPaths(graph, paths)

    def shortest_path_hop_distance_undirected(
        self,
        graph: PgxGraph,
        src: PgxVertex,
        distance: Union[VertexProperty, str] = "hop_dist_distance",
        parent: Union[VertexProperty, str] = "hop_dist_parent",
        parent_edge: Union[VertexProperty, str] = "hop_dist_edge",
    ) -> AllPaths:
        """Undirected hop distance can give a relatively fast insight on the distances in a graph.

        :param graph: Input graph
        :param src: Source node
        :param distance: Out argument) vertex property holding the distance to the source vertex
            for each vertex in the graph
        :param parent: (Out argument) vertex property holding the parent vertex of the each
            vertex in the shortest path
        :param parent_edge: (Out argument) vertex property holding the edge ID linking the
            current vertex in the path with the previous vertex in the path
        :returns: AllPaths holding the information of the possible shortest paths from the source
            node
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.shortest_path_hop_distance)

        if isinstance(distance, str):
            distance = graph.create_vertex_property("double", distance)
        if isinstance(parent, str):
            parent = graph.create_vertex_property("vertex", parent)
        if isinstance(parent_edge, str):
            parent_edge = graph.create_vertex_property("edge", parent_edge)

        paths = java_handler(
            self._analyst.shortestPathHopDistUndirected,
            [graph._graph, src._vertex, distance._prop, parent._prop, parent_edge._prop],
        )
        return AllPaths(graph, paths)

    def count_triangles(self, graph: PgxGraph, sort_vertices_by_degree: bool) -> int:
        """Triangle counting gives an overview of the amount of connections between vertices in
        neighborhoods.

        :param graph: Input graph
        :param sort_vertices_by_degree: Boolean flag for sorting the nodes by their degree as
            preprocessing step
        :returns: The total number of triangles found
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                result = analyst.count_triangles(graph, sort_vertices_by_degree=True)
                print(result)
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.count_triangles)

        return java_handler(self._analyst.countTriangles, [graph._graph, sort_vertices_by_degree])

    def k_core(
        self,
        graph: PgxGraph,
        min_core: int = 0,
        max_core: int = 2147483647,
        kcore: Union[VertexProperty, str] = "kcore",
    ) -> Tuple[int, VertexProperty]:
        """k-core decomposes a graph into layers revealing subgraphs with particular properties.

        :param graph: Input graph
        :param min_core: Minimum k-core value
        :param max_core: Maximum k-core value
        :param kcore: Vertex property holding the result value

        :returns: Pair holding the maximum core found and a node property with the largest k-core
            value for each node.
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                kcore = analyst.k_core(graph, kcore='kcore')
                result_set = graph.query_pgql(
                    "SELECT x, x.kcore MATCH (x) ORDER BY x.kcore DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.k_core)

        if isinstance(kcore, str):
            kcore = graph.create_vertex_property("long", kcore)

        max_k_core = java_handler(graph._graph.createScalar, [pgx_types.property_types["long"]])

        java_handler(
            self._analyst.kcore, [graph._graph, min_core, int(max_core), max_k_core, kcore._prop]
        )
        return (max_k_core.get(), kcore)

    def diameter(
        self, graph: PgxGraph, eccentricity: Union[VertexProperty, str] = "eccentricity"
    ) -> Tuple[int, VertexProperty]:
        """Diameter/radius gives an overview of the distances in a graph.

        :param graph: Input graph
        :param eccentricity: (Out argument) vertex property holding the eccentricity value for
            each vertex
        :returns: Pair holding the diameter of the graph and a node property with eccentricity
            value for each node
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                diameter = analyst.diameter(graph, 'eccentricity')
                result_set = graph.query_pgql(
                    "SELECT x, x.eccentricity MATCH (x) "
                    "ORDER BY x.eccentricity DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.diameter)

        if isinstance(eccentricity, str):
            eccentricity = graph.create_vertex_property("integer", eccentricity)

        diameter = java_handler(graph._graph.createScalar, [pgx_types.property_types["integer"]])

        java_handler(self._analyst.diameter, [graph._graph, diameter, eccentricity._prop])
        return (diameter.get(), eccentricity)

    def radius(
        self, graph: PgxGraph, eccentricity: Union[VertexProperty, str] = "eccentricity"
    ) -> Tuple[int, VertexProperty]:
        """Radius gives an overview of the distances in a graph. it is computed as the minimum
        graph eccentricity.

        :param graph: Input graph
        :param eccentricity: (Out argument) vertex property holding the eccentricity value for
            each vertex
        :returns: Pair holding the radius of the graph and a node property with eccentricity
            value for each node
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                diameter = analyst.radius(
                    graph, eccentricity='eccentricity')
                result_set = graph.query_pgql(
                    "SELECT x, x.eccentricity MATCH (x) "
                    "ORDER BY x.eccentricity DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.radius)

        if isinstance(eccentricity, str):
            eccentricity = graph.create_vertex_property("integer", eccentricity)

        radius = java_handler(graph._graph.createScalar, [pgx_types.property_types["integer"]])

        java_handler(self._analyst.radius, [graph._graph, radius, eccentricity._prop])
        return (radius.get(), eccentricity)

    def periphery(
        self, graph: PgxGraph, periphery: Optional[Union[VertexSet, str]] = None
    ) -> VertexSet:
        """Periphery/center gives an overview of the extreme distances and the corresponding
        vertices in a graph.

        :param graph: Input graph
        :param periphery: (Out argument) vertex set holding the vertices from the periphery
            of the graph
        :returns: Vertex set holding the vertices from the periphery of the graph
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                periphery = analyst.periphery(graph)
                for vertex in periphery:
                    print(vertex)
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.periphery)

        if periphery is None or isinstance(periphery, str):
            periphery = graph.create_vertex_set(periphery)

        java_handler(self._analyst.periphery, [graph._graph, periphery._collection])
        return periphery

    def center(self, graph: PgxGraph, center: Optional[Union[VertexSet, str]] = None) -> VertexSet:
        """Periphery/center gives an overview of the extreme distances and the corresponding
        vertices in a graph.

        The center is comprised by the set of vertices with eccentricity equal to the radius of
        the graph.

        :param graph: Input graph
        :param center: (Out argument) vertex set holding the vertices from the
            center of the graph
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                verticies = analyst.center(graph)
                for vertex in verticies:
                    print(vertex)
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.center)

        if center is None or isinstance(center, str):
            center = graph.create_vertex_set(center)

        java_handler(self._analyst.center, [graph._graph, center._collection])
        return center

    def local_clustering_coefficient(
        self, graph: PgxGraph, lcc: Union[VertexProperty, str] = "lcc"
        , ignore_edge_direction: bool = False
    ) -> VertexProperty:
        """LCC gives information about potential clustering options in a graph.

        :param graph: Input graph
        :param lcc: Vertex property holding the lcc value for each vertex
        :param ignore_edge_direction: Boolean flag for ignoring the direction of the edges during
            the search
        :returns: Vertex property holding the lcc value for each vertex
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                lcc = analyst.local_clustering_coefficient(graph, lcc='lcc'
                , ignore_edge_direction=True)
                result_set = graph.query_pgql(
                    "SELECT x, x.lcc MATCH (x) ORDER BY x.lcc DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.local_clustering_coefficient)

        if isinstance(lcc, str):
            lcc = graph.create_vertex_property("double", lcc)

        java_handler(
            self._analyst.localClusteringCoefficient,
            [graph._graph, lcc._prop, ignore_edge_direction]
        )
        return lcc

    def find_cycle(
        self,
        graph: PgxGraph,
        src: Optional[PgxVertex] = None,
        vertex_seq: Optional[Union[VertexSequence, str]] = None,
        edge_seq: Optional[Union[EdgeSequence, str]] = None,
    ) -> PgxPath:
        """Find cycle looks for any loop in the graph.

        :param graph: Input graph
        :param src: Source vertex for the search
        :param vertex_seq: (Out argument) vertex sequence holding the vertices in the cycle
        :param edge_seq: (Out argument) edge sequence holding the edges in the cycle
        :returns: PgxPath representing the cycle as path, if exists.
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                cycle = analyst.find_cycle(graph)
                print(cycle)
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.find_cycle)

        if vertex_seq is None or isinstance(vertex_seq, str):
            vertex_seq = graph.create_vertex_sequence(vertex_seq)

        if edge_seq is None or isinstance(edge_seq, str):
            edge_seq = graph.create_edge_sequence(edge_seq)

        cycle = None
        if src is None:
            cycle = java_handler(
                self._analyst.findCycle,
                [graph._graph, vertex_seq._collection, edge_seq._collection],
            )
        if isinstance(src, PgxVertex):
            cycle = java_handler(
                self._analyst.findCycle,
                [graph._graph, src._vertex, vertex_seq._collection, edge_seq._collection],
            )
        return PgxPath(graph, cycle)

    def reachability(
        self,
        graph: PgxGraph,
        src: PgxVertex,
        dst: PgxVertex,
        max_hops: int,
        ignore_edge_direction: bool,
    ) -> int:
        """Reachability is a fast way to check if two vertices are reachable from each other.

        :param graph: Input graph
        :param src: Source vertex for the search
        :param dst: Destination vertex for the search
        :param max_hops: Maximum hop distance between the source and destination vertices
        :param ignore_edge_direction: Boolean flag for ignoring the direction of the edges during
            the search
        :returns: The number of hops between the vertices. It will return -1 if the vertices are
            not connected or are not reachable given the condition of the maximum hop distance
            allowed.
        :example:

            .. code-block:: python
                    :linenos:

                    graph = ....
                    src = graph.get_vertex("1")
                    dst = graph.get_vertex("2")
                    result = analyst.reachability(
                        graph, src, dst, 2, ignore_edge_direction=False)
                    print(result)
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.reachability)

        return java_handler(
            self._analyst.reachability,
            [graph._graph, src._vertex, dst._vertex, max_hops, ignore_edge_direction],
        )

    def topological_sort(
        self, graph: PgxGraph, topo_sort: Union[VertexProperty, str] = "topo_sort"
    ) -> VertexProperty:
        """Topological sort gives an order of visit for vertices in directed acyclic graphs.

        :param graph: Input graph
        :param topo_sort: (Out argument) vertex property holding the topological order of each
            vertex
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.topological_sort)

        if isinstance(topo_sort, str):
            topo_sort = graph.create_vertex_property("integer", topo_sort)

        java_handler(self._analyst.topologicalSort, [graph._graph, topo_sort._prop])
        return topo_sort

    def topological_schedule(
        self, graph: PgxGraph, vs: VertexSet, topo_sched: Union[VertexProperty, str] = "topo_sched"
    ) -> VertexProperty:
        """Topological schedule gives an order of visit for the reachable vertices from the source.

        :param graph: Input graph
        :param vs: Set of vertices to be used as the starting points for the scheduling order
        :param topo_sched: (Out argument) vertex property holding the scheduled order of each
            vertex
        :returns: Vertex property holding the scheduled order of each vertex.
        :example:

            .. code-block:: python
                    :linenos:

                    graph = ....
                    source = graph.get_vertices(
                        VertexFilter("vertex.prop1 < 10"))
                    topo_sched = analyst.topological_schedule(
                        graph, source, topo_sched='topo_sched')
                    result_set = graph.query_pgql(
                        "SELECT x, x.topo_sched MATCH (x) "
                        "ORDER BY x.topo_sched DESC")
                    result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.topological_schedule)

        if isinstance(topo_sched, str):
            topo_sched = graph.create_vertex_property("integer", topo_sched)

        java_handler(
            self._analyst.topologicalSchedule, [graph._graph, vs._collection, topo_sched._prop]
        )
        return topo_sched

    def out_degree_distribution(
        self, graph: PgxGraph, dist_map: Optional[Union[PgxMap, str]] = None
    ) -> PgxMap:
        """
        :param graph: Input graph
        :param dist_map: (Out argument) map holding a histogram of the vertex degrees in the graph
        :returns: Map holding a histogram of the vertex degrees in the graph
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                distribution = graph.create_map('integer', 'long')
                analyst.out_degree_distribution(graph, distribution)
                for d in distribution:
                    print(d)
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.out_degree_distribution)

        if dist_map is None or isinstance(dist_map, str):
            dist_map = graph.create_map("integer", "long", dist_map)

        java_handler(self._analyst.outDegreeDistribution, [graph._graph, dist_map._map])
        return dist_map

    def in_degree_distribution(
        self, graph: PgxGraph, dist_map: Optional[Union[PgxMap, str]] = None
    ) -> PgxMap:
        """Calculate the in-degree distribution.

        In-degree distribution gives information about the incoming flows in a graph.

        :param graph: Input graph
        :param dist_map: (Out argument) map holding a histogram of the vertex degrees in the graph
        :returns: Map holding a histogram of the vertex degrees in the graph
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.in_degree_distribution)

        if dist_map is None or isinstance(dist_map, str):
            dist_map = graph.create_map("integer", "long", dist_map)

        java_handler(self._analyst.inDegreeDistribution, [graph._graph, dist_map._map])
        return dist_map

    def prim(
        self, graph: PgxGraph, weight: EdgeProperty, mst: Union[EdgeProperty, str] = "mst"
    ) -> EdgeProperty:
        """Prim reveals tree structures with shortest paths in a graph.

        :param graph: Input graph
        :param weight: Edge property holding the weight of each edge in the graph
        :param mst: Edge property holding the edges belonging to the minimum spanning tree of
            the graph
        :returns: Edge property holding the edges belonging to the minimum spanning tree
            of the graph (i.e. all the edges with in_mst=true)
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                cost = graph.get_or_create_edge_property("double", "cost")
                prim = analyst.prim(graph, cost, mst="mst")
                result_set = graph.query_pgql(
                    "SELECT x, x.mst MATCH (x) ORDER BY x.mst DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.prim)

        if isinstance(mst, str):
            mst = graph.create_edge_property("boolean", mst)

        java_handler(self._analyst.prim, [graph._graph, weight._prop, mst._prop])
        return mst

    def filtered_bfs(
        self,
        graph: PgxGraph,
        root: PgxVertex,
        navigator: VertexFilter,
        init_with_inf: bool = True,
        max_depth: int = 2147483647,
        distance: Union[VertexProperty, str] = "distance",
        parent: Union[VertexProperty, str] = "parent",
    ) -> Tuple[VertexProperty, VertexProperty]:
        """Breadth-first search with an option to filter edges during the traversal of the graph.

        :param graph: Input graph
        :param root: The source vertex from the graph for the path.
        :param navigator: Navigator expression to be evaluated on the vertices during the graph
            traversal
        :param init_with_inf: Boolean flag to set the initial distance values of the vertices.
            If set to true, it will initialize the distances as INF, and -1 otherwise.
        :param max_depth: Maximum depth limit for the BFS traversal
        :param distance: Vertex property holding the hop distance for each reachable vertex in
            the graph
        :param parent: Vertex property holding the parent vertex of the each reachable vertex in
            the path
        :returns: Distance and parent vertex properties
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                cost = graph.get_or_create_vertex_property("double", "cost")
                vertex = graph.get_vertex("1")
                navigator = VertexFilter("vertex.cost < 2")
                bfs = analyst.filtered_bfs(
                    graph, vertex, navigator, distance="distance")
                result_set = graph.query_pgql(
                    "SELECT x, x.distance MATCH (x) ORDER BY x.distance DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.filtered_bfs)

        if isinstance(distance, str):
            distance = graph.create_vertex_property("integer", distance)
        if isinstance(parent, str):
            parent = graph.create_vertex_property("vertex", parent)

        java_handler(
            self._analyst.filteredBfs,
            [
                graph._graph,
                root._vertex,
                navigator._filter,
                init_with_inf,
                distance._prop,
                parent._prop,
            ],
        )
        return (distance, parent)

    def filtered_dfs(
        self,
        graph: PgxGraph,
        root: PgxVertex,
        navigator: VertexFilter,
        init_with_inf: bool = True,
        max_depth: int = 2147483647,
        distance: Union[VertexProperty, str] = "distance",
        parent: Union[VertexProperty, str] = "parent",
    ) -> Tuple[VertexProperty, VertexProperty]:
        """Depth-first search with an option to filter edges during the traversal of the graph.

        :param graph: Input graph
        :param root: The source vertex from the graph for the path
        :param navigator: Navigator expression to be evaluated on the vertices during the graph
            traversal
        :param init_with_inf: Boolean flag to set the initial distance values of the vertices.
            If set to true, it will initialize the distances as INF, and -1 otherwise.
        :param max_depth: Maximum search depth
        :param distance: Vertex property holding the hop distance for each reachable vertex in
            the graph
        :param parent: Vertex property holding the parent vertex of the each reachable vertex in
            the path
        :returns: Distance and parent vertex properties
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                cost = graph.get_or_create_vertex_property("double", "cost")
                vertex = graph.get_vertex("1")
                navigator = VertexFilter("vertex.cost < 2")
                dfs = analyst.filtered_dfs(
                    graph, vertex, navigator, distance="distance")
                result_set = graph.query_pgql(
                    "SELECT x, x.distance MATCH (x) ORDER BY x.distance DESC")
                result_set.print()
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.filtered_dfs)

        if isinstance(distance, str):
            distance = graph.create_vertex_property("integer", distance)
        if isinstance(parent, str):
            parent = graph.create_vertex_property("vertex", parent)

        java_handler(
            self._analyst.filteredDfs,
            [
                graph._graph,
                root._vertex,
                navigator._filter,
                init_with_inf,
                distance._prop,
                parent._prop,
            ],
        )
        return distance, parent

    def all_reachable_vertices_edges(
        self,
        graph: PgxGraph,
        src: PgxVertex,
        dst: PgxVertex,
        k: int,
        filter: Optional[EdgeFilter] = None,
    ) -> Tuple[VertexSet, EdgeSet, PgxMap]:
        """Find all the vertices and edges on a path between the src and target of length smaller
        or equal to k.

        :param graph: Input graph
        :param src: The source vertex
        :param dst: The destination vertex
        :param k: The dimension of the distances property; i.e. number of high-degree vertices.
        :param filter: The filter to be used on edges when searching for a path
        :return: The vertices on the path, the edges on the path and a map containing the
            distances from the source vertex for each vertex on the path
        """
        arguments = locals()
        validate_arguments(arguments, alg_metadata.all_reachable_vertices_edges)

        java_args = [graph._graph, src._vertex, dst._vertex, k]
        if filter is None:
            java_triple = java_handler(self._analyst.allReachableVerticesEdges, java_args)
        else:
            java_args.append(filter._filter)
            java_triple = java_handler(self._analyst.allReachableVerticesEdgesFiltered, java_args)
        return (
            VertexSet(graph, java_triple.left),
            EdgeSet(graph, java_triple.middle),
            PgxMap(graph, java_triple.right),
        )

    def compute_high_degree_vertices(
        self,
        graph: PgxGraph,
        k: int,
        high_degree_vertex_mapping: Optional[Union[PgxMap, str]] = None,
        high_degree_vertices: Optional[Union[VertexSet, str]] = None,
    ) -> Tuple[PgxMap, VertexSet]:
        """Compute the k vertices with the highest degrees in the graph.

        :param graph: Input graph
        :param k: Number of high-degree vertices to be computed
        :param high_degree_vertex_mapping: (out argument) map with the top k high-degree vertices
            and their indices
        :param high_degree_vertices: (out argument) the high-degree vertices
        :return: a map with the top k high-degree vertices and their indices and a vertex
            set containing the same vertices
        """

        arguments = locals()
        validate_arguments(arguments, alg_metadata.compute_high_degree_vertices)

        if high_degree_vertex_mapping is None or isinstance(high_degree_vertex_mapping, str):
            high_degree_vertex_mapping = graph.create_map(
                "integer", "vertex", high_degree_vertex_mapping
            )

        if high_degree_vertices is None or isinstance(high_degree_vertices, str):
            high_degree_vertices = graph.create_vertex_set(high_degree_vertices)

        java_handler(
            self._analyst.computeHighDegreeVertices,
            [graph._graph, k, high_degree_vertex_mapping._map, high_degree_vertices._collection],
        )
        return high_degree_vertex_mapping, high_degree_vertices

    def create_distance_index(
        self,
        graph: PgxGraph,
        high_degree_vertex_mapping: PgxMap,
        high_degree_vertices: VertexSet,
        index: Optional[Union[VertexProperty, str]] = None,
    ) -> VertexProperty:
        """Compute an index with distances to each high-degree vertex

        :param graph: Input graph
        :param high_degree_vertex_mapping: a map with the top k high-degree vertices and their
            indices and a vertex
        :param high_degree_vertices: the high-degree vertices
        :param index: (out-argument) the index containing the distances to each high-degree
            vertex for all vertices
        :return: the index containing the distances to each high-degree vertex for all vertices
        """

        arguments = locals()
        validate_arguments(arguments, alg_metadata.create_distance_index)

        if index is None or isinstance(index, str):
            dim = len(high_degree_vertices)
            index = graph.create_vertex_vector_property("integer", dim, index)

        java_handler(
            self._analyst.createDistanceIndex,
            [
                graph._graph,
                high_degree_vertex_mapping._map,
                high_degree_vertices._collection,
                index._prop,
            ],
        )
        return index

    def bipartite_check(
        self, graph: PgxGraph, is_left: Union[VertexProperty, str] = "is_left"
    ) -> VertexProperty:
        """Verify whether a graph is bipartite.

        :param graph: Input graph
        :param is_left: (out-argument) vertex property holding the side of each
            vertex in a bipartite graph (true for left, false for right).
        :return: vertex property holding the side of each
            vertex in a bipartite graph (true for left, false for right).
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                is_left = graph.get_or_create_vertex_property(
                    "boolean", "is_left")
                bipartite = analyst.bipartite_check(graph, is_left)
                result_set = graph.query_pgql(
                    "SELECT x, x.is_left MATCH (x) ORDER BY x.is_left DESC")
                result_set.print()
        """

        arguments = locals()
        validate_arguments(arguments, alg_metadata.bipartite_check)

        if is_left is None or isinstance(is_left, str):
            is_left = graph.create_vertex_property("boolean", is_left)

        java_handler(self._analyst.bipartiteCheck, [graph._graph, is_left._prop])
        return is_left

    def enumerate_simple_paths(
        self,
        graph: PgxGraph,
        src: PgxVertex,
        dst: PgxVertex,
        k: int,
        vertices_on_path: VertexSet,
        edges_on_path: EdgeSet,
        dist: PgxMap,
    ) -> Tuple[List[int], VertexSet, EdgeSet]:
        """Enumerate simple paths between the source and destination vertex.

        :param graph: Input graph
        :param src: The source vertex
        :param dst: The destination vertex
        :param k: maximum number of iterations
        :param vertices_on_path: VertexSet containing all vertices to be considered while
            enumerating paths
        :param edges_on_path: EdgeSet containing all edges to be consider while enumerating paths
        :param dist: map containing the hop-distance from the source vertex to each vertex that is
            to be considered while enumerating the paths
        :return: Triple containing containing the path lengths, a vertex-sequence
            containing the vertices on the paths and edge-sequence containing the edges on the
            paths
        """

        arguments = locals()
        validate_arguments(arguments, alg_metadata.enumerate_simple_paths)

        java_triple = java_handler(
            self._analyst.enumerateSimplePaths,
            [
                graph._graph,
                src._vertex,
                dst._vertex,
                k,
                vertices_on_path._collection,
                edges_on_path._collection,
                dist._map,
            ],
        )

        path_lengths = list(java_triple.left)
        path_vertices = VertexSet(graph, java_triple.middle)
        path_edges = EdgeSet(graph, java_triple.right)
        return path_lengths, path_vertices, path_edges

    def limited_shortest_path_hop_dist(
        self,
        graph: PgxGraph,
        src: PgxVertex,
        dst: PgxVertex,
        max_hops: int,
        high_degree_vertex_mapping: PgxMap,
        high_degree_vertices: VertexSet,
        index: VertexProperty,
        path_vertices: Optional[Union[VertexSequence, str]] = None,
        path_edges: Optional[Union[EdgeSequence, str]] = None,
    ) -> Tuple[VertexSequence, EdgeSequence]:
        """Compute the shortest path between the source and destination vertex.

        The algorithm only considers paths up to a length of k.

        :param graph: Input graph
        :param src: The source vertex
        :param dst: The destination vertex
        :param max_hops: The maximum number of edges to follow when trying to find a path
        :param high_degree_vertex_mapping: Map with the top k high-degree vertices
            and their indices
        :param high_degree_vertices: The high-degree vertices
        :param index: Index containing distances to high-degree vertices
        :param path_vertices: (out-argument) will contain the vertices on the found path
            or will be empty if there is none
        :param path_edges: (out-argument) will contain the vertices on the found path or
            will be empty if there is none
        :return: A tuple containing the vertices in the shortest path from src to dst and the
            edges on the path. Both will be empty if there is no path within maxHops steps
        """

        arguments = locals()
        validate_arguments(arguments, alg_metadata.limited_shortest_path_hop_dist)

        if path_vertices is None or isinstance(path_vertices, str):
            path_vertices = graph.create_vertex_sequence()

        if path_edges is None or isinstance(path_edges, str):
            path_edges = graph.create_edge_sequence()

        pair = java_handler(
            self._analyst.limitedShortestPathHopDist,
            [
                graph._graph,
                src._vertex,
                dst._vertex,
                max_hops,
                high_degree_vertex_mapping._map,
                high_degree_vertices._collection,
                index._prop,
                path_vertices._collection,
                path_edges._collection,
            ],
        )
        return VertexSequence(graph, pair.getFirst()), EdgeSequence(graph, pair.getSecond())

    def limited_shortest_path_hop_dist_filtered(
        self,
        graph: PgxGraph,
        src: PgxVertex,
        dst: PgxVertex,
        max_hops: int,
        high_degree_vertex_mapping: PgxMap,
        high_degree_vertices: VertexSet,
        index: VertexProperty,
        filter: EdgeFilter,
        path_vertices: Optional[Union[VertexSequence, str]] = None,
        path_edges: Optional[Union[EdgeSequence, str]] = None,
    ) -> Tuple[VertexSequence, EdgeSequence]:
        """Compute the shortest path between the source and destination vertex.

        The algorithm only considers paths up to a length of k.

        :param graph: Input graph
        :param src: The source vertex
        :param dst: The destination vertex
        :param max_hops: The maximum number of edges to follow when trying to find a path
        :param high_degree_vertex_mapping: Map with the top k high-degree vertices
            and their indices
        :param high_degree_vertices: The high-degree vertices
        :param index: Index containing distances to high-degree vertices
        :param filter: Filter to be evaluated on the edges when searching for a path
        :param path_vertices: (out-argument) will contain the vertices on the found path
            or will be empty if there is none
        :param path_edges: (out-argument) will contain the vertices on the found path or
            will be empty if there is none
        :return: A tuple containing the vertices in the shortest path from src to dst and the
            edges on the path. Both will be empty if there is no path within maxHops steps
        """

        arguments = locals()
        validate_arguments(arguments, alg_metadata.limited_shortest_path_hop_dist_filtered)

        if path_vertices is None or isinstance(path_vertices, str):
            path_vertices = graph.create_vertex_sequence(path_vertices)

        if path_edges is None or isinstance(path_edges, str):
            path_edges = graph.create_edge_sequence(path_edges)

        pair = java_handler(
            self._analyst.limitedShortestPathHopDistFiltered,
            [
                graph._graph,
                src._vertex,
                dst._vertex,
                max_hops,
                high_degree_vertex_mapping._map,
                high_degree_vertices._collection,
                index._prop,
                filter._filter,
                path_vertices._collection,
                path_edges._collection,
            ],
        )
        return VertexSequence(graph, pair.getFirst()), EdgeSequence(graph, pair.getSecond())

    def random_walk_with_restart(
        self,
        graph: PgxGraph,
        source: PgxVertex,
        length: int,
        reset_prob: float,
        visit_count: Optional[PgxMap] = None,
    ) -> PgxMap:
        """Perform a random walk over the graph.

        The walk will start at the given source vertex and will randomly visit neighboring vertices
        in the graph, with a probability equal to the value of reset_probability of going back to
        the starting point.  The random walk will also go back to the starting point every time it
        reaches a vertex with no outgoing edges. The algorithm will stop once it reaches the
        specified walk length.

        :param graph: Input graph
        :param source: Starting point of the random walk
        :param length: Length (number of steps) of the random walk
        :param reset_prob: Probability value for resetting the random walk
        :param visit_count: (out argument) map holding the number of visits during the random walk
            for each vertex in the graph
        :return: map holding the number of visits during the random walk for each vertex in the
            graph
        :example:

            .. code-block:: python
                :linenos:

                graph = ....
                src = graph.get_vertex("1")
                visits = analyst.random_walk_with_restart(
                    graph, src, length=100, reset_prob=0.6)
                for visit in visits:
                    print(visit)
        """

        arguments = locals()
        validate_arguments(arguments, alg_metadata.random_walk_with_restart)

        if visit_count is None:
            visit_count = graph.create_map("vertex", "integer")

        java_map = java_handler(
            self._analyst.randomWalkWithRestart,
            [graph._graph, source._vertex, length, reset_prob, visit_count._map],
        )
        return PgxMap(graph, java_map)

    def matrix_factorization_recommendations(
        self,
        bipartite_graph: BipartiteGraph,
        user: PgxVertex,
        vector_length: int,
        feature: VertexProperty,
        estimated_rating: Optional[Union[VertexProperty, str]] = None,
    ) -> VertexProperty:
        """Complement for Matrix Factorization.

        The generated feature vectors will be used for making predictions in cases where the given
        user vertex has not been related to a particular item from the item set. Similarly to the
        recommendations from matrix factorization, this algorithm will perform dot products between
        the given user vertex and the rest of vertices in the graph, giving a score of 0 to the
        items that are already related to the user and to the products with other user vertices,
        hence returning the results of the dot products for the unrelated item vertices. The scores
        from those dot products can be interpreted as the predicted scores for the unrelated items
        given a particular user vertex.

        :param bipartite_graph: Bipartite input graph
        :param user: Vertex from the left (user) side of the graph
        :param vector_length: size of the feature vectors
        :param feature: vertex property holding the feature vectors for each vertex
        :param estimated_rating: (out argument) vertex property holding the estimated rating score
            for each vertex
        :return: vertex property holding the estimated rating score for each vertex
        """

        arguments = locals()
        validate_arguments(arguments, alg_metadata.matrix_factorization_recommendations)

        if estimated_rating is None or isinstance(estimated_rating, str):
            estimated_rating = bipartite_graph.create_vertex_property("double", estimated_rating)

        java_handler(
            self._analyst.matrixFactorizationRecommendations,
            [
                bipartite_graph._graph,
                user._vertex,
                vector_length,
                feature._prop,
                estimated_rating._prop,
            ],
        )
        return estimated_rating

    def __hash__(self) -> NoReturn:
        raise TypeError(UNHASHABLE_TYPE.format(type_name=self.__class__))
