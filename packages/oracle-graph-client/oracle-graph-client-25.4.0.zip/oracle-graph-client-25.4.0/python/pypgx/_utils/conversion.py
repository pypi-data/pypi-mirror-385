#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from datetime import date, time, datetime
from typing import Any, Optional, TYPE_CHECKING, Union, Iterable, Tuple, Dict, Mapping

from pypgx._utils.error_handling import java_handler
from pypgx._utils import pgx_types
from pypgx._utils.pyjnius_helper import PyjniusHelper, PyjniusBooleanEnum
from pypgx.api._pgx_entity import PgxEntity, PgxVertex, PgxEdge
from pypgx._utils.error_messages import (
    ARG_MUST_BE, VERTEX_ID_OR_PGXVERTEX, EDGE_ID_OR_PGXEDGE, INVALID_TYPE,
    INVALID_OPTION,
)

from jnius.jnius import JavaClass

if TYPE_CHECKING:
    # Don't import at runtime, to avoid circular imports.
    from pypgx.api._pgx_graph import PgxGraph


QUERY_ARGUMENT_TYPES = {
    "integer",
    "long",
    "float",
    "double",
    "boolean",
    "string",
    "time",
    "local_date",
    "timestamp",
    "time_with_timezone",
    "timestamp_with_timezone",
}


##############################
# Python to Java conversions #
##############################

def property_to_java(value: Any, type_name: str) -> JavaClass:
    """Convert a Python value to a Java value.

    `type_name` is a string that stands for an option in oracle.pgx.common.types.PropertyType.
    We need the `type_name` argument to distinguish 'float' from 'double', as well as 'integer' from
    'long'.

    See also entity_or_property_to_java().
    """

    if type_name == "integer":
        if not isinstance(value, int):
            raise _invalid_type_exception(value, int)
        return pgx_types.Integer(value)

    if type_name == "long":
        if not isinstance(value, int):
            raise _invalid_type_exception(value, int)
        return pgx_types.Long(value)

    if type_name == "float":
        if not isinstance(value, float):
            raise _invalid_type_exception(value, float)
        return pgx_types.Float(value)

    if type_name == "double":
        if not isinstance(value, float):
            raise _invalid_type_exception(value, float)
        return pgx_types.Double(value)

    if type_name == "boolean":
        if not isinstance(value, bool):
            raise _invalid_type_exception(value, bool)
        return pgx_types.Boolean(value)

    if type_name == "string":
        if not isinstance(value, str):
            raise _invalid_type_exception(value, str)
        return pgx_types.String(value)

    if type_name == "time":
        if not isinstance(value, time):
            raise _invalid_type_exception(value, time)
        return to_java_local_time(value)

    if type_name == "local_date":
        if not isinstance(value, date):
            raise _invalid_type_exception(value, date)
        return to_java_local_date(value)

    if type_name == "timestamp":
        if not isinstance(value, datetime):
            raise _invalid_type_exception(value, datetime)
        return to_java_timestamp(value)

    if type_name == "time_with_timezone":
        if not isinstance(value, time):
            raise _invalid_type_exception(value, time)
        return to_java_time_with_timezone(value)

    if type_name == "timestamp_with_timezone":
        if not isinstance(value, datetime):
            raise _invalid_type_exception(value, datetime)
        return to_java_timestamp_with_timezone(value)

    if type_name == "vertex":
        if not isinstance(value, PgxVertex):
            raise _invalid_type_exception(value, PgxVertex)
        return value._vertex

    if type_name == "edge":
        if not isinstance(value, PgxEdge):
            raise _invalid_type_exception(value, PgxEdge)
        return value._edge

    if type_name == "point2d":
        if not isinstance(value, tuple):
            raise _invalid_type_exception(value, tuple)
        x, y = value
        return pgx_types.Point2D(x, y)

    raise ValueError(f"Invalid property type {type_name!r}")


def _invalid_type_exception(value: object, python_type: type) -> Exception:
    """Return an exception to tell the user that their type is invalid."""
    msg = INVALID_TYPE.format(
        type=python_type.__name__, value=value, received_type=type(value).__name__
    )
    return TypeError(msg)


def entity_or_property_to_java(
    value: Union[
        int, str, float, bool, time, date, datetime, PgxVertex, PgxEdge, Tuple[float, float]
    ],
    type_name: str,
    graph: Optional["PgxGraph"],
) -> JavaClass:
    """Like property_to_java(), but converts int/str to PgxVertex/PgxEdge if needed."""

    if isinstance(value, (int, str)) and type_name == 'vertex':
        if graph is None:
            raise ValueError("Graph must be set if the type is 'vertex'")
        return java_handler(graph._graph.getVertex, [value])
    if isinstance(value, (int, str)) and type_name == 'edge':
        if graph is None:
            raise ValueError("Graph must be set if the type is 'edge'")
        return java_handler(graph._graph.getEdge, [value])
    return property_to_java(value, type_name)


def query_argument_to_java(
    value: Union[int, str, float, bool, time, date, datetime],
    type_name: str,
):
    """Convert a Python value to a Java value.

    `type_name` is a string that stands for an option in oracle.pgx.common.types.QueryArgumentType.
    We need the `type_name` argument to distinguish 'float' from 'double', as well as 'integer' from
    'long'.
    """

    if type_name not in QUERY_ARGUMENT_TYPES:
        raise ValueError(INVALID_OPTION.format(var=type_name, opts=sorted(QUERY_ARGUMENT_TYPES)))

    # oracle.pgx.common.types.QueryArgumentType is a subset of oracle.pgx.common.types.PropertyType.
    # So we can do this safely.
    return property_to_java(value, type_name)


def vertex_id_to_java(value: Union[int, str], type_name: str):
    """Convert a Python vertex ID to a Java object.

    Provided mainly for cases where we need to be lenient with types for backwards compatibility.
    """

    if type_name == "integer":
        # `value` can be a string for 'integer' and 'long' cases.
        return pgx_types.Integer(value)
    if type_name == "long":
        return pgx_types.Long(value)
    if type_name == "string":
        return pgx_types.String(value)

    return property_to_java(value, type_name)  # Fallback, should never happen.


def anything_to_java(value: Any) -> Any:
    """Convert a Python object to an equivalent Java object.

    CAUTION: Using this function carelessly can lead to bugs around Integer vs Long and
    Float vs Double. If the needed type is known at runtime, use property_to_java() instead. If the
    needed type is known statically, use a specific conversion for the type. For example:
        * v._vertex for vertices
        * Long(x) for long
        * to_java_local_date(x) for local date

    The typical use case for this function is converting a Python object whose type is not known
    until runtime.
    """

    if isinstance(value, bool):
        # bool before int because bool is a subtype of int.
        return pgx_types.Boolean(value)

    if isinstance(value, int):
        # Use the widest possible type to avoid inconsistencies. (GM-30135)
        return pgx_types.Long(value)

    if isinstance(value, float):
        return pgx_types.Double(value)

    if isinstance(value, PgxEntity):
        return value._entity

    if isinstance(value, datetime):
        # datetime before date because datetime is a subtype of date.
        if value.tzinfo:
            return to_java_timestamp_with_timezone(value)
        return to_java_timestamp(value)

    if isinstance(value, date):
        return to_java_local_date(value)

    if isinstance(value, time):
        if value.tzinfo:
            return to_java_time_with_timezone(value)
        return to_java_local_time(value)

    # Stings are converted automatically once we pass them to pyjnius.
    return value


def to_java_local_date(value: date) -> JavaClass:
    """Convert Python date to Java."""
    return pgx_types.local_date.parse(pgx_types.String(value.isoformat()))


def to_java_local_time(value: time) -> JavaClass:
    """Convert Python time to Java."""
    return pgx_types.local_time.parse(pgx_types.String(value.isoformat()))


def to_java_time_with_timezone(value: time) -> JavaClass:
    """Convert Python time with timezone to Java."""
    return pgx_types.time_with_timezone.parse(pgx_types.String(value.isoformat()))


def to_java_timestamp(value: datetime) -> JavaClass:
    """Convert Python datetime to Java."""
    return pgx_types.timestamp.parse(pgx_types.String(value.isoformat()))


def to_java_timestamp_with_timezone(value: datetime) -> JavaClass:
    """Convert Python datetime with timezone to Java."""
    return pgx_types.timestamp_with_timezone.parse(pgx_types.String(value.isoformat()))


def to_java_list(iterable: Iterable) -> JavaClass:
    """Return a Java ArrayList.

    The elements usually need to be converted Java beforehand.
    """

    java_list = pgx_types.array_list()
    for item in iterable:
        java_list.add(item)
    return java_list


def to_java_set(iterable: Iterable) -> JavaClass:
    """Return a Java HashSet.

    The elements usually need to be converted Java beforehand.
    """

    java_set = pgx_types.HashSet()
    for item in iterable:
        java_set.add(item)
    return java_set


def to_java_map(mapping: Mapping) -> JavaClass:
    """Return a Java HashMap.

    The keys and values usually need to be converted Java beforehand.
    """

    java_map = pgx_types.HashMap()
    for key, value in mapping.items():
        java_map.put(key, value)
    return java_map


def to_java_vertex(graph: "PgxGraph", vertex: Union["PgxVertex", int, str]) -> JavaClass:
    """Return a Java vertex."""

    if isinstance(vertex, PgxVertex):
        return vertex._vertex
    if isinstance(vertex, (int, str)):
        java_vertex_id = vertex_id_to_java(vertex, graph.vertex_id_type)
        return java_handler(graph._graph.getVertex, [java_vertex_id])

    raise TypeError(VERTEX_ID_OR_PGXVERTEX.format(var='vertices'))


def to_java_edge(graph: "PgxGraph", edge: Union["PgxEdge", int, str]) -> JavaClass:
    """Return a Java edge."""

    if isinstance(edge, PgxEdge):
        return edge._edge
    if isinstance(edge, (int, str)):
        return java_handler(graph._graph.getEdge, [edge])

    raise TypeError(EDGE_ID_OR_PGXEDGE.format(var='edges'))


##############################
# Java to Python conversions #
##############################

def property_to_python(value: Any, type_name: str, graph: Optional["PgxGraph"]) -> Any:
    """Convert a Java (or Python) value to a Python value.

    `value` is typically a Java object, but could be a Python object if Pyjnius already converted
    it automatically (e.g. Java String -> Python str).

    `type_name` is a string that stands for an option in oracle.pgx.common.types.PropertyType.
    We need the `type_name` argument to distinguish 'integer' from 'boolean'. Pyjnius wrongly
    converts Java Boolean to Python int (as of pyjnius 1.4.0).
    """
    # This is a workaround for https://github.com/kivy/pyjnius/issues/602, see also GM-28290.

    # Boolean is not a valid vector property type, so we can ignore the "boolean vector property"
    # case.
    if type_name == 'boolean' and value in (0, 1):
        return bool(value)
    return anything_to_python(value, graph)


def anything_to_python(value: Any, graph: Optional["PgxGraph"] = None) -> Any:
    """Convert a Java value to a Python value.

    IMPORTANT NOTE: Using anything_to_python() MAY LEAD TO BUGS:
    As of pyjnius 1.4.0, Booleans are sometimes converted to Python int instead of bool. If we have
    the type available (as an oracle.pgx.common.types.PropertyType instance), we should use
    property_to_python(), NOT anything_to_python().

    The typical use case for this function is converting a Java object whose type is not known
    until runtime. For example, an element from a PGQL result set.
    """

    from pypgx.api._pgx_graph import PgxGraph

    if isinstance(value, (pgx_types.pgx_entities['vertex'], pgx_types.pgx_entities['edge'])):
        if graph is None:
            raise ValueError("Graph must be set if the item type is PgxVertex/PgxEdge")
        if not isinstance(graph, PgxGraph):
            raise TypeError(ARG_MUST_BE.format(arg='graph', type=PgxGraph))
        return entity_to_python(value, graph)
    if isinstance(value, pgx_types.local_date):
        return local_date_to_python(value)
    if isinstance(value, pgx_types.local_time):
        return local_time_to_python(value)
    if isinstance(value, pgx_types.timestamp):
        return timestamp_to_python(value)
    if isinstance(value, pgx_types.time_with_timezone):
        return time_with_timezone_to_python(value)
    if isinstance(value, pgx_types.timestamp_with_timezone):
        return timestamp_with_timezone_to_python(value)
    if isinstance(value, pgx_types.legacy_date):
        return legacy_date_to_python(value)
    if isinstance(value, pgx_types.Point2D):
        return point2d_to_python(value)
    if isinstance(value, pgx_types.Enum):
        return enum_to_python_str(value)
    if isinstance(value, pgx_types.graph_property_config):
        from pypgx.api import GraphPropertyConfig
        return GraphPropertyConfig._from_java_config(value)
    if isinstance(value, pgx_types.graph_config):
        return graph_config_to_python(value)
    if isinstance(value, pgx_types.abstract_config):
        return config_to_python_dict(value)
    if isinstance(value, pgx_types.java_set):
        return set_to_python(value)
    if isinstance(value, pgx_types.java_collection):
        # Set before collection because each Set is a collection.
        return collection_to_python_list(value)
    if isinstance(value, pgx_types.java_map):
        return map_to_python(value)
    if isinstance(value, pgx_types.pgx_vect):
        # Returns a list.
        return value.toArray()
    return value


def entity_to_python(java_entity: JavaClass, graph: "PgxGraph") -> PgxEntity:
    """Convert a Java vertex or edge to Python."""

    if isinstance(java_entity, pgx_types.pgx_entities['vertex']):
        return PgxVertex(graph, java_entity)
    elif isinstance(java_entity, pgx_types.pgx_entities['edge']):
        return PgxEdge(graph, java_entity)
    else:
        raise TypeError(ARG_MUST_BE.format(arg='item', type='vertex or edge'))


def optional_boolean_to_python(value: Optional[int]) -> Optional[bool]:
    """Fix pyjnius conversion by converting to bool."""

    # Pyjnius wrongly converts Java Boolean to Python int (as of pyjnius 1.4.0). We need to convert
    # it back to bool.
    if value is None:
        return None
    return bool(value)


def local_date_to_python(value: Optional[JavaClass]) -> Optional[date]:
    """Convert Java LocalDate to Python."""

    if value is None:
        return None
    return datetime.strptime(value.toString(), '%Y-%m-%d').date()


def local_time_to_python(value: Optional[JavaClass]) -> Optional[time]:
    """Convert Java LocalTime to Python."""

    if value is None:
        return None

    value_str = value.toString()
    # Format may or may not have milliseconds in the string. Test for both.
    try:
        return datetime.strptime(value_str, '%H:%M:%S.%f').time()
    except ValueError:
        pass
    try:
        return datetime.strptime(value_str, '%H:%M:%S').time()
    except ValueError:
        pass
    try:
        return datetime.strptime(value_str, '%H:%M').time()
    except ValueError:
        pass
    try:
        return datetime.strptime(value_str, '%H').time()
    except ValueError:
        pass
    raise ValueError(value_str + " cannot be parsed into time")


def time_with_timezone_to_python(value: Optional[JavaClass]) -> Optional[time]:
    """Convert Java TimeWithTimezone to Python."""

    if value is None:
        return None

    # Adjust timezone to be readable by .strptime()
    value_str = value.toString()
    if value_str[-1] == 'Z':
        value_str = value_str[:-1] + '+0000'
    else:
        value_str = value_str[:-3] + value_str[-2:]
    # Format may or may not have milliseconds in the string. Test for both.
    try:
        return datetime.strptime(value_str, '%H:%M:%S.%f%z').timetz()
    except ValueError:
        pass
    try:
        return datetime.strptime(value_str, '%H:%M:%S%z').timetz()
    except ValueError:
        pass
    try:
        return datetime.strptime(value_str, '%H:%M%z').timetz()
    except ValueError:
        pass
    try:
        return datetime.strptime(value_str, '%H%z').timetz()
    except ValueError:
        pass
    raise ValueError(value_str + " cannot be parsed into time")


def timestamp_to_python(value: Optional[JavaClass]) -> Optional[datetime]:
    """Convert Java timestamp to Python."""

    if value is None:
        return None

    value_str = value.toString()
    # Format may or may not have milliseconds in the string. Test for both.
    try:
        return datetime.strptime(value_str, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        pass
    try:
        return datetime.strptime(value_str, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        pass
    try:
        return datetime.strptime(value_str, '%Y-%m-%dT%H:%M')
    except ValueError:
        pass
    try:
        return datetime.strptime(value_str, '%Y-%m-%dT%H')
    except ValueError:
        pass
    raise ValueError(value_str + " cannot be parsed into datetime")


def timestamp_with_timezone_to_python(value: Optional[JavaClass]) -> Optional[datetime]:
    """Convert Java timestamp with timezone to Python."""

    if value is None:
        return None

    # Adjust timezone to be readable by .strptime()
    value_str = value.toString()
    if value_str[-1] == 'Z':
        value_str = value_str[:-1] + '+0000'
    else:
        value_str = value_str[:-3] + value_str[-2:]
    # Format may or may not have milliseconds in the string. Test for both.
    try:
        return datetime.strptime(value_str, '%Y-%m-%dT%H:%M:%S.%f%z')
    except ValueError:
        pass
    try:
        return datetime.strptime(value_str, '%Y-%m-%dT%H:%M:%S%z')
    except ValueError:
        pass
    try:
        return datetime.strptime(value_str, '%Y-%m-%dT%H:%M%z')
    except ValueError:
        pass
    try:
        return datetime.strptime(value_str, '%Y-%m-%dT%H%z')
    except ValueError:
        pass
    raise ValueError(value_str + " cannot be parsed into datetime")


def legacy_date_to_python(value: Optional[JavaClass]) -> Optional[datetime]:
    """Convert Java Date to Python."""

    if value is None:
        return None
    return datetime.strptime(value.toString(), '%a %b %d %H:%M:%S %Z %Y')


def point2d_to_python(value: Optional[JavaClass]) -> Optional[Tuple[float, float]]:
    """Convert Java Point2D to Python tuple."""

    if value is None:
        return None
    return value.getX(), value.getY()


def collection_to_python_list(value: Optional[JavaClass]) -> Any:
    """Convert Java List to Python."""

    if value is None:
        return None

    item_iter = java_handler(value.iterator, [])
    item_list = []
    # get all values from iterator and convert
    while java_handler(item_iter.hasNext, []):
        item_list.append(call_and_convert_to_python(item_iter, 'next'))
    return item_list


def set_to_python(value: Optional[JavaClass]) -> Any:
    """Convert Java Set to Python."""

    if value is None:
        return None

    item_iter = java_handler(value.iterator, [])
    item_set = set()
    # get all values from iterator and convert
    while java_handler(item_iter.hasNext, []):
        item_set.add(call_and_convert_to_python(item_iter, 'next'))
    return item_set


def map_to_python(value: Optional[JavaClass]) -> Any:
    """Convert Java Map to Python."""

    if value is None:
        return None
    return {
        call_and_convert_to_python(e, 'getKey'): call_and_convert_to_python(e, 'getValue')
        for e in java_handler(value.entrySet, [])
    }


def config_to_python_dict(value: JavaClass) -> Dict[Any, Any]:
    """Convert a Java config to a Python dict."""
    python_dict = map_to_python(value.getValues())
    return dict(sorted(python_dict.items()))


def enum_to_python_str(enum: pgx_types.Enum) -> str:
    """Return the Java Enum field as a lower case string."""
    if isinstance(enum, pgx_types.Enum):
        return enum.name().lower()
    raise TypeError('Argument must be an Enum')


def call_and_convert_to_python(obj: Any, method_name: str) -> Any:
    """Invoke object method and convert it to python type

    Meant to handle cases with methods which return Booleans and Character types
    which pyjnius handles poorly.
    Can only be called on methods which take no argument
    """
    ret_val = java_handler(PyjniusHelper.reflectInvokeMethod, [obj, method_name])
    if isinstance(ret_val, PyjniusBooleanEnum):
        ret_val = True if ret_val.ordinal() else False
    return anything_to_python(ret_val)


def graph_config_to_python(java_config) -> Any:
    """Return the graph config class associated to the given java config class."""
    if isinstance(java_config, pgx_types.file_graph_config):
        from pypgx.api._file_graph_config import FileGraphConfig
        return FileGraphConfig(java_config)
    if isinstance(java_config, pgx_types.two_tables_text_graph_config):
        from pypgx.api._file_graph_config import TwoTablesTextGraphConfig
        return TwoTablesTextGraphConfig(java_config)
    if isinstance(java_config, pgx_types.partitioned_graph_config):
        from pypgx.api._partitioned_graph_config import PartitionedGraphConfig
        return PartitionedGraphConfig(java_config)
    if isinstance(java_config, pgx_types.rdf_graph_config):
        from pypgx.api._rdf_graph_config import RdfGraphConfig
        return RdfGraphConfig(java_config)
    if isinstance(java_config, pgx_types.two_tables_rdbms_graph_config):
        from pypgx.api._two_tables_rdbms_graph_config import TwoTablesRdbmsGraphConfig
        return TwoTablesRdbmsGraphConfig(java_config)
    else:
        from pypgx.api._graph_config import GraphConfig
        if isinstance(java_config, pgx_types.graph_config):
            return GraphConfig(java_config)
        else:
            raise _invalid_type_exception(java_config, pgx_types.graph_config)
