# coding=utf-8

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))

from db.MysqlUtil import initMysql, execute, select, batchInsert, disconnect
from common.JsonHelper import loadJsonConfig
from datetime import datetime, timedelta
from common.LoggerHelper import writeErrorLog, writeWarningLog, writeInfoLog, writeDebugLog, writeLog
from wechat.weChatSender import sendMessageToMySelf
import time
from threading import Timer


def updateMAData(startDate):
    stockList = select(unicode(
        "SELECT code,name from s_stock_info"))  # loadJsonConfig(os.path.abspath(os.path.join(os.getcwd(), "../config/goodStockList.json")))
    for stock in stockList:
        code = stock[0]
        writeLog(unicode("开始更新股票：{0}，名称：{1}的均线数据").format(code, stock[1]))
        sql = unicode(
            "SELECT code,date,closePrice from s_stock where code='{0}' and date>'{1}' ORDER BY timestamp asc").format(
            code,
            startDate)
        data = select(sql)
        MA5 = calculateMA(5, data)
        MA10 = calculateMA(10, data)
        MA20 = calculateMA(20, data)
        MA30 = calculateMA(30, data)
        MA60 = calculateMA(60, data)
        MA120 = calculateMA(120, data)
        MA250 = calculateMA(250, data)

        for i in range(0, len(data)):
            date = data[i][1]
            updateSql = unicode(
                "update s_stock set MA5={0},MA10={1},MA20={2},MA30={3},MA60={4},MA120={5},MA250={6} where code='{7}' and date='{8}'").format(
                MA5.get(date), MA10.get(date), MA20.get(date), MA30.get(date), MA60.get(date), MA120.get(date),
                MA250.get(date), code, date)
            execute(updateSql)


def calculateMA(dayCount, data):
    result = {}
    for i in range(0, len(data)):
        if (i < dayCount - 1):
            result[data[i][1]] = 0
            continue

        sum = 0
        for j in range(0, dayCount):
            sum = sum + data[i - j][2]
        result[data[i][1]] = round(sum / dayCount, 2)

    return result


def updateTodayMAData():
    stockList = select(unicode(
        "SELECT code,name from s_stock_info"))  # loadJsonConfig(os.path.abspath(os.path.join(os.getcwd(), "../config/goodStockList.json")))
    for stock in stockList:
        code = stock[0]
        writeLog(unicode("开始更新股票：{0}，名称：{1} 今日的均线数据").format(code, stock[1]))
        MA5 = getMAData(5, code)
        MA10 = getMAData(10, code)
        MA20 = getMAData(20, code)
        MA30 = getMAData(30, code)
        MA60 = getMAData(60, code)
        MA120 = getMAData(120, code)
        MA250 = getMAData(250, code)

        updateSql = unicode(
            "update s_stock set MA5={0},MA10={1},MA20={2},MA30={3},MA60={4},MA120={5},MA250={6} where code='{7}' and date='{8}'").format(
            MA5, MA10, MA20, MA30, MA60, MA120,
            MA250, code, datetime.now().strftime('%Y-%m-%d'))
        execute(updateSql)


def getMAData(dayCount, code):
    sql = unicode(
        "select if(count(*)<{0},0,sum(closePrice)/{0}) from ( select closePrice from s_stock where code='{1}' order by timestamp desc limit {0}) as t").format(
        dayCount, code)
    data = select(sql)
    if len(data) <= 0:
        return 0
    else:
        return round(data[0][0], 2)


def runTask():
    if datetime.today().weekday() < 5 and datetime.now().hour >= 21 and datetime.now().hour < 22 and datetime.now().minute < 20:
        sendMessageToMySelf(unicode("开始更新今日均线数据"))
        begin = datetime.now()

        initMysql()
        updateTodayMAData()
        disconnect()
        end = datetime.now()

        message = unicode("更新今日均线数据的任务执行完毕,当前时间：{0}，执行用时：{1}").format(datetime.now(), end - begin)
        writeLog(message)
        sendMessageToMySelf(message)

    t = Timer(900, runTask)
    t.start()


def main(argv):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    runTask()


if __name__ == '__main__':
    main(sys.argv)
