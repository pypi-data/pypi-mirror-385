#
# Copyright (C) 2013 - 2025, Oracle and/or its affiliates. All rights reserved.
# ORACLE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
from jnius import autoclass
from opg4py._adb.job import Job
from opg4py._utils.error_handling import java_handler
from pypgx.api._server_instance import ServerInstance

AdbGraphClient = autoclass('oracle.pg.rdbms.AdbGraphClient')
AdbGraphClientConfiguration = autoclass('oracle.pg.rdbms.AdbGraphClientConfiguration')
EnvironmentStatus = autoclass('oracle.pg.rdbms.EnvironmentStatus')
DriverManager = autoclass('java.sql.DriverManager')
TimeUnit = autoclass('java.util.concurrent.TimeUnit')


class AdbClient:
    def __init__(self, config):
        """Creates a new ADB Graph Client

        :param config: the client configuration
        :return: A client handle
        """
        self.config = config
        self.client = None

    def __enter__(self):
        builder = java_handler(AdbGraphClientConfiguration.builder, [])

        # mandatory fields
        builder.database(self.config['database'])
        builder.username(self.config['username'])
        builder.password(self.config['password'])
        builder.endpoint(self.config['endpoint'])

        # optional fields
        if 'tenant' in self.config:
            builder.tenant(self.config['tenant'])

        if 'tenancy_ocid' in self.config:
            builder.tenancyOcid(self.config['tenancy_ocid'])

        if 'cloud_database_name' in self.config:
            builder.cloudDatabaseName(self.config['cloud_database_name'])

        if 'database_ocid' in self.config:
            builder.databaseOcid(self.config['database_ocid'])

        if 'refresh_time_before_token_expiry_ms' in self.config:
            builder.refreshTimeBeforeTokenExpiry(self.config['refresh_time_before_token_expiry_ms'])
            builder.refreshTimeBeforeTokenExpiryTimeUnit(TimeUnit.MILLISECONDS)

        if 'job_poll_interval_ms' in self.config:
            builder.jobPollInterval(self.config['job_poll_interval_ms'])
            builder.jobPollIntervalTimeUnit(TimeUnit.MILLISECONDS)

        if 'graph_studio_api_version' in self.config:
            builder.graphStudioApiVersion(self.config['graph_studio_api_version'])

        config = java_handler(builder.build, [])
        self.client = java_handler(AdbGraphClient, [config])
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.client is not None:
            self.client.close()

    def is_attached(self):
        """Checks if the Autonomous Database is currently attached to an environment.

        :return: True if the Autonomous Database is currently attached to an environment. False otherwise.
        """
        if self.client is None:
            self.__enter__()
        return java_handler(self.client.isAttached, [])

    def get_environment_status(self):
        """Fetches the environment status of the Autonomous Database.

       :return: the environment status of the Autonomous Database.
       """
        if self.client is None:
            self.__enter__()
        return java_handler(self.client.getEnvironmentStatus, [])

    def start_environment(self, memory):
        """Starts attaching the Autonomous Database to a new environment.

        :param memory: the amount of system memory (in gigabytes) to allocate on the attached environment.
        :return: a Job instance which completes once attachment operation completes.

        Throws: IllegalStateException - if the Autonomous Database is currently not in EnvironmentStatus#DETACHED state
        """
        if self.client is None:
            self.__enter__()
        return Job(java_handler(self.client.startEnvironment, [memory]))

    def stop_environment(self):
        """Starts detaching the Autonomous Database from the current environment. Note: all in-memory data will be lost

        :return: a Job instance which completes once detachment operation completes.

        Throws: IllegalStateException - if the Autonomous Database is currently not in EnvironmentStatus#ATTACHED state
        """
        if self.client is None:
            self.__enter__()
        return Job(java_handler(self.client.stopEnvironment, []))

    def restart_environment(self):
        """Starts re-attaching the Autonomous Database to a new environment.

        :return: a Job instance which completes once re-attachment operation completes.

        Throws: IllegalStateException - if the Autonomous Database is currently not in EnvironmentStatus#ATTACHED state
        """
        if self.client is None:
            self.__enter__()
        return Job(java_handler(self.client.restartEnvironment, []))

    def get_pgx_instance(self):
        """Gets the PGX ServerInstance object of an attached environment which can be used to create a new session for
        in-memory graph analysis.

        :return: the PGX ServerInstance of the Autonomous Database.
        """
        if self.client is None:
            self.__enter__()
        return ServerInstance(java_handler(self.client.getPgxInstance, []))

    def get_current_memory(self):
        """Gets the current environment's allocated memory. Only returns the memory if environment is in attached
        status.

        :return: the allocated memory for the currently attached environment. The results' units are in Gigabytes and
                 in decimal format.
        """
        if self.client is None:
            self.__enter__()
        return java_handler(self.client.getCurrentMemory, [])

    def get_available_memory(self):
        """Gets the available memory for environments to allocate. Only returns the memory if environment is in
        detached status.

        :return: the available memory for the environments to allocate. The results' units are in Gigabytes and in
                 decimal format.
        """
        if self.client is None:
            self.__enter__()
        return java_handler(self.client.getAvailableMemory, [])

    @staticmethod
    def from_connection(jdbc_url, username, password):
        """Creates an AdbClient instance given the jdbc url and the credentials of a database.

        To use this API, the user must execute a GRANT statement for selection on the
        V$PDBS table for the GRAPH_DEVELOPER role.

        :param jdbc_url: The jdbc url of the connection.
        :param username: The username of the database.
        :param password: The password of the database.
        :return: The configuration object created from the connection.
        """
        connection = java_handler(DriverManager.getConnection, [jdbc_url, username, password])
        config_java = java_handler(AdbGraphClientConfiguration.fromConnection, [connection, password])

        config = {
            'tenant': java_handler(config_java.getTenancyOcid, []),
            'database': java_handler(config_java.getDatabase, []),
            'database_ocid': java_handler(config_java.getDatabaseOcid, []),
            'username': java_handler(config_java.getUsername, []),
            'password': java_handler(config_java.getPassword, []),
            'endpoint': java_handler(config_java.getEndpoint, [])
        }

        client = AdbClient(config)

        return client.__enter__()
