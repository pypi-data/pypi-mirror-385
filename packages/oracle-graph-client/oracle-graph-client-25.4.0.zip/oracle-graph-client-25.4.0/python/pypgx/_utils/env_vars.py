#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

"""Initialize environment and local variables during import."""

import os
import atexit
import shutil
import tempfile
import jnius_config

# PACKAGED_EMBEDDED_DIST determines the module installation type.
# There are 2 pypgx installations from which this script will be used:
# 1) client pypgx distribution,
# 2) embedded pypgx distribution, for which here we modify the default
# graph algorithm language to be Java instead of GM.
PACKAGED_EMBEDDED_DIST = False


def init_env():
    """Initialize the environment of pypgx."""
    if PACKAGED_EMBEDDED_DIST:
        os.environ['PGX_GRAPH_ALGORITHM_LANGUAGE'] = 'JAVA'
        os.environ['PGX_JAVA_HOME_DIR'] = '<system-java-home-dir>'

    if 'PGX_TMP_DIR' not in os.environ:
        temporary_file = tempfile.mkdtemp()
        atexit.register(shutil.rmtree, path=temporary_file)
        os.environ['PGX_TMP_DIR'] = temporary_file


def init_jnius():
    """Initialize the configuration of jnius."""
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    jars_dir = os.path.join(cur_dir, '..', 'jars/*')
    jnius_config.add_classpath(jars_dir)

    # Add anything in PGX_CLASSPATH env variable to jnius config
    if 'PGX_CLASSPATH' in os.environ:
        paths = os.environ['PGX_CLASSPATH'].split(':')
        for path in paths:
            jnius_config.add_classpath(path)
