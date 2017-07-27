import os
import logging
import logging.config

filePath = os.path.abspath(os.path.join(os.getcwd(), "../config/logging.conf"))
logging.config.fileConfig(filePath)
logger = logging.getLogger()


def writeDebugLog(message):
    logger.debug(message)


def writeInfoLog(message):
    logger.info(message)


def writeErrorLog(message):
    logger.error(message)


def writeWarningLog(message):
    logger.warning(message)


def writeLog(message):
    logger.info(message)
