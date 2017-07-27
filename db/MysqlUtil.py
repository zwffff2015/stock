# coding:utf-8

import os
from db.MysqlHelper import MySqlConnection
from common.JsonHelper import loadJsonConfig

MYSQLCONNECTION = None


def initMysql():
    global MYSQLCONNECTION
    config = loadJsonConfig(os.path.abspath(os.path.join(os.getcwd(), "../config/db.json")))
    MYSQLCONNECTION = MySqlConnection(config['host'], config['port'], config['user'], config['password'],
                                      config['database'])


def execute(sql, parameter=None):
    global MYSQLCONNECTION
    MYSQLCONNECTION.execute(sql, parameter)


def select(sql, fetchall=True):
    global MYSQLCONNECTION
    return MYSQLCONNECTION.select(sql, fetchall)


def batchInsert(sql, parameters):
    global MYSQLCONNECTION
    MYSQLCONNECTION.batchInsert(sql, parameters)


def disconnect():
    global MYSQLCONNECTION
    MYSQLCONNECTION.disconnect()
