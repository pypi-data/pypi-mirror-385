#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from typing import Any, Iterator, Optional, TYPE_CHECKING

from pypgx.api._pgx_context_manager import PgxContextManager
from pypgx._utils.error_handling import java_handler
from pypgx._utils import conversion

if TYPE_CHECKING:
    # Don't import at runtime, to avoid circular imports.
    from pypgx.api._pgx_graph import PgxGraph


class PgxMap(PgxContextManager):
    """A map is a collection of key-value pairs."""

    _java_class = 'oracle.pgx.api.PgxMap'

    def __init__(self, graph: Optional["PgxGraph"], java_map) -> None:
        self._map = java_map
        self.graph = graph

    @property
    def name(self) -> str:
        """Name of the map."""
        return self._map.getName()

    @property
    def key_type(self) -> str:
        """Type of the keys."""
        return self._map.getKeyType().toString()

    @property
    def value_type(self) -> str:
        """Type of the values."""
        return self._map.getValueType().toString()

    @property
    def session_id(self) -> int:
        """Session id."""
        return java_handler(self._map.getSessionId, [])

    @property
    def size(self) -> int:
        """Map size."""
        return self._map.size()

    def put(self, key, value) -> None:
        """Set the value for a key in the map specified by the given name.

        :param key: Key of the entry
        :param value: New value
        """
        java_key = conversion.entity_or_property_to_java(key, self.key_type, self.graph)
        java_value = conversion.entity_or_property_to_java(value, self.value_type, self.graph)
        java_handler(self._map.put, [java_key, java_value])

    def remove(self, key) -> bool:
        """Remove the entry specified by the given key from the map with the given name.

        Returns true if the map did contain an entry with the given key, false otherwise.

        :param key: Key of the entry
        :returns: True if the map contained the key
        """
        java_key = conversion.entity_or_property_to_java(key, self.key_type, self.graph)
        return bool(java_handler(self._map.remove, [java_key]))

    def get(self, key) -> Any:
        """Get the entry with the specified key.

        :param key: Key of the entry
        :returns: Value
        """
        java_key = conversion.entity_or_property_to_java(key, self.key_type, self.graph)
        value = java_handler(self._map.get, [java_key])

        return conversion.property_to_python(value, self.value_type, self.graph)

    def contains_key(self, key) -> bool:
        """Return True if this map contains the given key.

        :param key: Key of the entry
        """
        java_key = conversion.entity_or_property_to_java(key, self.key_type, self.graph)
        return bool(java_handler(self._map.containsKey, [java_key]))

    def keys(self) -> list:
        """Return a key set."""
        return list(self)

    def entries(self) -> dict:
        """Return an entry set."""
        map_dict = {}
        for key in self:
            map_dict[key] = self.get(key)
        return map_dict

    def destroy(self) -> None:
        """Destroy this map."""
        java_handler(self._map.destroy, [])

    def __iter__(self) -> Iterator[Any]:
        it = self._map.keys().iterator()
        return (conversion.property_to_python(item, self.key_type, self.graph) for item in it)

    def __getitem__(self, key) -> Any:
        return self.get(key)

    def __setitem__(self, key, value) -> None:
        self.put(key, value)

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return "{}(name: {}, {}: {}, key_type: {}, value_type: {}, size: {})".format(
            self.__class__.__name__,
            self.name,
            'session' if self.graph is None else 'graph',
            self.session_id if self.graph is None else self.graph.name,
            self.key_type,
            self.value_type,
            self.size,
        )

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> int:
        if self.graph is None:
            return hash((str(self), str(self.session_id)))
        else:
            return hash((str(self), str(self.graph.name)))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return bool(self._map.equals(other._map))
