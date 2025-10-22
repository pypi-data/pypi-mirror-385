#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#
from pypgx.api.frames._pgx_frame import PgxFrame
from pypgx._utils.error_messages import ARG_MUST_BE
from typing import Optional


class VertexFrameDeclaration:
    """A class containing the necessary information to create a vertex provider"""

    _java_class = 'oracle.pgx.api.frames.internal.VertexFrameDeclaration'

    def __init__(
        self,
        provider_name: str,
        frame: PgxFrame,
        vertex_key_column: str,
        label: Optional[str] = None,
    ) -> None:
        if not isinstance(provider_name, str):
            raise TypeError(ARG_MUST_BE.format(arg='provider_name', type=str))
        if not isinstance(frame, PgxFrame):
            raise TypeError(ARG_MUST_BE.format(arg='frame', type=PgxFrame))
        if not isinstance(vertex_key_column, str):
            raise TypeError(ARG_MUST_BE.format(arg='vertex_key_column', type=str))
        if label and not isinstance(label, str):
            raise TypeError(ARG_MUST_BE.format(arg='label', type=str))
        self.provider_name = provider_name
        self.frame = frame
        self.vertex_key_column = vertex_key_column
        self.label = label
