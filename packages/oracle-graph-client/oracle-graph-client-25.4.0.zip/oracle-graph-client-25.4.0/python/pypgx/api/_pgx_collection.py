#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

import collections.abc
from itertools import islice

from jnius import autoclass

from pypgx.api._pgx_entity import PgxEdge, PgxEntity, PgxVertex
from pypgx.api._pgx_context_manager import PgxContextManager
from pypgx._utils.error_handling import java_handler
from pypgx._utils.error_messages import UNHASHABLE_TYPE
from pypgx._utils import conversion
from pypgx.api._pgx_id import PgxId
from typing import Iterable, Iterator, List, Optional, Union, TYPE_CHECKING, NoReturn, Any

if TYPE_CHECKING:
    # Don't import at runtime, to avoid circular imports.
    from pypgx.api._pgx_graph import PgxGraph
    from pypgx.api._pgx_map import PgxMap


class PgxCollection(PgxContextManager):
    """Superclass for Pgx collections."""

    _java_class = 'oracle.pgx.api.PgxCollection'

    def __init__(self, java_collection) -> None:
        self._collection = java_collection
        self.graph: Optional["PgxGraph"] = None

    @property
    def name(self) -> str:
        """Get the name of this collection."""
        return self._collection.getName()

    @property
    def content_type(self) -> str:
        """Get the content type of this collection."""
        return self._collection.getContentType().toString()

    @property
    def collection_type(self) -> str:
        """Get the type of this collection."""
        return self._collection.getCollectionType().toString()

    @property
    def id_type(self) -> Optional[str]:
        """Get the id type of this collection."""
        id_type = self._collection.getIdType()
        if id_type:
            return id_type.toString()
        return None

    @property
    def is_mutable(self) -> bool:
        """Return True if this collection is mutable, False otherwise."""
        return self._collection.isMutable()

    def clear(self) -> None:
        """Clear an existing collection.

        :return: None
        """
        return java_handler(self._collection.clear, [])

    def clone(self, name: Optional[str] = None) -> "PgxCollection":
        """Clone and rename existing collection.

        :param name:  New name of the collection. If none, the old name is not changed.
        """
        cloned_coll = java_handler(self._collection.clone, [name])
        return self.__class__(cloned_coll)

    def to_mutable(self, name: Optional[str] = None) -> "PgxCollection":
        """Create a mutable copy of an existing collection.

        :param name: New name of the collection. If none, the old name is not changed.
        """
        mutable_coll = java_handler(self._collection.toMutable, [name])
        return self.__class__(mutable_coll)

    @property
    def size(self) -> int:
        """Get the number of elements in this collection."""
        return self._collection.size()

    def destroy(self) -> None:
        """Request destruction of this object.

        After this method returns, the behavior of any method of this class becomes undefined.

        :return: None
        """
        java_handler(self._collection.destroy, [])

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return "{}(name: {}, size: {})".format(self.__class__.__name__, self.name, self.size)

    def __str__(self) -> str:
        return repr(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._collection.equals(other._collection)

    def get_id(self) -> str:
        """Return the string representation of an internal identifier for this collection.
        Only meant for internal usage.

        :returns: a string representation of the internal identifier of this collection
        """
        java_pgx_id = java_handler(self._collection.getId, [])
        return java_handler(java_pgx_id.toString, [])

    def get_pgx_id(self) -> PgxId:
        """Return an internal identifier for this collection.
        Only meant for internal usage.

        :returns: the internal identifier of this collection
        """
        java_pgx_id = java_handler(self._collection.getId, [])
        return PgxId(java_pgx_id)

    def close(self) -> None:
        """Request destruction of this object. After this method returns, the behavior of any method
        of this class becomes undefined.
        """
        java_handler(self._collection.close, [])

    def add_all_elements(self, source: Iterable[Union[PgxEdge, PgxVertex]]) -> None:
        """Add elements to an existing collection.

        :param source: Elements to add
        """
        java_elements = autoclass('java.util.ArrayList')()
        for element in source:
            java_elements.add(conversion.property_to_java(element, self.content_type))
        java_handler(self._collection.addAllElements, [java_elements])

    def remove_all_elements(self, source: Iterable[Union[PgxEdge, PgxVertex]]) -> None:
        """Remove elements from an existing collection.

        :param source: Elements to remove
        """
        java_elements = autoclass('java.util.ArrayList')()
        for element in source:
            java_elements.add(conversion.property_to_java(element, self.content_type))
        java_handler(self._collection.removeAllElements, [java_elements])

    def contains(self, element):  # noqa: D102
        raise NotImplementedError

    def add_all(self, elements):  # noqa: D102
        raise NotImplementedError

    def remove(self, element):  # noqa: D102
        raise NotImplementedError

    def remove_all(self, elements):  # noqa: D102
        raise NotImplementedError


class GraphEntityCollection(PgxCollection):
    """A collection of vertices or edges."""

    # This class is intentionally not published for now, to reduce complexity of user facing API.

    def __init__(self, graph: "PgxGraph", java_collection) -> None:
        super().__init__(java_collection)
        self.graph: "PgxGraph" = graph

    def clone(self, name: Optional[str] = None) -> "PgxCollection":
        """Clone and rename existing collection.

        :param name: New name of the collection. If none, the old name is not changed.
        """
        cloned_coll = java_handler(self._collection.clone, [name])
        return self.__class__(self.graph, cloned_coll)

    def to_mutable(self, name: Optional[str] = None) -> "PgxCollection":
        """Create a mutable copy of an existing collection.

        :param name: New name of the collection. If none, the old name is not changed.
        """
        mutable_coll = java_handler(self._collection.toMutable, [name])
        return self.__class__(self.graph, mutable_coll)

    def __repr__(self) -> str:
        return "{}(name: {}, graph: {}, size: {})".format(
            self.__class__.__name__, self.name, self.graph.name, self.size
        )


class VertexCollection(GraphEntityCollection):
    """A collection of vertices."""

    _java_class = 'oracle.pgx.api.VertexCollection'

    def contains(self, v: Union[PgxVertex, int, str]) -> bool:
        """Check if the collection contains vertex v.

        :param v: PgxVertex object or id
        """
        if not isinstance(v, PgxVertex):
            if not self.graph.has_vertex(v):
                return False
            v = self.graph.get_vertex(v)
        return java_handler(self._collection.contains, [v._vertex])

    def add(self, v: Union[PgxVertex, int, str, Iterable[Union[PgxVertex, int, str]]]) -> None:
        """Add one or multiple vertices to the collection.

        :param v: Vertex or vertex id. Can also be an iterable of vertices/vertex ids
        """
        if isinstance(v, collections.abc.Iterable):
            return self.add_all(v)
        elif not isinstance(v, PgxVertex):
            v = self.graph.get_vertex(v)
        java_handler(self._collection.add, [v._vertex])

    def add_all(self, vertices: Iterable[Union[PgxVertex, int, str]]) -> None:
        """Add multiple vertices to the collection.

        :param vertices: Iterable of vertices/vertex ids
        """
        vids = _create_ids_array(vertices)
        java_handler(self._collection.addAllById, [vids])

    def remove(self, v: Union[PgxVertex, int, str, Iterable[Union[PgxVertex, int, str]]]) -> None:
        """Remove one or multiple vertices from the collection.

        :param v: Vertex or vertex id. Can also be an iterable of vertices/vertex ids.
        """
        if isinstance(v, collections.abc.Iterable):
            self.remove_all(v)
        else:
            if not isinstance(v, PgxVertex):
                v = self.graph.get_vertex(v)
            java_handler(self._collection.remove, [v._vertex])

    def remove_all(self, vertices: Iterable[Union[PgxVertex, int, str]]):
        """Remove multiple vertices from the collection.

        :param vertices: Iterable of vertices/vertex ids
        """
        vids = _create_ids_array(vertices)
        java_handler(self._collection.removeAllById, [vids])

    def __iter__(self) -> Iterator[PgxVertex]:
        it = self._collection.iterator()
        return (PgxVertex(self.graph, item) for item in islice(it, 0, self.size))

    def __getitem__(self, idx: Union[slice, int]) -> Union[List[PgxVertex], PgxVertex]:
        it = self._collection.iterator()
        if isinstance(idx, slice):
            return list(
                PgxVertex(self.graph, item) for item in islice(it, idx.start, idx.stop, idx.step)
            )
        else:
            return list(PgxVertex(self.graph, item) for item in islice(it, idx, idx + 1))[0]

    def __hash__(self) -> NoReturn:
        raise TypeError(UNHASHABLE_TYPE.format(type_name=self.__class__))


class EdgeCollection(GraphEntityCollection):
    """A collection of edges."""

    _java_class = 'oracle.pgx.api.EdgeCollection'

    def contains(self, e: Union[PgxEdge, int]) -> bool:
        """Check if the collection contains edge e.

        :param e: PgxEdge object or id:
        :returns: Boolean
        """
        if not isinstance(e, PgxEdge):
            if not self.graph.has_edge(e):
                return False
            e = self.graph.get_edge(e)
        return java_handler(self._collection.contains, [e._edge])

    def add(self, e: Union[PgxEdge, int, Iterable[Union[PgxEdge, int]]]):
        """Add one or multiple edges to the collection.

        :param e: Edge or edge id. Can also be an iterable of edge/edge ids.
        """
        if isinstance(e, collections.abc.Iterable):
            return self.add_all(e)
        elif not isinstance(e, PgxEdge):
            e = self.graph.get_edge(e)
        java_handler(self._collection.add, [e._edge])

    def add_all(self, edges: Iterable[Union[PgxEdge, int]]) -> None:
        """Add multiple vertices to the collection.

        :param edges: Iterable of edges/edges ids
        """
        eids = _create_ids_array(edges)
        java_handler(self._collection.addAllById, [eids])

    def remove(self, e: Union[PgxEdge, int, Iterable[Union[PgxEdge, int]]]):
        """Remove one or multiple edges from the collection.

        :param e: Edges or edges id. Can also be an iterable of edges/edges ids.
        """
        if isinstance(e, collections.abc.Iterable):
            return self.remove_all(e)
        elif not isinstance(e, PgxEdge):
            e = self.graph.get_edge(e)
        java_handler(self._collection.remove, [e._edge])

    def remove_all(self, edges: Iterable[Union[PgxEdge, int]]):
        """Remove multiple edges from the collection.

        :param edges: Iterable of edges/edges ids
        """
        eids = _create_ids_array(edges)
        java_handler(self._collection.removeAllById, [eids])

    def __iter__(self) -> Iterator[PgxEdge]:
        it = self._collection.iterator()
        return (PgxEdge(self.graph, item) for item in islice(it, 0, self.size))

    def __getitem__(self, idx: Union[slice, int]) -> Union[List[PgxEdge], PgxEdge]:
        it = self._collection.iterator()
        if isinstance(idx, slice):
            return list(
                PgxEdge(self.graph, item) for item in islice(it, idx.start, idx.stop, idx.step)
            )
        else:
            return list(PgxEdge(self.graph, item) for item in islice(it, idx, idx + 1))[0]

    def __hash__(self) -> NoReturn:
        raise TypeError(UNHASHABLE_TYPE.format(type_name=self.__class__))


class VertexSet(VertexCollection):
    """An unordered set of vertices (no duplicates)."""

    _java_class = 'oracle.pgx.api.VertexSet'

    def extract_top_k_from_map(self, pgx_map: "PgxMap", k: int) -> None:
        """Extract the top k keys from the given map and puts them into this collection.

        :param pgx_map: the map to extract the keys from
        :param k:   how many keys to extract
        """
        java_pgx_map = pgx_map._map
        java_handler(self._collection.extractTopKFromMap, [java_pgx_map, k])


class VertexSequence(VertexCollection):
    """An ordered sequence of vertices which may contain duplicates."""

    _java_class = 'oracle.pgx.api.VertexSequence'


class EdgeSet(EdgeCollection):
    """An unordered set of edges (no duplicates)."""

    _java_class = 'oracle.pgx.api.EdgeSet'


class EdgeSequence(EdgeCollection):
    """An ordered sequence of edges which may contain duplicates."""

    _java_class = 'oracle.pgx.api.EdgeSequence'


class ScalarCollection(PgxCollection):
    """A collection of scalars."""

    _java_class = 'oracle.pgx.api.ScalarCollection'

    def __iter__(self) -> Iterable[Any]:
        it = self._collection.iterator()
        return (conversion.property_to_python(item, self.content_type, None) for item in it)

    def add(self, items) -> None:
        """Add one or multiple elements to the collection.

        :param items: An element of the predefined type. Can also be an iterable of the same type.
        """
        if not isinstance(items, Iterable):
            items = [items]
        for item in items:
            java_value = conversion.property_to_java(item, self.content_type)
            java_handler(self._collection.add, [java_value])

    def remove(self, items) -> None:
        """Remove one or multiple elements from the collection.

        :param items: An element of the predefined type. Can also be an iterable of the same type.
        """
        if not isinstance(items, Iterable):
            items = [items]
        for item in items:
            java_value = conversion.property_to_java(item, self.content_type)
            java_handler(self._collection.remove, [java_value])

    def contains(self, element) -> bool:
        """Check whether the element is in the collection."""
        return bool(java_handler(self._collection.contains, [element]))

    def __hash__(self) -> NoReturn:
        raise TypeError(UNHASHABLE_TYPE.format(type_name=self.__class__))


class ScalarSequence(ScalarCollection):
    """An ordered sequence of scalars which may contain duplicates."""

    _java_class = 'oracle.pgx.api.ScalarSequence'

    def __getitem__(self, idx):
        it = self._collection.iterator()
        if isinstance(idx, slice):
            return list(
                conversion.property_to_python(item, self.content_type, None)
                for item in islice(it, idx.start, idx.stop, idx.step)
            )
        else:
            return list(
                conversion.property_to_python(item, self.content_type, None)
                for item in islice(it, idx, idx + 1)
            )[0]


class ScalarSet(ScalarCollection):
    """An unordered set of scalars that does not contain duplicates."""

    _java_class = 'oracle.pgx.api.ScalarSet'


def _create_ids_array(collection):
    return conversion.to_java_list(
        item.id if isinstance(item, PgxEntity) else item for item in collection
    )
