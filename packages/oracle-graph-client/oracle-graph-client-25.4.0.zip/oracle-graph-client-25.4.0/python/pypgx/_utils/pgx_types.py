#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from jnius import autoclass
from typing import Dict, Any
from pypgx._utils.error_messages import INVALID_OPTION

Integer = autoclass('java.lang.Integer')
Long = autoclass('java.lang.Long')
Float = autoclass('java.lang.Float')
Double = autoclass('java.lang.Double')
Boolean = autoclass('java.lang.Boolean')
String = autoclass('java.lang.String')

aggregates = {}
picking_functions = {}
label_merging_functions = {}
merging_functions = {}
authorization_types = {}
id_types = {}
id_generation_strategies = {}
property_merge_strategies = {}
id_strategies = {}
on_add_existing_element_types = {}
on_invalid_change_types = {}
on_required_conversion_types = {}
property_types = {}
format_types = {}
provider_format_types = {}
filter_types = {}
source_types = {}
read_graph_options = {}
vertex_props = {}
edge_props = {}
pgx_entities = {}
pgx_resource_permissions = {}
pgx_general_permissions = {}
collection_types = {}
direction_types = {}
graph_builder_config_fields = {}
graph_property_config_fields = {}
string_pooling_strategies = {}
time_units = {}
memory_units = {}
compiler_optimizations = {}
task_priorities = {}
update_consistency_models = {}

sort_order = {}
degree_type = {}
mode = {}
self_edges = {}
multi_edges = {}
trivial_vertices = {}

vector_types = ('integer', 'long', 'double', 'float')
col_types = (
    'vertex',
    'edge',
    'point2d',
    'date',
    'time',
    'timestamp',
    'time_with_timezone',
    'timestamp_with_timezone',
    'vertex_labels',
    'array',
    'boolean',
)

local_date = autoclass('java.time.LocalDate')
local_time = autoclass('java.time.LocalTime')
timestamp = autoclass('java.time.LocalDateTime')
time_with_timezone = autoclass('java.time.OffsetTime')
timestamp_with_timezone = autoclass('java.time.OffsetDateTime')
java_collection = autoclass('java.util.Collection')
legacy_date = autoclass('java.util.Date')
java_set = autoclass('java.util.Set')
java_list = autoclass('java.util.List')
array_list = autoclass('java.util.ArrayList')
java_map = autoclass('java.util.Map')
HashMap = autoclass('java.util.HashMap')
HashSet = autoclass('java.util.HashSet')
pgx_vect = autoclass("oracle.pgx.api.PgxVect")
Enum = autoclass('java.lang.Enum')
Point2D = autoclass('oracle.pgql.lang.spatial.Point2D')
abstract_config = autoclass('oracle.pgx.config.AbstractConfig')
graph_config = autoclass('oracle.pgx.config.GraphConfig')
file_graph_config = autoclass('oracle.pgx.config.FileGraphConfig')
two_tables_text_graph_config = autoclass('oracle.pgx.config.TwoTablesTextGraphConfig')
partitioned_graph_config = autoclass('oracle.pgx.config.PartitionedGraphConfig')
rdf_graph_config = autoclass('oracle.pgx.config.RdfGraphConfig')
two_tables_rdbms_graph_config = autoclass('oracle.pgx.config.TwoTablesRdbmsGraphConfig')
graph_property_config = autoclass('oracle.pgx.config.GraphPropertyConfig')
task_priority = autoclass("oracle.pgx.config.TaskPriority")
update_consistency_model = autoclass("oracle.pgx.config.UpdateConsistencyModel")
key_column_descriptor = autoclass("oracle.pgx.api.keys.KeyColumnDescriptor")
property_loading_option = autoclass('oracle.pgx.config.ReadGraphOption$PropertyLoadingOption')


def _set_up_types() -> None:
    """Set up the types in this module."""

    # The reason this function exists is to avoid having helper variables
    # exported (this function's local variables aren't exported by the module).

    aggregate = autoclass('oracle.pgx.config.Aggregate')
    picking_function = autoclass("oracle.pgx.common.mutations.PickingStrategyFunction")
    label_merging_function = autoclass("oracle.pgx.common.mutations.LabelMergingFunction")
    merging_function = autoclass("oracle.pgx.common.mutations.MergingFunction")
    authorization_type = autoclass('oracle.pgx.common.types.AuthorizationType')
    id_type = autoclass('oracle.pgx.common.types.IdType')
    id_generation_strategy = autoclass('oracle.pgx.config.IdGenerationStrategy')
    property_merge_strategy = autoclass('oracle.pgx.api.expansion.PropertyMergeStrategy')
    id_strategy = autoclass('oracle.pgx.common.types.IdStrategy')
    on_add_existing_element = autoclass('oracle.pgx.config.OnAddExistingElement')
    on_invalid_change = autoclass('oracle.pgx.config.OnInvalidChange')
    on_required_conversion = autoclass('oracle.pgx.config.OnRequiredConversion')
    pgx_resource_permission = autoclass('oracle.pgx.common.auth.PgxResourcePermission')
    pgx_general_permission = autoclass('oracle.pgx.common.auth.PgxGeneralPermission')
    property_type = autoclass('oracle.pgx.common.types.PropertyType')
    direction_type = autoclass('oracle.pgx.common.types.Direction')
    format_type = autoclass('oracle.pgx.config.Format')
    provider_format_type = autoclass('oracle.pgx.config.ProviderFormat')
    source_type = autoclass('oracle.pgx.api.GraphSource')
    read_graph_option = autoclass('oracle.pgx.config.ReadGraphOption')
    vertex_property = autoclass('oracle.pgx.api.VertexProperty')
    edge_property = autoclass('oracle.pgx.api.EdgeProperty')
    graph_builder_config_field = autoclass('oracle.pgx.config.GraphBuilderConfig$Field')
    graph_property_config_field = autoclass('oracle.pgx.config.GraphPropertyConfig$Field')
    string_pooling_strategy = autoclass('oracle.pgx.config.StringPoolingStrategy')
    time_unit = autoclass('java.util.concurrent.TimeUnit')
    memory_unit = autoclass('oracle.pgx.common.MemoryUnit')
    compiler_optimization = autoclass('oracle.pgx.api.GmCompilerOptimization')

    aggregates['identity'] = aggregate.IDENTITY
    aggregates['group_key'] = aggregate.GROUP_KEY
    aggregates['min'] = aggregate.MIN
    aggregates['max'] = aggregate.MAX
    aggregates['sum'] = aggregate.SUM
    aggregates['avg'] = aggregate.AVG
    aggregates['concat'] = aggregate.CONCAT
    aggregates['count'] = aggregate.COUNT

    picking_functions['min'] = picking_function.MIN
    picking_functions['max'] = picking_function.MAX

    label_merging_functions['min'] = label_merging_function.MIN
    label_merging_functions['max'] = label_merging_function.MAX

    merging_functions['min'] = merging_function.MIN
    merging_functions['max'] = merging_function.MAX
    merging_functions['sum'] = merging_function.SUM

    authorization_types['user'] = authorization_type.USER
    authorization_types['role'] = authorization_type.ROLE

    id_types['integer'] = id_type.INTEGER
    id_types['long'] = id_type.LONG
    id_types['string'] = id_type.STRING

    id_generation_strategies['user_ids'] = id_generation_strategy.USER_IDS
    id_generation_strategies['auto_generated'] = id_generation_strategy.AUTO_GENERATED

    property_merge_strategies['keep_current_values'] = \
        property_merge_strategy.KEEP_CURRENT_VALUES
    property_merge_strategies['update_with_new_values'] = \
        property_merge_strategy.UPDATE_WITH_NEW_VALUES

    id_strategies['no_ids'] = id_strategy.NO_IDS
    id_strategies['keys_as_ids'] = id_strategy.KEYS_AS_IDS
    id_strategies['unstable_generated_ids'] = id_strategy.UNSTABLE_GENERATED_IDS
    id_strategies['partitioned_ids'] = id_strategy.PARTITIONED_IDS

    on_add_existing_element_types['error'] = on_add_existing_element.ERROR
    on_add_existing_element_types['warn'] = on_add_existing_element.WARN
    on_add_existing_element_types['warn_once'] = on_add_existing_element.WARN_ONCE
    on_add_existing_element_types['ignore'] = on_add_existing_element.IGNORE

    on_invalid_change_types['ignore'] = on_invalid_change.IGNORE
    on_invalid_change_types['ignore_and_log'] = on_invalid_change.IGNORE_AND_LOG
    on_invalid_change_types['ignore_and_log_once'] = on_invalid_change.IGNORE_AND_LOG_ONCE
    on_invalid_change_types['error'] = on_invalid_change.ERROR

    on_required_conversion_types['convert'] = on_required_conversion.CONVERT
    on_required_conversion_types['convert_and_log'] = on_required_conversion.CONVERT_AND_LOG
    on_required_conversion_types['convert_and_log_once'] = \
        on_required_conversion.CONVERT_AND_LOG_ONCE
    on_required_conversion_types['error'] = on_required_conversion.ERROR

    property_types['integer'] = property_type.INTEGER
    property_types['long'] = property_type.LONG
    property_types['float'] = property_type.FLOAT
    property_types['double'] = property_type.DOUBLE
    property_types['boolean'] = property_type.BOOLEAN
    property_types['string'] = property_type.STRING
    property_types['vertex'] = property_type.VERTEX
    property_types['edge'] = property_type.EDGE
    property_types['local_date'] = property_type.LOCAL_DATE
    property_types['time'] = property_type.TIME
    property_types['timestamp'] = property_type.TIMESTAMP
    property_types['time_with_timezone'] = property_type.TIME_WITH_TIMEZONE
    property_types['timestamp_with_timezone'] = property_type.TIMESTAMP_WITH_TIMEZONE
    property_types['point2d'] = property_type.POINT2D

    direction_types['outgoing'] = direction_type.OUTGOING
    direction_types['incoming'] = direction_type.INCOMING
    direction_types['both'] = direction_type.BOTH

    format_types['pgb'] = format_type.PGB
    format_types['edge_list'] = format_type.EDGE_LIST
    format_types['two_tables'] = format_type.TWO_TABLES
    format_types['adj_list'] = format_type.ADJ_LIST
    format_types['flat_file'] = format_type.FLAT_FILE
    format_types['graphml'] = format_type.GRAPHML
    format_types['pg'] = format_type.PG
    format_types['rdf'] = format_type.RDF
    format_types['csv'] = format_type.CSV

    provider_format_types["pgb"] = provider_format_type.PGB
    provider_format_types["rdbms"] = provider_format_type.RDBMS
    provider_format_types["csv"] = provider_format_type.CSV
    provider_format_types["es"] = provider_format_type.ES

    source_types['pg_view'] = source_type.PG_VIEW
    source_types['pg_pgql'] = source_type.PG_PGQL
    source_types['pg_sql'] = source_type.PG_SQL

    read_graph_options['optimized_for_updates'] = read_graph_option.OPTIMIZED_FOR_UPDATES
    read_graph_options['optimized_for_read'] = read_graph_option.OPTIMIZED_FOR_READ
    read_graph_options['synchronizable'] = read_graph_option.SYNCHRONIZABLE
    read_graph_options['on_missing_vertex_ignore_edge'] = \
        read_graph_option.ON_MISSING_VERTEX_IGNORE_EDGE
    read_graph_options['on_missing_vertex_ignore_edge_log'] = \
        read_graph_option.ON_MISSING_VERTEX_IGNORE_EDGE_LOG
    read_graph_options['on_missing_vertex_ignore_edge_log_once'] = \
        read_graph_option.ON_MISSING_VERTEX_IGNORE_EDGE_LOG_ONCE
    read_graph_options['on_missing_vertex_error'] = read_graph_option.ON_MISSING_VERTEX_ERROR

    filter_types['vertex'] = autoclass('oracle.pgx.api.filter.VertexFilter')
    filter_types['edge'] = autoclass('oracle.pgx.api.filter.EdgeFilter')
    filter_types['path_finding'] = autoclass('oracle.pgx.api.filter.PathFindingFilter')

    pgx_entities['vertex'] = autoclass('oracle.pgx.api.PgxVertex')
    pgx_entities['edge'] = autoclass('oracle.pgx.api.PgxEdge')

    pgx_resource_permissions['none'] = pgx_resource_permission.NONE
    pgx_resource_permissions['read'] = pgx_resource_permission.READ
    pgx_resource_permissions['write'] = pgx_resource_permission.WRITE
    pgx_resource_permissions['export'] = pgx_resource_permission.EXPORT
    pgx_resource_permissions['manage'] = pgx_resource_permission.MANAGE

    pgx_general_permissions['none'] = pgx_general_permission.NONE
    pgx_general_permissions['server_get_info'] = pgx_general_permission.SERVER_GET_INFO
    pgx_general_permissions['server_manage'] = pgx_general_permission.SERVER_MANAGE
    pgx_general_permissions['session_add_published_graph'] = \
        pgx_general_permission.SESSION_ADD_PUBLISHED_GRAPH
    pgx_general_permissions['session_compile_algorithm'] = \
        pgx_general_permission.SESSION_COMPILE_ALGORITHM
    pgx_general_permissions['session_create'] = pgx_general_permission.SESSION_CREATE
    pgx_general_permissions['session_get_published_graph'] = \
        pgx_general_permission.SESSION_GET_PUBLISHED_GRAPH
    pgx_general_permissions['session_new_graph'] = pgx_general_permission.SESSION_NEW_GRAPH
    pgx_general_permissions['session_read_model'] = \
        pgx_general_permission.SESSION_READ_MODEL
    pgx_general_permissions['session_modify_model'] = \
        pgx_general_permission.SESSION_MODIFY_MODEL

    collection_types['vertex_sequence'] = autoclass('oracle.pgx.api.VertexSequence')
    collection_types['vertex_set'] = autoclass('oracle.pgx.api.VertexSet')
    collection_types['edge_sequence'] = autoclass('oracle.pgx.api.EdgeSequence')
    collection_types['edge_set'] = autoclass('oracle.pgx.api.EdgeSet')

    java_sort_order = autoclass('oracle.pgx.api.PgxGraph$SortOrder')
    sort_order[True] = java_sort_order.ASCENDING
    sort_order[False] = java_sort_order.DESCENDING

    java_degree = autoclass('oracle.pgx.api.PgxGraph$Degree')
    degree_type[True] = java_degree.IN
    degree_type[False] = java_degree.OUT

    java_mode = autoclass('oracle.pgx.api.PgxGraph$Mode')
    mode[True] = java_mode.MUTATE_IN_PLACE
    mode[False] = java_mode.CREATE_COPY

    java_self_edges = autoclass('oracle.pgx.api.PgxGraph$SelfEdges')
    self_edges[True] = java_self_edges.KEEP_SELF_EDGES
    self_edges[False] = java_self_edges.REMOVE_SELF_EDGES

    java_multi_edges = autoclass('oracle.pgx.api.PgxGraph$MultiEdges')
    multi_edges[True] = java_multi_edges.KEEP_MULTI_EDGES
    multi_edges[False] = java_multi_edges.REMOVE_MULTI_EDGES

    java_trivial_vertices = autoclass('oracle.pgx.api.PgxGraph$TrivialVertices')
    trivial_vertices[True] = java_trivial_vertices.KEEP_TRIVIAL_VERTICES
    trivial_vertices[False] = java_trivial_vertices.REMOVE_TRIVIAL_VERTICES

    vertex_props[True] = vertex_property.ALL
    vertex_props[False] = vertex_property.NONE

    edge_props[True] = edge_property.ALL
    edge_props[False] = edge_property.NONE

    graph_builder_config_fields['retain_edge_id'] = \
        graph_builder_config_field.RETAIN_EDGE_ID
    graph_builder_config_fields['retain_vertex_id'] = \
        graph_builder_config_field.RETAIN_VERTEX_ID
    graph_builder_config_fields['vertex_id_generation_strategy'] = \
        graph_builder_config_field.VERTEX_ID_GENERATION_STRATEGY
    graph_builder_config_fields['edge_id_generation_strategy'] = \
        graph_builder_config_field.EDGE_ID_GENERATION_STRATEGY

    graph_property_config_fields['name'] = graph_property_config_field.NAME
    graph_property_config_fields['dimension'] = graph_property_config_field.DIMENSION
    graph_property_config_fields['format'] = graph_property_config_field.FORMAT
    graph_property_config_fields['type'] = graph_property_config_field.TYPE
    graph_property_config_fields['default'] = graph_property_config_field.DEFAULT
    graph_property_config_fields['column'] = graph_property_config_field.COLUMN
    graph_property_config_fields['stores'] = graph_property_config_field.STORES
    graph_property_config_fields['max_distinct_strings_per_pool'] = \
        graph_property_config_field.MAX_DISTINCT_STRINGS_PER_POOL
    graph_property_config_fields['string_pooling_strategy'] = \
        graph_property_config_field.STRING_POOLING_STRATEGY
    graph_property_config_fields['aggregate'] = graph_property_config_field.AGGREGATE
    graph_property_config_fields['field'] = graph_property_config_field.FIELD
    graph_property_config_fields['group_key'] = graph_property_config_field.GROUP_KEY
    graph_property_config_fields['drop_after_loading'] = \
        graph_property_config_field.DROP_AFTER_LOADING

    string_pooling_strategies['indexed'] = string_pooling_strategy.INDEXED
    string_pooling_strategies['on_heap'] = string_pooling_strategy.ON_HEAP
    string_pooling_strategies['none'] = string_pooling_strategy.NONE

    time_units['days'] = time_unit.DAYS
    time_units['hours'] = time_unit.HOURS
    time_units['microseconds'] = time_unit.MICROSECONDS
    time_units['milliseconds'] = time_unit.MILLISECONDS
    time_units['minutes'] = time_unit.MINUTES
    time_units['nanoseconds'] = time_unit.NANOSECONDS
    time_units['seconds'] = time_unit.SECONDS

    memory_units['megabyte'] = memory_unit.MEGABYTE
    memory_units['gigabyte'] = memory_unit.GIGABYTE
    memory_units['terabyte'] = memory_unit.TERABYTE

    compiler_optimizations['auto_transform_ms_bfs'] = compiler_optimization.AUTO_TRANSFORM_MS_BFS
    compiler_optimizations['common_neighbor_iteration'] = (
        compiler_optimization.COMMON_NEIGHBOR_ITERATION
    )
    compiler_optimizations['common_neighbor_iteration_early_pruning'] = (
        compiler_optimization.COMMON_NEIGHBOR_ITERATION_EARLY_PRUNING
    )
    compiler_optimizations['edge_iterator_to_node_iterator'] = (
        compiler_optimization.EDGE_ITERATOR_TO_NODE_ITERATOR
    )
    compiler_optimizations['eliminate_empty_code'] = (
        compiler_optimization.ELIMINATE_EMPTY_CODE
    )
    compiler_optimizations['eliminate_unused_variables'] = (
        compiler_optimization.ELIMINATE_UNUSED_VARIABLES
    )
    compiler_optimizations['fixed_print_order'] = compiler_optimization.FIXED_PRINT_ORDER
    compiler_optimizations['flip_bfs_edges'] = compiler_optimization.FLIP_BFS_EDGES
    compiler_optimizations['flip_foreach_edges'] = compiler_optimization.FLIP_FOREACH_EDGES
    compiler_optimizations['hoist_resources'] = compiler_optimization.HOIST_RESOURCES
    compiler_optimizations['hoist_statements'] = compiler_optimization.HOIST_STATEMENTS
    compiler_optimizations['inline_vector_operators'] = (
        compiler_optimization.INLINE_VECTOR_OPERATORS
    )
    compiler_optimizations['merge_loops'] = compiler_optimization.MERGE_LOOPS
    compiler_optimizations['merge_properties'] = compiler_optimization.MERGE_PROPERTIES
    compiler_optimizations['move_assigns'] = compiler_optimization.MOVE_ASSIGNS
    compiler_optimizations['move_foreach'] = compiler_optimization.MOVE_FOREACH
    compiler_optimizations['optimize_reductions'] = compiler_optimization.OPTIMIZE_REDUCTIONS
    compiler_optimizations['precompute_degree'] = compiler_optimization.PRECOMPUTE_DEGREE
    compiler_optimizations['privatization'] = compiler_optimization.PRIVATIZATION
    compiler_optimizations['propagate_writes'] = compiler_optimization.PROPAGATE_WRITES
    compiler_optimizations['remove_unused_properties'] = (
        compiler_optimization.REMOVE_UNUSED_PROPERTIES
    )
    compiler_optimizations['remove_unused_scalars'] = compiler_optimization.REMOVE_UNUSED_SCALARS
    compiler_optimizations['select_map_implementation'] = (
        compiler_optimization.SELECT_MAP_IMPLEMENTATION
    )
    compiler_optimizations['select_parallel_regions'] = (
        compiler_optimization.SELECT_PARALLEL_REGIONS
    )
    compiler_optimizations['select_seq_implementation'] = (
        compiler_optimization.SELECT_SEQ_IMPLEMENTATION
    )
    compiler_optimizations['simplify_min_max_assign'] = (
        compiler_optimization.SIMPLIFY_MIN_MAX_ASSIGN
    )
    compiler_optimizations['specialize_graph_types'] = compiler_optimization.SPECIALIZE_GRAPH_TYPES

    task_priorities["high"] = task_priority.HIGH
    task_priorities["medium"] = task_priority.MEDIUM
    task_priorities["low"] = task_priority.LOW

    cancel_tasks = update_consistency_model.CANCEL_TASKS
    allow_inconsistencies = update_consistency_model.ALLOW_INCONSISTENCIES
    update_consistency_models["cancel_tasks"] = cancel_tasks
    update_consistency_models["allow_inconsistencies"] = allow_inconsistencies


_set_up_types()

ACTIVATION_FUNCTION = autoclass('oracle.pgx.config.mllib.ActivationFunction')
ACTIVATION_FUNCTIONS = {
    'leaky_relu': ACTIVATION_FUNCTION.LEAKY_RELU,
    'relu': ACTIVATION_FUNCTION.RELU,
    'linear': ACTIVATION_FUNCTION.LINEAR,
    'tanh': ACTIVATION_FUNCTION.TANH,
}

POOL_TYPE = autoclass('oracle.pgx.api.PoolType')
POOL_TYPES = {
    'server_thread': POOL_TYPE.SERVER_THREAD,
    'fast_track_analysis_pool': POOL_TYPE.FAST_TRACK_ANALYSIS_POOL,
    'analysis_pool': POOL_TYPE.ANALYSIS_POOL,
    'io_pool': POOL_TYPE.IO_POOL,
}

WEIGHT_INIT_SCHEME = autoclass('oracle.pgx.config.mllib.WeightInitScheme')
WEIGHT_INIT_SCHEMES = {
    'zeros': WEIGHT_INIT_SCHEME.ZEROS,
    'ones': WEIGHT_INIT_SCHEME.ONES,
    'xavier_uniform': WEIGHT_INIT_SCHEME.XAVIER_UNIFORM,
    'he': WEIGHT_INIT_SCHEME.HE,
    'xavier': WEIGHT_INIT_SCHEME.XAVIER,
}

AGGREGATION_OPERATION = autoclass('oracle.pgx.config.mllib.AggregationOperation')
AGGREGATION_OPERATION = {
    'mean': AGGREGATION_OPERATION.MEAN,
}

EVALUATION_FREQUENCY_SCALE = autoclass('oracle.pgx.config.mllib.EvaluationFrequencyScale')
EVALUATION_FREQUENCY_SCALE = {
    'epoch': EVALUATION_FREQUENCY_SCALE.EPOCH,
    'step': EVALUATION_FREQUENCY_SCALE.STEP,
}

SUPERVISED_LOSS_FUNCTIONS = {
    'softmax_cross_entropy': 'SoftmaxCrossEntropyLoss',
    'sigmoid_cross_entropy': 'SigmoidCrossEntropyLoss',
    'mse': 'MSELoss',
}

UNSUPERVISED_LOSS_FUNCTION = autoclass(
    'oracle.pgx.config.mllib.UnsupervisedGraphWiseModelConfig$LossFunction'
)
UNSUPERVISED_EDGEWISE_LOSS_FUNCTION = autoclass(
    'oracle.pgx.config.mllib.UnsupervisedEdgeWiseModelConfig$LossFunction'
)
UNSUPERVISED_LOSS_FUNCTIONS = {
    'sigmoid_cross_entropy': UNSUPERVISED_LOSS_FUNCTION.SIGMOID_CROSS_ENTROPY,
}
UNSUPERVISED_EDGEWISE_LOSS_FUNCTIONS = {
    'sigmoid_cross_entropy': UNSUPERVISED_EDGEWISE_LOSS_FUNCTION.SIGMOID_CROSS_ENTROPY,
}

READOUT_FUNCTION = autoclass('oracle.pgx.config.mllib.GraphWiseDgiLayerConfig$ReadoutFunction')
READOUT_FUNCTIONS = {"mean": READOUT_FUNCTION.MEAN}

DISCRIMINATOR_FUNCTION = autoclass(
    'oracle.pgx.config.mllib.GraphWiseDgiLayerConfig$Discriminator'
)
DISCRIMINATOR_FUNCTIONS = {"bilinear": DISCRIMINATOR_FUNCTION.BILINEAR}
BATCH_GENERATOR = autoclass('oracle.pgx.config.mllib.batchgenerator.BatchGenerator')
BATCH_GENERATORS = {
    'standard': autoclass('oracle.pgx.config.mllib.batchgenerator.StandardBatchGenerator'),
    'stratified_oversampling': autoclass(
        'oracle.pgx.config.mllib.batchgenerator.StratifiedOversamplingBatchGenerator'
    ),
}


def include_properties(properties: Dict) -> Any:
    """
    Create  a property loading option, which specifies loading with only included properties.
    :param properties:  properties
    :return: key, option for include property
    :raises ValueError: If `properties` is not dict.
    """
    if not isinstance(properties, dict):
        raise ValueError(
            INVALID_OPTION.format(var='properties map',
                                  opts=properties)
        )
    prop_map = autoclass('java.util.HashMap')()
    read_graph_option = autoclass('oracle.pgx.config.ReadGraphOption')
    for key, value in properties.items():
        provider = key
        prop_list = autoclass('java.util.ArrayList')()
        if isinstance(value, list):
            for item in value:
                prop_list.add(item)
        else:
            prop_list.add(value)
        prop_map.put(provider, prop_list)
    return read_graph_option.includeProperties(prop_map)


def exclude_properties(properties: dict) -> Any:
    """
    Create a property loading option, which specifies loading without excluded properties.
    :param properties:  properties
    :return: key, option for exclude property
    :raises ValueError: If `properties` is not dict.
    """
    if not isinstance(properties, dict):
        raise ValueError(
            INVALID_OPTION.format(var='properties map',
                                  opts=properties)
        )
    prop_map = autoclass('java.util.HashMap')()
    read_graph_option = autoclass('oracle.pgx.config.ReadGraphOption')
    for key, value in properties.items():
        provider = key
        prop_list = autoclass('java.util.ArrayList')()
        if isinstance(value, list):
            for item in value:
                prop_list.add(item)
        else:
            prop_list.add(value)
        prop_map.put(provider, prop_list)
    return read_graph_option.excludeProperties(prop_map)


def topology_only() -> Any:
    """
    Create a property loading option, which specifies loading with topology only
    :return: key, option for load property only
    """
    read_graph_option = autoclass('oracle.pgx.config.ReadGraphOption')
    return read_graph_option.topologyOnly()


def _check_and_get_value(value_name: str, value: str, pgx_type: Dict[str, Any]) -> Any:
    if value not in pgx_type.keys():
        raise ValueError(
            INVALID_OPTION.format(
                var=value_name,
                opts=', '.join(pgx_type.keys())
            )
        )
    return pgx_type[value]
