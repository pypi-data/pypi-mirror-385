#
# Copyright (C) 2013 - 2025, Oracle and/or its affiliates. All rights reserved.
# ORACLE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
"""Tools for handling exceptions that happen in Java."""

from jnius.jnius import JavaException
from typing import Any, Callable, Optional, Iterable


def java_handler(
    callable: Callable,
    arguments: Iterable[Any],
    expected_opg_exception: Optional[str] = None,
) -> Any:
    """Call `callable` with the given arguments.

    Raise a RuntimeError if something goes wrong on the Java side.
    If java exception matches expected_opg_exception, raise OpgError instead.

    :param callable: Java callable
    :param arguments: list of arguments for callable
    :param expected_opg_exception: string representing java exception class.
        E.g. "java.lang.UnsupportedOperationException"
    """

    try:
        return callable(*arguments)
    except JavaException as exc:
        classname = getattr(exc, "classname", None)
        message = getattr(exc, "innermessage", None)
        if not message:
            message = classname if classname else "Java exception"

        if expected_opg_exception is not None and expected_opg_exception == classname:
            raise OpgError(message) from None
        else:
            raise RuntimeError(message) from OriginalJavaException(exc)


class OpgError(Exception):
    """An error representing exceptions from OPG."""

    pass


class OriginalJavaException(Exception):
    """A Python exception representing a Java exception.

    Useful for displaying a Java stack trace before a Python stack trace. This class is NOT part of
    PyPGX, nor OPG4Py public API.
    """

    def __init__(self, wrapped_pyjnius_exc: JavaException) -> None:
        super().__init__(wrapped_pyjnius_exc)
        self._wrapped_pyjnius_exc = wrapped_pyjnius_exc

    def __str__(self) -> str:
        stacktrace = getattr(self._wrapped_pyjnius_exc, "stacktrace", None)
        if not stacktrace:
            return ""

        # The first line doesn't need any added prefix (unlike the other lines). An empty line is
        # added before the first "real" line to make the stacktrace look nicer when printed as part
        # of a Python error message.
        lines = ["", stacktrace[0]]
        caused_by = False
        for raw_line in stacktrace[1:]:
            if raw_line.startswith("Caused by"):
                # The next line needs to be treated specially.
                caused_by = True
                continue

            if caused_by:
                lines.append("Caused by: " + raw_line)
                caused_by = False
            else:
                # Java stack traces are typically shown with the word "at" starting each line.
                lines.append("    at " + raw_line)

        return "\n".join(lines)
