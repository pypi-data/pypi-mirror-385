#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils.error_handling import java_handler
from pypgx._utils.pgx_types import id_types, key_column_descriptor
from pypgx._utils import conversion

from typing import Optional


class KeyColumnDescriptor:
    """Describes a key column of an entity provider"""

    _java_class = "oracle.pgx.api.keys.KeyColumnDescriptor"

    def __init__(self, java_key_column_desc=None,
                 col_name: Optional[str] = None,
                 col_type: Optional[str] = None) -> None:
        """Initialize this KeyColumn object.

        This function accepts either a Java KeyColumnDescriptor object or
        a column name and type. If the Java object is provided, the other parameters
        must be None. If the Java object is None, the other parameters must be set.

        :param java_key_column_desc: A java object of type 'KeyColumnDescriptor'
        :param col_name: The key column name
        :param col_type: The key column type
        :raises TypeError: If missing or too many arguments were provided
        """
        key_col_tmp = None
        if java_key_column_desc is not None and col_name is None and col_type is None:
            # Use asKeyColumnDescriptor to create a copy first, to ensure that the backing
            # object is not a config or an enum value (DefaultKeyColumnDescriptors).
            key_col_tmp = java_handler(java_key_column_desc.asKeyColumnDescriptor, [])
        elif java_key_column_desc is None and col_name is not None and col_type is not None:
            java_id_type = id_types[col_type]
            key_col_tmp = java_handler(key_column_descriptor.of, [col_name, java_id_type])
        # We should have a column desc. now, otherwise an invalid combination of args
        # was provided
        if key_col_tmp is None:
            raise TypeError(
                "You must specify either a Java 'KeyColumnDescriptor' object or a "
                "'col_name' and an 'col_type'"
            )
        self._key_column = key_col_tmp

    def get_name(self) -> str:
        """Get the name of this key column.

        :return: The key column name.
        """
        return java_handler(self._key_column.getName, [])

    def get_type(self) -> str:
        """Get the type of this key column.

        :return: The key column type.
        """
        java_id_type = java_handler(self._key_column.getType, [])
        return conversion.enum_to_python_str(java_id_type)

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return java_handler(self._key_column.equals, [other._key_column])

    def __str__(self) -> str:
        return java_handler(self._key_column.toString, [])

    def __hash__(self) -> int:
        return java_handler(self._key_column.hashCode, [])
