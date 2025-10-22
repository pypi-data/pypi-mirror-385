#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#
from typing import List

from pypgx._utils.error_handling import java_handler


class ModelRepository:
    """
    ModelRepository object that exposes crud operations on
    - model stores and
    - the models within these model stores.
    """

    _java_class = 'oracle.pgx.api.mllib.ModelRepository'

    def __init__(self, java_generic_model_repository):
        """
        Initialize model repository.

        :param java_generic_model_repository: reference to java object
        """
        self._java_specific_model_repository = java_generic_model_repository

    def create(self, model_store_name: str) -> None:
        """Create a new model store.

        :param model_store_name: The name of the model store.
        :type model_store_name: str
        """
        java_handler(self._java_specific_model_repository.create, [model_store_name])

    def delete_model_store(self, model_store_name: str) -> None:
        """Delete a model store.

        :param model_store_name: The name of the model store.
        :type model_store_name: str
        """
        java_handler(
            self._java_specific_model_repository.deleteModelStore,
            [model_store_name]
        )

    def list_model_stores_names(self) -> List[str]:
        """List the names of all model stores in the model repository.

        :returns: List of names.
        :rtype: List[str]
        """
        return java_handler(self._java_specific_model_repository.listModelStoresNames, [])

    def list_model_stores_names_matching(self, regex: str) -> List[str]:
        """List the names of all model stores in the model repository that match the regex.

        :param regex: A regex in form of a string.
        :type regex: str

        :returns: List of matching names.
        :rtype: List[str]
        """
        return java_handler(
            self._java_specific_model_repository.listModelStoresNamesMatching,
            [regex]
        )

    def list_models(self, model_store_name: str) -> List[str]:
        """List the models present in the model store with the given name.

        :param model_store_name: The name of the model store (non-prefixed).
        :type model_store_name: str

        :returns: List of model names.
        :rtype: List[str]
        """
        return java_handler(
            self._java_specific_model_repository.listModels,
            [model_store_name]
        )

    def get_model_description(self, model_store_name: str, model_name: str) -> str:
        """Retrieve the description of the model in the specified model store,
        with the given model name.

        :param model_store_name: The name of the model store.
        :type model_store_name: str
        :param model_name: The name under which the model was stored.
        :type model_name: str

        :returns: A string containing the description that was stored with the model.
        :rtype: str
        """
        return java_handler(
            self._java_specific_model_repository.getModelDescription,
            [model_store_name, model_name]
        )

    def delete_model(self, model_store_name: str, model_name: str) -> None:
        """Delete the model in the specified model store with the given model
        name.

        :param model_store_name: The name of the model store.
        :type model_store_name: str
        :param model_name: The name under which the model was stored.
        :type model_name: str
        """
        java_handler(
            self._java_specific_model_repository.deleteModel,
            [model_store_name, model_name]
        )
