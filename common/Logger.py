# coding=utf-8
import os
import logging
import logging.config
import time
import inspect

class Logger():
    def printfNow(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def __init__(self):
        #filePath = os.path.abspath(os.path.join(os.getcwd(), "../config/logging.conf"))
        #logging.config.fileConfig(filePath)
        self.__logger = logging.getLogger()
        path = os.path.abspath("../log/error.log")

        handler = logging.FileHandler(path)
        self.__logger.addHandler(handler)
        self.__logger.setLevel(logging.NOTSET)

    def getLogMessage(self, level, message):
        # message = "[%s] %s " %(self.printfNow(),message)

        frame, filename, lineNo, functionName, code, unknowField = inspect.stack()[2]
        '''日志格式：[时间] [类型] [记录代码] 信息'''
        return "[%s] [%s] [%s - %s - %s] %s" % (self.printfNow(), level, filename, lineNo, functionName, message)

    def info(self, message):
        message = self.getLogMessage("info", message)
        self.__logger.info(message)

    def error(self, message):
        message = self.getLogMessage("error", message)
        self.__logger.error(message)

    def warning(self, message):
        message = self.getLogMessage("warning", message)
        self.__logger.warning(message)

    def debug(self, message):
        message = self.getLogMessage("debug", message)
        self.__logger.debug(message)

    def critical(self, message):
        message = self.getLogMessage("critical", message)
        self.__logger.critical(message)

    def exception(self, message):
        message = self.getLogMessage("exception", message)
        self.__logger.exception(message)
