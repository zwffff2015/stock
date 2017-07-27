# coding:utf-8

import sys
import MySQLdb
from wechat.weChatSender import sendMessageToMySelf
from common.LoggerHelper import writeErrorLog, writeWarningLog


class MySqlConnection:
    def __init__(self, ip, port, user, password, database):
        reload(sys)
        sys.setdefaultencoding('utf-8')

        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = MySQLdb.connect(host=self.ip, port=self.port, user=self.user, passwd=self.password,
                                          db=self.database, charset='utf8')

    def execute(self, sql, parameter=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, parameter) if parameter is not None else cursor.execute(sql)
            self.connection.commit()
        except Exception as e:
            writeErrorLog(unicode('executeFailed, sql:{0}, error:{1}').format(sql, str(e)))
            self.connection.rollback()
        finally:
            cursor.close()

    def select(self, sql, fetchall=True):
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            return cursor.fetchall() if fetchall else cursor.fetchone()
        except Exception as e:
            writeErrorLog(unicode('selectFailed, sql:{0}, error:{1}').format(sql, str(e)))
            self.connection.rollback()
        finally:
            cursor.close()

    def batchInsert(self, sql, parameters):
        try:
            cursor = self.connection.cursor()
            cursor.executemany(sql, parameters)
            self.connection.commit()
        except Exception as e:
            writeErrorLog(
                unicode('batchInsertFailed, sql:{0},parameters:{2}, error:{1}').format(sql, str(e), parameters))
            self.connection.rollback()
        finally:
            cursor.close()

    def disconnect(self):
        if self.connection:
            self.connection.close()
