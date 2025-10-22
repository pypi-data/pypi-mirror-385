#
# Copyright (C) 2013 - 2025, Oracle and/or its affiliates. All rights reserved.
# ORACLE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
from datetime import date, time, datetime
from jnius import autoclass, JavaClass
from typing import Any, Optional

boolean = autoclass('java.lang.Boolean')
big_decimal = autoclass('java.math.BigDecimal')
local_date = autoclass('java.time.LocalDate')
local_time = autoclass('java.time.LocalTime')
timestamp = autoclass('java.time.LocalDateTime')
time_with_timezone = autoclass('java.time.OffsetTime')
timestamp_with_timezone = autoclass('java.time.OffsetDateTime')


def convert_to_python_type(value: Any) -> Any:
    if isinstance(value, boolean):
        return bool(value)
    elif isinstance(value, big_decimal):
        return big_decimal_to_python(value)
    elif isinstance(value, local_date):
        return local_date_to_python(value)
    elif isinstance(value, local_time):
        return local_time_to_python(value)
    elif isinstance(value, timestamp):
        return timestamp_to_python(value)
    elif isinstance(value, time_with_timezone):
        return time_with_timezone_to_python(value)
    elif isinstance(value, timestamp_with_timezone):
        return timestamp_with_timezone_to_python(value)
    else:
        return value


def big_decimal_to_python(value: Optional[JavaClass]) -> Optional[float]:
    """Convert Java BigDecimal to Python."""

    if value is None:
        return None

    return value.doubleValue()


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
