#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#
from typing import Optional
from pypgx._utils.error_handling import java_handler
from pypgx._utils.pgx_types import col_types, id_types


class PgqlResultElement:
    """Type and variable name information on a pattern matching result element"""

    _java_class = "oracle.pgx.api.PgqlResultElement"

    def __init__(
        self,
        java_pgql_result_elem,
    ) -> None:
        self._pgql_result_elem = java_pgql_result_elem

    @property
    def element_type(self) -> Optional[str]:
        """Get the type of this result element

        :returns: result element type
        """
        elem_type = java_handler(self._pgql_result_elem.getElementType, [])
        elem_type = java_handler(elem_type.toString, [])
        return elem_type if elem_type in col_types else None

    @property
    def collection_element_type(self) -> Optional[str]:
        """Get the type of the elements stored in the collection
        if the result element is a collection

        :returns: type of the elements stored in the collection
        """
        collection_elem_type = java_handler(self._pgql_result_elem.getCollectionElementType, [])
        if collection_elem_type is not None:
            collection_elem_type = java_handler(collection_elem_type.toString, [])
        return collection_elem_type if collection_elem_type in col_types else None

    @property
    def variable_name(self) -> str:
        """Get the variable name of the result element

        :returns: the variable name
        """
        return java_handler(self._pgql_result_elem.getVarName, [])

    @property
    def vertex_edge_id_type(self) -> Optional[str]:
        """Get the type of vertex/edge result elements

        :returns: type of vertex/edge result elements or None if not vertex/edge.
        """
        vertex_edge_id_type = java_handler(self._pgql_result_elem.getVertexEdgeIdType, [])
        if vertex_edge_id_type is not None:
            vertex_edge_id_type = java_handler(vertex_edge_id_type.toString, [])
        return vertex_edge_id_type if vertex_edge_id_type in id_types else None

    def __repr__(self):
        return '{} (variable_name: {}, element_type: {}, vertex_edge_id_type: {})'.format(
            self.__class__.__name__,
            self.variable_name,
            self.element_type,
            self.vertex_edge_id_type,
        )

    def __str__(self):
        return repr(self)
