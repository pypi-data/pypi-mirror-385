#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils.error_handling import java_handler
from pypgx.api.mllib._model_utils import ModelStorer
from pypgx.api._pgx_context_manager import PgxContextManager


class Model(PgxContextManager):
    """Model object"""

    _java_class = 'oracle.pgx.api.mllib.Model'

    def __init__(self, java_generic_model):
        """
        Initialize model.

        :param java_generic_model: reference to java object
        """
        self._model = java_generic_model

    def is_fitted(self) -> bool:
        """Whether or not the model has been fitted.

        :returns: Always returns False since this base class cant be fitted.
        """
        return False

    def export(self) -> ModelStorer:
        """Return a ModelStorer object which can be used to save the model.

        :returns: ModelStorer object
        :rtype: ModelStorer
        """
        return ModelStorer(self)

    def destroy(self) -> None:
        """Destroy this model object."""
        java_handler(self._model.destroy, [])

    def close(self) -> None:
        """Call destroy"""
        self.destroy()
