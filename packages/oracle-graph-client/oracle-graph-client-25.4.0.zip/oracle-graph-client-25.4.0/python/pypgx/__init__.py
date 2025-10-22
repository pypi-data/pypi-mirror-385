#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

"""Python PGX client.

Some core functions are provided directly at the top level of the package.

The documented behavior of the PyPGX API is stable between versions. Other parts of
the API, in particular attributes whose name starts with an underscore, are considered
internal implementation details and may change between versions.
"""

import jnius_config
from pypgx._utils import env_vars as _env_vars

if jnius_config.vm_running:
    raise RuntimeError("PyPGX must be imported before jnius (or packages dependent on jnius)")
_env_vars.init_env()
_env_vars.init_jnius()

try:
    # ask opg4py to provide its JARs to the jnius_config classpath
    # so that jnius will be started properly and will have access
    # to opg4py-specific JARs
    import opg4py
    # disable access like `pypgx.opg4py`
    del opg4py
except ModuleNotFoundError:
    # skip the exception when opg4py isn't installed
    pass

from pypgx._utils.error_handling import PgxError
from pypgx._utils.loglevel import setloglevel
from pypgx.api._pgx import get_instance, get_session

# keep it accessible from the public API for backwards compatibility
from pypgx._utils.env_vars import PACKAGED_EMBEDDED_DIST

__all__ = ["get_instance", "get_session", "setloglevel", "PgxError"]

__version__ = '25.4.1'
