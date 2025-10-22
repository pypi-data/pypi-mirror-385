#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils.error_handling import java_handler
from jnius import autoclass
from pypgx.api._pgx_id import PgxId
from pypgx._utils.error_messages import (
    INVALID_OPTION,
    UNHASHABLE_TYPE
)
from pypgx._utils.conversion import enum_to_python_str
from pypgx._utils.pgx_types import (
    property_types
)
from typing import NoReturn

_JavaPropertyMetaData = autoclass('oracle.pgx.api.PropertyMetaData')


class PropertyMetaData:
    """Meta information about a property."""

    _java_class = 'oracle.pgx.api.PropertyMetaData'

    def __init__(
            self,
            name: str,
            pgx_id: PgxId,
            property_type: str,
            dimension: int,
            transient: bool,
    ) -> None:
        """Initialize this PropertyMetaData object.

        :param name: name of the property
        :param pgx_id: id of the property
        :param property_type: type of the property
        :param dimension: dimension of the property
        :param transient: whether the property is transient or not
        """
        if property_type in property_types:
            java_property_type = property_types[property_type]
        else:
            raise ValueError(
                INVALID_OPTION.format(var='property_type', opts=[*property_types])
            )
        java_property_meta_data = java_handler(
            _JavaPropertyMetaData, [name, pgx_id._id, java_property_type,
                                    dimension, transient]
        )
        self._property_meta_data = java_property_meta_data

    @classmethod
    def _internal_init(cls, java_property_meta_data) -> "PropertyMetaData":
        """For internal use only!
        Initialize this PropertyMetaData object.

        :param java_property_meta_data: A java object of type 'PropertyMetaData'
        """
        self = cls.__new__(cls)
        self._property_meta_data = java_property_meta_data
        return self

    def get_dimension(self) -> int:
        """Get the dimension of the property.

        :return: the dimension of the property
        """
        return java_handler(self._property_meta_data.getDimension, [])

    def get_name(self) -> str:
        """Get the name of this property.

        :return: the name of this property
        """
        return java_handler(self._property_meta_data.getName, [])

    def get_property_id(self) -> PgxId:
        """Get the ID of this property.

        :return: the ID of this property
        """
        java_id = java_handler(self._property_meta_data.getPropertyId, [])
        return PgxId(java_id)

    def get_property_type(self) -> str:
        """Get the type of this property

        :return: the type of this property
        """
        java_property_type = java_handler(self._property_meta_data.getPropertyType, [])
        vertex_property_type = enum_to_python_str(java_property_type)
        return vertex_property_type

    def is_transient(self) -> bool:
        """Indicate if the property is transient or not.

        :return: whether the property is transient or not
        """
        return java_handler(self._property_meta_data.isTransient, [])

    def set_transient(self, transient: bool) -> None:
        """Set whether the property is transient or not.

        :param transient: A boolean value
        """
        return java_handler(self._property_meta_data.setTransient, [transient])

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return java_handler(self._property_meta_data.equals, [other._property_meta_data])

    def __repr__(self) -> str:
        return java_handler(self._property_meta_data.toString, [])

    def __hash__(self) -> NoReturn:
        raise TypeError(UNHASHABLE_TYPE.format(type_name=self.__class__))
