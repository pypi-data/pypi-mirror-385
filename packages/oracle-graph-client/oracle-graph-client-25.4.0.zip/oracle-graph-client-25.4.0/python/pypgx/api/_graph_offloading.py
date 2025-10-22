#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from datetime import date, time, datetime
from jnius import autoclass
from typing import Any, List, Optional

from pypgx._utils.error_handling import java_handler
from pypgx._utils import conversion

_QueryArgumentType_class = autoclass('oracle.pgx.common.types.QueryArgumentType')


class PreparedPgqlQueryArgument:
    """An argument for a prepared PGQL query.
    Please do not use this class directly, use any of its typed subclasses instead.
    """

    # the Python class 'PreparedPgqlQueryArgument' has no equivalent Java class.
    # to add arguments for a prepared PGQL statement to a Java-based builder
    # use _apply_prepared_query_arguments function.
    _java_class = None

    def __init__(self, type_name: str, value: Any) -> None:
        """
        Create a new query argument. Please do not use instances of this class.

        :param type_name: The name of the argument type.
        :param value: The actual query argument value.
        """
        self.type_name = type_name
        self.value = value


class PreparedPgqlQueryBooleanArgument(PreparedPgqlQueryArgument):
    """A boolean argument for a prepared PGQL query."""

    def __init__(self, value: bool) -> None:
        super().__init__("BOOLEAN", value)


class PreparedPgqlQueryDoubleArgument(PreparedPgqlQueryArgument):
    """A double argument for a prepared PGQL query."""

    def __init__(self, value: float) -> None:
        super().__init__("DOUBLE", value)


class PreparedPgqlQueryFloatArgument(PreparedPgqlQueryArgument):
    """A float argument for a prepared PGQL query."""

    def __init__(self, value: float) -> None:
        super().__init__("FLOAT", value)


class PreparedPgqlQueryIntegerArgument(PreparedPgqlQueryArgument):
    """An integer argument for a prepared PGQL query."""

    def __init__(self, value: int) -> None:
        super().__init__("INTEGER", value)


class PreparedPgqlQueryLongArgument(PreparedPgqlQueryArgument):
    """A long argument for a prepared PGQL query."""

    def __init__(self, value: int) -> None:
        super().__init__("LONG", value)


class PreparedPgqlQueryStringArgument(PreparedPgqlQueryArgument):
    """A string argument for a prepared PGQL query."""

    def __init__(self, value: str) -> None:
        super().__init__("STRING", value)


class PreparedPgqlQueryDateArgument(PreparedPgqlQueryArgument):
    """A date argument for a prepared PGQL query."""

    def __init__(self, value: date) -> None:
        super().__init__("LOCAL_DATE", value)


class PreparedPgqlQueryTimeArgument(PreparedPgqlQueryArgument):
    """A time argument for a prepared PGQL query."""

    def __init__(self, value: time) -> None:
        super().__init__("TIME", value)


class PreparedPgqlQueryTimeWithTimezoneArgument(PreparedPgqlQueryArgument):
    """A time (with timezone) argument for a prepared PGQL query."""

    def __init__(self, value: time) -> None:
        super().__init__("TIME_WITH_TIMEZONE", value)


class PreparedPgqlQueryTimestampArgument(PreparedPgqlQueryArgument):
    """A timestamp (date and time) argument for a prepared PGQL query."""

    def __init__(self, value: datetime) -> None:
        super().__init__("TIMESTAMP", value)


class PreparedPgqlQueryTimestampWithTimezoneArgument(PreparedPgqlQueryArgument):
    """A timestamp (date and time, with timezone) argument for a prepared PGQL query."""

    def __init__(self, value: datetime) -> None:
        super().__init__("TIMESTAMP_WITH_TIMEZONE", value)


class PreparedPgqlQuery:
    """
    Configuration for a prepared PGQL query, together with its arguments.
    This holds a string-representation for a prepared PGQL statement,
    together with all of its arguments.
    """

    # the Python class 'PreparedPgqlQuery' has no equivalent Java class.
    # to add arguments for a prepared PGQL statement to a Java-based builder
    # use _apply_prepared_query_arguments function.
    _java_class = None

    def __init__(
        self, query: str, arguments: Optional[List[PreparedPgqlQueryArgument]] = None
    ) -> None:
        """
        Create a new prepared PGQL query config.
        The query and all of its arguments must be supplied here.

        :param query: The string representation of the PGQL query.
        :param arguments: All arguments for the query, order by index.
        """
        self.query = query
        self.arguments = arguments


def _apply_prepared_query_arguments(
    query_builder: Any, arguments: Optional[List[PreparedPgqlQueryArgument]]
) -> None:
    """Add arguments for a prepared PGQL statement to a Java-based builder.

    :param query_builder: A builder for prepared statements, i.e.,
        an instance of 'oracle.pgx.api.subgraph.internal.PreparedQueryBuilder'.
    :type query_builder: Any
    :param arguments: Arguments for the prepared query, in order of position.
    :type arguments: Optional[List[PreparedPgqlQueryArgument]]
    """
    if arguments is None:
        return
    for i, arg in enumerate(arguments, 1):
        java_type = java_handler(_QueryArgumentType_class.valueOf, [arg.type_name])
        java_value = conversion.query_argument_to_java(arg.value, arg.type_name.lower())
        java_handler(query_builder.withArg, [i, java_type, java_value])
