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
from common.NumberHelper import getFloat, getRound

'''
    用于数据补充，如果从网站没有抓取到相应技术指标数据，则自己计算
'''


def updateKDJ():
    sql = unicode("SELECT code,date,k,d,j from s_stock_tech where K=0 and d=0 and j=0 ORDER by code,date asc")
    data = select(sql)

    if len(data) <= 0:
        writeLog(unicode("没有获取到无效KDJ指标数据"))
        return

    for item in data:
        code = item[0]
        date = item[1]
        try:
            rsv = getRSV(code, date)
            if rsv is None:
                continue

            techSql = unicode(
                "SELECT k,d,j from s_stock_tech where code='{0}' and date<'{1}' ORDER by date desc limit 1").format(
                code,
                date)
            data = select(techSql)
            yesterdayK = 50
            yesterdayD = 50

            if len(data) > 0:
                yesterdayK = data[0][0]
                yesterdayD = data[0][1]

            todayK = getFloat((rsv + 2 * float(yesterdayK)) / 3)
            todayD = getFloat((todayK + 2 * float(yesterdayD)) / 3)
            todayJ = getFloat(3 * todayK - 2 * todayD)
            writeLog(unicode("更新KDJ指标数据，code:{0},date:{1},todayK:{2},todayD:{3},todayJ:{4},rsv:{5}").format(code, date,
                                                                                                            todayK,
                                                                                                            todayD,
                                                                                                            todayJ,
                                                                                                            rsv))
            print code, date, todayK, todayD, todayJ, rsv

            updateSql = unicode("update s_stock_tech set k={0},d={1},j={2} where code='{3}' and date='{4}'").format(
                todayK,
                todayD,
                todayJ,
                code,
                date)
            execute(updateSql)
        except Exception, e:
            writeErrorLog(unicode("更新KDJ指标数据异常，code:{0}, date:{1}, e:{2}").format(code, date, str(e)))


def getRSV(code, date):
    sql = unicode(
        "select min(lowPrice),max(highPrice) from (SELECT * from s_stock where code='{0}' and date<='{1}' ORDER by date desc limit 9) as t").format(
        code, date)
    data = select(sql)

    if len(data) <= 0:
        return None

    minLow = data[0][0]
    maxHigh = data[0][1]

    todayClosePrice = getTodayClosePrice(code, date)
    if todayClosePrice is None:
        return None

    if (maxHigh - minLow == 0):
        return None

    return round((todayClosePrice - minLow) * 100 / (maxHigh - minLow), 2)


def updateMACD():
    sql = unicode(
        "select code,date,macd,dif,dea from s_stock_tech where MACD=0 and dif=0 and dea=0 ORDER by code,date asc")
    data = select(sql)

    if len(data) <= 0:
        writeLog(unicode("没有获取到无效MACD指标数据"))
        return

    for item in data:
        code = '002466'  # item[0]
        date = '2017-07-12'  # item[1]
        try:
            data = getMACD(code, date)
            if data is None:
                continue

            updateSql = unicode(
                "update s_stock_tech set macd={0},dif={1},dea={2} where code='{3}' and date='{4}'").format(
                data[0],
                data[1],
                data[2],
                code,
                date)
            execute(updateSql)
        except Exception, e:
            writeErrorLog(unicode("更新MACD指标数据异常，code:{0}, date:{1}, e:{2}").format(code, date, str(e)))


def updateAllMACD():
    sql = unicode("select code from s_stock_tech group by code")
    stockList = []  # select(sql)

    if stockList is None:
        return

    for stock in stockList:
        sql = unicode(
            "select code,date,macd,dif,dea from s_stock_tech where code='{0}' ORDER by code,date asc limit 1,60000").format(
            stock)
        data = select(sql)

        if len(data) <= 0:
            # writeLog(unicode("没有获取到无效MACD指标数据,code:{0}").format(stock[0]))
            continue

        for item in data:
            code = item[0]
            date = item[1]
            try:
                data = getMACD(code, date)
                if data is None:
                    continue

                updateSql = unicode(
                    "update s_stock_tech set macd={0},dif={1},dea={2} where code='{3}' and date='{4}'").format(
                    data[0],
                    data[1],
                    data[2],
                    code,
                    date)
                execute(updateSql)
            except Exception, e:
                writeErrorLog(unicode("更新MACD指标数据异常，code:{0}, date:{1}, e:{2}").format(code, date, str(e)))


def getMACD(code, date):
    techSql = unicode(
        "SELECT DIF,EXPMA1,DEA from s_stock_tech where code='{0}' and date<'{1}' ORDER by date desc limit 1").format(
        code,
        date)
    data = select(techSql)

    if len(data) <= 0:
        return None

    yesterdayDIF = data[0][0]
    yesterdayEMA12 = data[0][1]
    yesterdayDEA = data[0][2]
    yesterdayEMA26 = yesterdayEMA12 - yesterdayDIF

    todayClosePrice = getTodayClosePrice(code, date)
    if todayClosePrice is None:
        return None

    todayEMA12 = round((2 * todayClosePrice + 11 * yesterdayEMA12) / 13, 2)
    todayEMA26 = round(2 * float(todayClosePrice) / 27, 2) + round(25 * float(yesterdayEMA26) / 27, 2)
    todayDIF = round(todayEMA12 - todayEMA26, 2)
    todayDEA = round((8 * float(yesterdayDEA) + todayDIF * 2) / 10, 2)
    todayMACD = (todayDIF - todayDEA) * 2
    writeLog(unicode("更新MACD指标数据，code:{0},date:{1},todayDIF:{2},todayDEA:{3},todayMACD:{4}").format(code, date,
                                                                                                    todayDIF,
                                                                                                    todayDEA,
                                                                                                    todayMACD))
    print code, date, todayDIF, todayDEA, todayMACD
    return (todayMACD, todayDIF, todayDEA)


def updateEXPMA():
    sql = unicode(
        "select code,date from s_stock_tech where EXPMA1=0 and EXPMA2=0 ORDER by code,date asc")
    data = select(sql)

    if len(data) <= 0:
        writeLog(unicode("没有获取到无效EXPMA指标数据"))
        return

    for item in data:
        code = item[0]
        date = item[1]
        try:
            data = getEXPMA(code, date)
            if data is None:
                continue

            updateSql = unicode(
                "update s_stock_tech set EXPMA1={0},EXPMA2={1} where code='{2}' and date='{3}'").format(
                data[0],
                data[1],
                code,
                date)
            execute(updateSql)
        except Exception, e:
            writeErrorLog(unicode("更新EXPMA指标数据异常，code:{0}, date:{1}, e:{2}").format(code, date, str(e)))


def getEXPMA(code, date):
    techSql = unicode(
        "SELECT EXPMA1,EXPMA2 from s_stock_tech where code='{0}' and date<'{1}' ORDER by date desc limit 1").format(
        code,
        date)
    data = select(techSql)

    if len(data) <= 0:
        return None

    yesterdayEXPMA1 = data[0][0]
    yesterdayEXPMA2 = data[0][1]

    todayClosePrice = getTodayClosePrice(code, date)
    if todayClosePrice is None:
        return None

    todayEXPMA1 = getRound((2 * todayClosePrice + 11 * yesterdayEXPMA1) / 13)
    todayEXPMA2 = getRound((2 * todayClosePrice + 49 * yesterdayEXPMA2) / 51)
    writeLog(unicode("更新EXPMA指标数据，code:{0},date:{1},todayEXPMA1:{2},todayEXPMA1:{3}").format(code, date,
                                                                                             todayEXPMA1,
                                                                                             todayEXPMA2))
    return (todayEXPMA1, todayEXPMA2)


def getTodayClosePrice(code, date):
    sql = unicode("SELECT closePrice from s_stock where code='{0}' and date='{1}'").format(code, date)
    data = select(sql)

    if len(data) <= 0:
        return None

    return data[0][0]


def runTask():
    if datetime.today().weekday() < 5 and datetime.now().hour >= 23 and datetime.now().hour < 24 and datetime.now().minute < 20:
        sendMessageToMySelf(unicode("开始计算今日技术指标数据"))
        begin = datetime.now()

        initMysql()
        updateKDJ()
        disconnect()
        end = datetime.now()

        message = unicode("计算今日技术指标数据的任务执行完毕,当前时间：{0}，执行用时：{1}").format(datetime.now(), end - begin)
        writeLog(message)
        sendMessageToMySelf(message)

    t = Timer(900, runTask)
    t.start()


def main(argv):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    # runTask()
    initMysql()
    updateAllMACD()


if __name__ == '__main__':
    main(sys.argv)
