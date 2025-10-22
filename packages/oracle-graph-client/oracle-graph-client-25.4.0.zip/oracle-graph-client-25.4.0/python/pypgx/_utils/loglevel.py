#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from jnius import autoclass, cast
import logging as log


def setloglevel(loggername: str = "", loglevel: str = "DEBUG") -> None:
    """Set loglevel for PGX.
    If `loglevel` is invalid (see below), it writes this to the python log as an error
    without raising any exceptions.

    :param loggername: Name of the PGX logger. If empty, ROOT logger's level is updated.
    :type loggername: str
    :param loglevel: Level specification. Must be one of
        `"OFF", "FATAL", "ERROR", "WARN", "INFO", "DEBUG", "TRACE", "ALL"`.
    :type loglevel: str

    :returns: None
    """

    rootloggername = autoclass("org.slf4j.Logger").ROOT_LOGGER_NAME.lower()
    loggerfactory = autoclass("org.slf4j.LoggerFactory")
    level = autoclass("ch.qos.logback.classic.Level")

    logger = None
    if (loggername == "") or (loggername.lower() == rootloggername):
        logger = cast("ch.qos.logback.classic.Logger", loggerfactory.getLogger(rootloggername))
    else:
        logger = cast("ch.qos.logback.classic.Logger", loggerfactory.getLogger(loggername))

    actuallevel = level.toLevel(loglevel)
    if (actuallevel.toString().lower() != loglevel.lower()):
        log.error("Invalid loglevel specified: {}".format(loglevel))
    else:
        logger.setLevel(actuallevel)
    return None
