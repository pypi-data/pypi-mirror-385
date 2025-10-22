#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#
from typing import Optional

from pypgx._utils.error_handling import java_handler
from pypgx.api.mllib import ModelRepository


def _input_db_params(model_repo_builder,
                     username: Optional[str], password: Optional[str],
                     jdbc_url: Optional[str], keystore_alias: Optional[str],
                     schema: Optional[str]):
    if username:
        model_repo_builder = java_handler(model_repo_builder.username, [username])
    if password:
        model_repo_builder = java_handler(model_repo_builder.password, [password])
    if jdbc_url:
        model_repo_builder = java_handler(model_repo_builder.jdbcUrl, [jdbc_url])
    if keystore_alias:
        model_repo_builder = java_handler(model_repo_builder.keystoreAlias, [keystore_alias])
    if schema:
        model_repo_builder = java_handler(model_repo_builder.schema, [schema])
    return java_handler(model_repo_builder.open, [])


class ModelRepositoryBuilder:
    """
    ModelRepositoryBuilder object that can be used to configure the connection to a
    model repository.
    """

    _java_class = 'oracle.pgx.api.mllib.GenericModelRepositoryBuilder'

    def __init__(self, java_generic_model_repository_builder):
        """
        Initialize model repository builder.

        :param java_generic_model_repository_builder: reference to java object
        """
        self._java_generic_model_repository_builder = java_generic_model_repository_builder

    def db(self,
           username: Optional[str] = None,
           password: Optional[str] = None,
           jdbc_url: Optional[str] = None,
           keystore_alias: Optional[str] = None,
           schema: Optional[str] = None) -> ModelRepository:
        """
        Connect to a model repository backed by a database.

        :param username: username in database
        :param password: password of username in database
        :param jdbc_url: jdbc url of database
        :param keystore_alias: the keystore alias to get the password in the keystore
        :param schema: the schema of the model store in database

        :return: A model repository configured to connect to a database.
        """
        model_builder = java_handler(self._java_generic_model_repository_builder.db, [])
        java_specific_model_repository = _input_db_params(
            model_builder, username, password, jdbc_url,
            keystore_alias, schema
        )
        return ModelRepository(java_specific_model_repository)
