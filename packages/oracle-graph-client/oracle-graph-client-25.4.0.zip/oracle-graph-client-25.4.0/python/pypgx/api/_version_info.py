#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils import conversion


class VersionInfo:
    """Class that holds version information about PGX.

    :ivar release_version: The PGX release version.
    :vartype release_version: str

    :ivar api_version: The PGX API version (e.g. "3.13.0").
    :vartype api_version: str

    :ivar pgql_version: The PGQL version.
    :vartype pgql_version: str

    :ivar server_type: The type of server ("sm" or "distributed").
    :vartype server_type: str

    :ivar build: The date PGX was built, in ISO-8601 format.
    :vartype build: str

    :ivar commit: The full hash of the commit from which PGX was built.
    :vartype commit: str

    :ivar display_fields: The display fields to show when converting to string representation
    :vartype display_fields: dict
    """

    _java_class = 'oracle.pgx.common.VersionInfo'

    def __init__(self, version_info) -> None:
        self.release_version = version_info.getReleaseVersion()
        self.api_version = version_info.getApiVersion()

        self.pgql_version = version_info.getPgqlVersion()
        self.server_type = version_info.getServerType()
        self.build = version_info.getBuild()
        self.commit = version_info.getCommit()
        self.display_fields = conversion.map_to_python(version_info.getDisplayFields())

    def __repr__(self) -> str:
        if (self.display_fields):
            return "{}({})".format(
                self.__class__.__name__,
                ", ".join('{}={}'.format(k, v) for k, v in self.display_fields.items())
            )

        return """{}(release_version={}, api_version={}, pgql_version={},
                 server_type={}, build={}, commit={})""".format(
            self.__class__.__name__,
            self.release_version,
            self.api_version,
            self.pgql_version,
            self.server_type,
            self.build,
            self.commit,
        )
