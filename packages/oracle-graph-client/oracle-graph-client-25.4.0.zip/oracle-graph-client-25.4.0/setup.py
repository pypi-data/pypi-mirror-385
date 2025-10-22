#
# Copyright (C) 2013 - 2025, Oracle and/or its affiliates. All rights reserved.
# ORACLE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
import shutil

from pathlib import Path
from setuptools import setup

SETUP_PATH = Path(__file__).resolve().parent
LIB_PATH = SETUP_PATH / "lib"
PYPGX_JARS_PATH = SETUP_PATH / "python" / "pypgx" / "jars"
OPG4PY_JARS_PATH = SETUP_PATH / "python" / "opg4py" / "jars"

try:
    for jar_file in LIB_PATH.iterdir():
        shutil.copy(jar_file, PYPGX_JARS_PATH)
        if "logback" not in str(jar_file):
            shutil.copy(jar_file, OPG4PY_JARS_PATH)

    setup(
        name="oracle-graph-client",
        python_requires=">=3.10",
        install_requires=[
            # We are using few APIs of numpy and pandas, so we can afford to be lenient in
            # the lower bound. We use more pyjnius APIs, so we are strict with the lower
            # bound to avoid version problems. Python dependency resolvers use the highest
            # possible version, so in most cases the lower bound should not matter.
            "numpy >= 2.0.2",
            "pyjnius >= 1.6.1",
            "pandas >= 2.2.2",
        ],
        version="25.4.0",
        description="Oracle Graph Python Client",
        url="https://www.oracle.com/database/graph/",
        platforms=["Linux x86_64"],
        license="Oracle Free Use Terms and Conditions (FUTC)",
        long_description="The Python client for the Property Graph feature of Oracle Database",
        packages=[
            "pypgx",
            "pypgx.api",
            "pypgx.api.auth",
            "pypgx.api.filters",
            "pypgx.api.frames",
            "pypgx.api.mllib",
            "pypgx.api.redaction",
            "pypgx._utils",
            "pypgx.jars",
            "opg4py",
            "opg4py.jars",
            "opg4py.pgql",
            "opg4py.graph_importer",
            "opg4py._adb",
            "opg4py._utils",
        ],
        package_dir={"pypgx": "python/pypgx",
                     "opg4py": "python/opg4py"},
        package_data={"pypgx": ["*.txt"],
                      "pypgx.jars": ["*.jar"],
                      "pypgx.resources": ["*"],
                      "opg4py.jars": ["*.jar"]},
    )

finally:
    for jar_file in LIB_PATH.iterdir():
        pypgx_file_to_remove = PYPGX_JARS_PATH / jar_file.name
        pypgx_file_to_remove.unlink()

        if "logback" not in str(jar_file):
            opg4py_file_to_remove = OPG4PY_JARS_PATH / jar_file.name
            opg4py_file_to_remove.unlink()
