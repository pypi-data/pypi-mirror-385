#
# Copyright (C) 2013 - 2025, Oracle and/or its affiliates. All rights reserved.
# ORACLE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
from jnius import autoclass
from opg4py._utils.error_handling import java_handler

GraphImporterClass = autoclass('oracle.pg.imports.GraphImporter')
GraphImporterBuilderClass = autoclass('oracle.pg.imports.GraphImporter$Builder')
input_type = autoclass('oracle.pg.imports.GraphImportInputFormat')
output_type = autoclass('oracle.pg.imports.GraphImportOutputFormat')

input_types = {}
input_types['graphson'] = input_type.GRAPHSON

output_types = {}
output_types['pg_pgql'] = output_type.PG_PGQL
output_types['pg_sql'] = output_type.PG_SQL
output_types['pg_view'] = output_type.PG_VIEW


class GraphImporter:
    """Wrapper class for oracle.pg.imports.GraphImporter."""

    def __init__(self, config):
        """Creates a new Graph Importer

        :param config: the client configuration
        :return: A graph importer object
        """
        self.importer = GraphImporterClass
        self.config = config

        builder = java_handler(GraphImporterBuilderClass, [])

        # Mandatory fields
        builder = java_handler(builder.setDbJdbcUrl, [self.config['jdbc_url']])
        builder = java_handler(builder.setDbUsername, [self.config['username']])
        builder = java_handler(builder.setDbPassword, [self.config['password']])
        builder = java_handler(builder.setFilePath, [self.config['file_path']])
        builder = java_handler(builder.setGraphName, [self.config['graph_name']])

        output_format = self.config['output_format']
        input_format = self.config['input_format']

        if output_format is None or output_format not in output_types:
            raise ValueError("Invalid output format, valid output formats are: pg_pgql or pg_sql.")

        if input_format is None or input_format not in input_types:
            raise ValueError("Invalid input format, valid input formats are: graphson.")

        java_output_format = output_types[output_format]
        java_input_format = input_types[input_format]

        builder = java_handler(builder.setInputFormat, [java_input_format])
        builder = java_handler(builder.setOutputFormat, [java_output_format])

        # Optional fields
        if 'threads' in self.config:
            builder = java_handler(builder.setThreads, [self.config['threads']])

        if 'string_field_size' in self.config:
            builder = java_handler(builder.setStringFieldsSize, [self.config['string_field_size']])

        if 'franctional_seconds_precision' in self.config:
            builder = java_handler(builder.setFractionalSecondsPrecision,
                                   [self.config['franctional_seconds_precision']])

        if 'batch_size' in self.config:
            builder = java_handler(builder.setBatchSize, [self.config['batch_size']])

        if 'parallelism' in self.config:
            builder = java_handler(builder.setParallelism, [self.config['parallelism']])

        if 'dynamic_sampling' in self.config:
            builder = java_handler(builder.setDynamicSampling, [self.config['dynamic_sampling']])

        if 'match_options' in self.config:
            builder = java_handler(builder.setMatchOptions, [self.config['match_options']])

        if 'options' in self.config:
            builder = java_handler(builder.setOptions, [self.config['options']])

        self.importer = java_handler(builder.build, [])

    def import_graph(self):
        """Import the graph to the database provided to the constructor.

        :return: A string containing the CPG statement indicating the import finished successfully.
        """
        return java_handler(self.importer.importGraph, [])
