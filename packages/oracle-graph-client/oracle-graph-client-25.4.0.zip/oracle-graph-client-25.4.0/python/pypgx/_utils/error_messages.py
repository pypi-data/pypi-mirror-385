#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

ABSTRACT_METHOD = "abstract method, implemented only in subclasses"
ARG_MUST_BE = "'{arg}' must be: {type}."
ARG_MUST_BE_REASON = "'{arg}' must be: {value}. {cause}"
INVALID_OPTION = "Invalid '{var}'. Valid options are: {opts}"
INVALID_COMBINATION = "Invalid combination. Need to use at least one source."
NO_SUCH_FILE = "No such file: '{file}'"
VALID_PATH_OR_LIST_OF_PATHS = "'{path}' must be a valid path, or a list of valid paths."
VALID_PATH_LISTS = "'{path1}' and '{path2}' must be lists of valid paths."
VALID_CONFIG_ARG = (
    "'{config}' must be a valid file path, dict, config string or '{config_type}' object."
)
MODEL_NOT_FITTED = "The model has not been fitted."
VERTEX_ID_OR_COLLECTION_OF_IDS = "'{var}' must be a vertex ID or a collection of vertex IDs."
VERTEX_ID_OR_PGXVERTEX = "'{var}' must be a vertex ID or a PgxVertex."
EDGE_ID_OR_PGXEDGE = "'{var}' must be an edge ID or a PgxEdge."
PROPERTY_NOT_FOUND = "Property '{prop}' not found."
INDEX_OUT_OF_BOUNDS = "'{idx}' must be an integer: 0 <= '{idx}' <= {max_idx}"
VALID_INTERVAL = (
    "'start': {start} and 'stop': {stop} must define a valid interval within the range: "
    "[0, {max_idx}]"
)
COMPARE_VECTOR = "vector comparison is not supported."
INVALID_TYPE = "value must be of type {type}, received {value!r} (of type {received_type}) instead"
WRONG_SIZE_PROPERTY = "for vector property, expected an iterable with len {size}, got len {got}"
WRONG_NUMBER_OF_ARGS = "expected {expected} arguments but received {received}"
UNHASHABLE_TYPE = "Unhashable type: '{type_name}'"
UNSUPPORTED_QUERY_TYPE = "Unsupported query type, must be query or prepared query"
INVALID_FORMAT_PARTITIONED = (
    "Invalid format: '{var}'. For partitioned graphs, only the following formats are valid: {opts}"
)
INVALID_FORMAT_HOMOGENEOUS = (
    "Invalid format: '{var}'. For homogeneous graphs, only the following formats are valid: {opts}"
)
GRAPH_EXPAND_SOURCE_AMBIGUOUS = "Both a PG View and SQL Property Graph name have been specified. " \
                                "Please only specify either 'pg_view_name' or 'pg_sql_name'"
