#
# Copyright (C) 2013 - 2025, Oracle and/or its affiliates. All rights reserved.
# ORACLE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#

"""Initialize environment and local variables during import."""

import os
import jnius_config


def init_jnius():
    """Initialize the configuration of jnius."""
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    jars_dir = os.path.join(cur_dir, '..', 'jars/*')
    jnius_config.add_classpath(jars_dir)

    # Add anything in OPG_CLASSPATH env variable to jnius config
    if 'OPG_CLASSPATH' in os.environ:
        paths = os.environ['OPG_CLASSPATH'].split(':')
        for path in paths:
            jnius_config.add_classpath(path)
