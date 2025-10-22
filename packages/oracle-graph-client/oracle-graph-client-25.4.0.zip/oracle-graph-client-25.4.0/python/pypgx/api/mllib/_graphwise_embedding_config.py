#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

class GraphWiseEmbeddingConfig:
    """GraphWise embedding configuration."""

    _java_class = 'oracle.pgx.config.mllib.GraphWiseEmbeddingConfig'

    def get_embedding_type(self) -> str:
        """Return the embedding type used by this config"""
        pass

    def _get_config(self):
        pass
