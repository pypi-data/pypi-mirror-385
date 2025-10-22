#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils.error_messages import INVALID_COMBINATION
from pypgx._utils.error_handling import java_handler
from typing import Any, List
from jnius import autoclass

JavaEdgeCombinationMethods = autoclass(
    "oracle.pgx.config.mllib.edgecombination.EdgeCombinationMethods"
)


class EdgeCombinationMethod(object):
    """Abstract EdgeCombinationMethod class that represent edge combination methods"""

    _java_class = 'oracle.pgx.config.mllib.edgecombination.EdgeCombinationMethod'

    def __init__(self, java_arg_list: List[bool], method: Any) -> None:
        self._java_arg_list = java_arg_list
        if not any(self._java_arg_list):
            raise ValueError(INVALID_COMBINATION)
        self._java_obj = java_handler(method, self._java_arg_list)

    def use_src_vertex(self) -> bool:
        """Get if source vertex embedding is used or not for the edge embedding.

        :return: uses or not the source vertex
        """
        return java_handler(self._java_obj.isUseSourceVertex, [])

    def use_dst_vertex(self) -> bool:
        """Get if destination vertex embedding is used or not for the edge embedding.

        :return: uses or not the destination vertex
        """
        return java_handler(self._java_obj.isUseDestinationVertex, [])

    def use_edge(self) -> bool:
        """Get if edge features are used or not for the edge embedding

        :return: uses or not the edge features
        """
        return java_handler(self._java_obj.isUseEdge, [])

    def get_aggregation_type(self) -> str:
        """Get the aggregation type

        Returns:
            the aggregation type
        """
        return java_handler(self._java_obj.getAggregationType, []).name()


class ConcatEdgeCombinationMethod(EdgeCombinationMethod):
    """Concatenation method for edge embedding generation"""

    _java_class = 'oracle.pgx.config.mllib.edgecombination.ConcatEdgeCombinationMethod'

    def __init__(self,
                 use_source_vertex: bool,
                 use_destination_vertex: bool,
                 use_edge: bool) -> None:
        """
        :param use_source_vertex: whether to use the source vertex embedding to produce
        the edge embedding or not
        :param use_destination_vertex: whether to use the destination vertex embedding
        to produce the edge embedding or not
        :param use_edge: whether to use the edge features to produce the edge embedding
        or not
        """
        super().__init__(
            [use_source_vertex, use_destination_vertex, use_edge],
            JavaEdgeCombinationMethods.concatEdgeCombinationMethod,
        )

    def __repr__(self) -> str:
        return "%s" % (self.__class__.__name__)

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._java_arg_list[0] == other._java_arg_list[0] \
            and self._java_arg_list[1] == other._java_arg_list[1] \
            and self._java_arg_list[2] == other._java_arg_list[2]


class ProductEdgeCombinationMethod(EdgeCombinationMethod):
    """Product method for edge embedding generation"""

    _java_class = 'oracle.pgx.config.mllib.edgecombination.ProductEdgeCombinationMethod'

    def __init__(self,
                 use_source_vertex: bool,
                 use_destination_vertex: bool,
                 use_edge: bool) -> None:
        """
        :param use_source_vertex: whether to use the source vertex embedding to produce
        the edge embedding or not
        :param use_destination_vertex: whether to use the destination vertex embedding
        to produce the edge embedding or not
        :param use_edge: whether to use the edge features to produce the edge embedding
        or not
        """
        super().__init__(
            [use_source_vertex, use_destination_vertex, use_edge],
            JavaEdgeCombinationMethods.productEdgeCombinationMethod,
        )

    def __repr__(self) -> str:
        return "%s" % (self.__class__.__name__)

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._java_arg_list[0] == other._java_arg_list[0] \
            and self._java_arg_list[1] == other._java_arg_list[1] \
            and self._java_arg_list[2] == other._java_arg_list[2]
