# coding=utf-8
import os
import logging
import logging.config


class Logger():
    def __init__(self):
        filePath = os.path.abspath(os.path.join(os.getcwd(), "../config/logging.conf"))
        logging.config.fileConfig(filePath)
        self.__logger = logging.getLogger()

    def info(self, message):
        self.__logger.info(message)

    def error(self, message):
        self.__logger.error(message)

    def warning(self, message):
        self.__logger.warning(message)

    def debug(self, message):
        self.__logger.debug(message)

    def critical(self, message):
        self.__logger.critical(message)

    def exception(self, message):
        self.__logger.exception(message)
