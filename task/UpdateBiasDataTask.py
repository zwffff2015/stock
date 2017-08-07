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
from common.Logger import Logger


def updateBiasData(startDate):
    stockList = select(unicode(
        "SELECT code,name from s_stock_info"))  # loadJsonConfig(os.path.abspath(os.path.join(os.getcwd(), "../config/goodStockList.json")))
    for stock in stockList:
        code = stock[0]
        writeLog(unicode("开始更新股票：{0}，名称：{1}的Bias数据").format(code, stock[1]))

        sql = unicode(
            "SELECT code,date,closePrice from s_stock where code='{0}' and date>'{1}' ORDER BY timestamp asc").format(
            code,
            startDate)
        data = select(sql)
        MA6 = calculateMA(6, data)
        MA12 = calculateMA(12, data)
        MA24 = calculateMA(24, data)

        for i in range(0, len(data)):
            date = data[i][1]
            closePrice = float(data[i][2])
            MA6data = float(MA6.get(date))
            MA12data = float(MA12.get(date))
            MA24data = float(MA24.get(date))

            bias1 = 0 if MA6data == 0 else round((closePrice - MA6data) * 100 / MA6data, 2)
            bias2 = 0 if MA12data == 0 else round((closePrice - MA12data) * 100 / MA12data, 2)
            bias3 = 0 if MA24data == 0 else round((closePrice - MA24data) * 100 / MA24data, 2)

            updateSql = unicode(
                "update s_stock set bias1={0},bias2={1},bias3={2} where code='{3}' and date='{4}'").format(bias1, bias2,
                                                                                                           bias3, code,
                                                                                                           date)
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
        result[data[i][1]] = sum / dayCount

    return result


def updateTodayBiasData():
    stockList = select(unicode(
        "SELECT code,name from s_stock_info"))  # loadJsonConfig(os.path.abspath(os.path.join(os.getcwd(), "../config/goodStockList.json")))
    today = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    for stock in stockList:
        code = stock[0]
        writeLog(unicode("开始更新股票：{0}，名称：{1} 今日的Bias数据").format(code, stock[1]))

        sql = unicode("select code,closePrice from s_stock where code='{0}' and date='{1}'").format(code, today)
        data = select(sql)
        if (len(data) <= 0):
            writeLog(unicode("没有获取到今日的收盘价数据, code: {0}, date: {1}").format(code, today))
            continue

        closePrice = float(data[0][1])
        MA6 = float(getMAData(6, code, today))
        MA12 = float(getMAData(12, code, today))
        MA24 = float(getMAData(24, code, today))

        bias1 = 0 if MA6 == 0 else round((closePrice - MA6) * 100 / MA6, 2)
        bias2 = 0 if MA12 == 0 else round((closePrice - MA12) * 100 / MA12, 2)
        bias3 = 0 if MA24 == 0 else round((closePrice - MA24) * 100 / MA24, 2)

        updateSql = unicode(
            "update s_stock set bias1={0},bias2={1},bias3={2} where code='{3}' and date='{4}'").format(bias1, bias2,
                                                                                                       bias3, code,
                                                                                                       today)
        execute(updateSql)


def getMAData(dayCount, code, date):
    sql = unicode(
        "select if(count(*)<{0},0,sum(closePrice)/{0}) from ( select closePrice from s_stock where code='{1}' and date<='{2}' order by timestamp desc limit {0}) as t").format(
        dayCount, code, date)
    data = select(sql)
    if len(data) <= 0:
        return 0
    else:
        return float(data[0][0])


def runTask():
    if datetime.today().weekday() < 5 and datetime.now().hour >= 21 and datetime.now().hour < 22 and datetime.now().minute < 20:
        sendMessageToMySelf(unicode("开始更新今日bias数据"))
        begin = datetime.now()

        initMysql()
        updateTodayBiasData()
        disconnect()
        end = datetime.now()

        message = unicode("更新今日bias数据的任务执行完毕,当前时间：{0}，执行用时：{1}").format(datetime.now(), end - begin)
        writeLog(message)
        sendMessageToMySelf(message)

    t = Timer(900, runTask)
    t.start()


def main(argv):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    runTask()


if __name__ == '__main__':
    logger = Logger()
    try:
        main(sys.argv)
    except Exception, e:
        logger.exception(str(e))
