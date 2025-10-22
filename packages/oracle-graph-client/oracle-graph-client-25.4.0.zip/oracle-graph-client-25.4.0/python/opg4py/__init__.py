#
# Copyright (C) 2013 - 2025, Oracle and/or its affiliates. All rights reserved.
# ORACLE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#

"""OPG4Py package."""

import sys
import types
import jnius_config
from opg4py._utils import env_vars as _env_vars

if jnius_config.vm_running:
    raise RuntimeError("OPG4Py must be imported before jnius (or packages dependent on jnius)")
_env_vars.init_jnius()

try:
    import pypgx  # noqa: F401
except ModuleNotFoundError:
    raise RuntimeError("PyPGX must be installed to use OPG4Py")

try:
    from jnius import autoclass  # noqa: F401
except Exception as exc:
    if "Unable to find" in str(exc):
        message = "OPG4Py requires a Java (JDK) installation, the following exception was raised during setup:\n\t"
        raise RuntimeError(message + str(exc)) from None

from opg4py import pgql  # noqa: E402
from opg4py import graph_importer  # noqa: E402
from opg4py import adb  # noqa: E402
from opg4py import graph_server  # noqa: E402

# Ensure that version 22.4+ of Graph Client is backwards compatible with older versions. The
# 'pypgx.pg.rdbms.graph_server' module is deprecated and replaced with 'opg4py.graph_server'.
pypgx.pg = sys.modules["pypgx.pg"] = types.ModuleType("pypgx.pg")
pypgx.pg.rdbms = sys.modules["pypgx.pg.rdbms"] = types.ModuleType("pypgx.pg.rdbms")
pypgx.pg.rdbms.graph_server = sys.modules["pypgx.pg.rdbms.graph_server"] = graph_server

__all__ = ["pgql", "adb", "graph_server", "graph_importer"]
