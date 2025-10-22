#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#
from jnius import autoclass

from pypgx._utils.error_handling import java_handler
from pypgx._utils.error_messages import ARG_MUST_BE
from pypgx._utils.conversion import anything_to_java
from pypgx.api.frames._pgx_frame import PgxFrame
from pypgx.api._pgx_context_manager import PgxContextManager
from typing import Dict, Any


class PgxFrameBuilder(PgxContextManager):
    """A frame builder for constructing a :class:`PgxFrame`."""

    _java_class = 'oracle.pgx.api.frames.PgxFrameBuilder'

    def __init__(self, java_pgx_frame_builder) -> None:
        self._frame_builder = java_pgx_frame_builder

    def add_rows(self, column_data: Dict[str, Any]) -> "PgxFrameBuilder":
        """Add the data to the frame builder.

        :param column_data: The column data in a dictionary.
        :type column_data: Dict[str, Any]

        :raises TypeError: `column_data` must be a dictionary.

        :returns: The current pgx frame reader.
        :rtype: PgxFrameBuilder
        """
        if not isinstance(column_data, dict):
            raise TypeError(ARG_MUST_BE.format(arg='column_data', type=dict))
        java_data = autoclass('java.util.HashMap')()
        for column_name in column_data:
            python_list = column_data[column_name]
            java_list = autoclass('java.util.ArrayList')()
            for x in python_list:
                java_list.add(anything_to_java(x))
            java_data.put(column_name, java_list)
        java_handler(self._frame_builder.addRows, [java_data])
        return self

    def build(self, frame_name: str) -> PgxFrame:
        """Build the frame with the given frame name.

        :param frame_name: The name of the frame to create.
        :type frame_name: str

        :raises TypeError: `frame_name` must be a string.

        :returns: The newly frame created.
        :rtype: PgxFrame
        """
        if not isinstance(frame_name, str):
            raise TypeError(ARG_MUST_BE.format(arg='frame_name', type=str))
        java_pgx_frame = java_handler(self._frame_builder.build, [frame_name])
        return PgxFrame(java_pgx_frame)

    def close(self) -> None:
        """Free resources on the server taken up by this frame builder.
        After this method returns, the behaviour of any methods of this class becomes undefined.
        """
        java_handler(self._frame_builder.close, [])

    def destroy(self) -> None:
        """Free resources on the server taken up by this frame builder.
        After this method returns, the behaviour of any methods of this class becomes undefined.
        """
        java_handler(self._frame_builder.destroy, [])
