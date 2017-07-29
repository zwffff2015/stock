# coding=utf-8

'''
用于判断当前价格是否突破了N日均线上涨或者下跌
'''

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))

from stock import StockInfo
from api.tushareApi import getRealTimeData
from common.FileHelper import saveFile
from datetime import datetime, timedelta
from db.MysqlUtil import initMysql, execute, select, batchInsert, disconnect
from common.JsonHelper import loadJsonConfig
import time
from threading import Timer
from wechat.weChatSender import sendMessageToMySelf
from common.LoggerHelper import writeLog, writeErrorLog


def getCodeList():
    selectSql = unicode(
        "SELECT code,name from b_peg where date=(SELECT max(date) FROM b_peg where dataType={0}) and dataType={0} and peg>0 and peg<=0.5").format(
        1)
    return select(selectSql)


def checkAvgLine(fileName, stockList, needSaveToDb=True):
    result = []
    result.append(
        unicode("{0},{5},{1},{2},{3},{4}\n").format("代码", "类别", "昨日最高价", "今日最高价", "MaN", "名称").encode('gbk'))

    i = 0
    weekday = datetime.today().weekday()
    datediff = 3 if weekday == 0 else (weekday - 4 if weekday == 6 else 1)
    date = (datetime.now() - timedelta(days=datediff)).strftime('%Y-%m-%d')
    while i < len(stockList):
        code = stockList[i][0]
        name = stockList[i][1]
        try:
            sql = unicode(
                "SELECT code,date,MA5,MA10,MA20,MA30,MA60,MA120,MA250 from s_stock where code='{0}' and date='{1}'").format(
                code, date)
            data = select(sql)
            if (len(data) <= 0):
                writeLog(unicode("没有获取到均值数据, code: {0}, date: {1}").format(code, date))
                i = i + 1
                continue

            ma5 = data[0][2]
            ma10 = data[0][3]
            ma30 = data[0][5]
            ma60 = data[0][6]
            ma120 = data[0][7]
            ma250 = data[0][8]

            yesterdayPrice = StockInfo.getNPrice(code, 1, 'high')
            realTimePrice = float(getRealTimeData(code))

            if (yesterdayPrice != 0 and realTimePrice != 0 and yesterdayPrice <= ma5 and realTimePrice >= ma5):
                # 击穿5日均线，并上涨
                result.append(
                    unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '5up', yesterdayPrice, realTimePrice, ma5,
                                                                name).encode('gbk'))
                writeLog(unicode("[5up] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma5: {3}").format(code,
                                                                                                             yesterdayPrice,
                                                                                                             realTimePrice,
                                                                                                             ma5))

            if (yesterdayPrice != 0 and realTimePrice != 0 and yesterdayPrice <= ma10 and realTimePrice >= ma10):
                # 击穿10日均线，并上涨
                result.append(
                    unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '10up', yesterdayPrice, realTimePrice, ma10,
                                                                name).encode(
                        'gbk'))
                writeLog(unicode("[10up] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma10: {3}").format(code,
                                                                                                               yesterdayPrice,
                                                                                                               realTimePrice,
                                                                                                               ma10))

            if (yesterdayPrice != 0 and realTimePrice != 0 and yesterdayPrice <= ma30 and realTimePrice >= ma30):
                # 击穿30日均线，并上涨
                result.append(
                    unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '30up', yesterdayPrice, realTimePrice, ma30,
                                                                name).encode(
                        'gbk'))
                writeLog(unicode("[30up] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma30: {3}").format(code,
                                                                                                               yesterdayPrice,
                                                                                                               realTimePrice,
                                                                                                               ma30))

            if (yesterdayPrice != 0 and realTimePrice != 0 and yesterdayPrice <= ma60 and realTimePrice >= ma60):
                # 击穿60日均线，并上涨
                result.append(
                    unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '60up', yesterdayPrice, realTimePrice, ma60,
                                                                name).encode(
                        'gbk'))
                writeLog(unicode("[60up] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma60: {3}").format(code,
                                                                                                               yesterdayPrice,
                                                                                                               realTimePrice,
                                                                                                               ma60))

            if (yesterdayPrice != 0 and realTimePrice != 0 and yesterdayPrice <= ma120 and realTimePrice >= ma120):
                # 击穿120日均线，并上涨
                result.append(
                    unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '120up', yesterdayPrice, realTimePrice, ma120,
                                                                name).encode(
                        'gbk'))
                writeLog(unicode("[120up] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma120: {3}").format(code,
                                                                                                                 yesterdayPrice,
                                                                                                                 realTimePrice,
                                                                                                                 ma120))

            if (yesterdayPrice != 0 and realTimePrice != 0 and yesterdayPrice <= ma250 and realTimePrice >= ma250):
                # 击穿250日均线，并上涨
                result.append(
                    unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '250up', yesterdayPrice, realTimePrice, ma250,
                                                                name).encode(
                        'gbk'))
                writeLog(unicode("[250up] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma250: {3}").format(code,
                                                                                                                 yesterdayPrice,
                                                                                                                 realTimePrice,
                                                                                                                 ma250))

            if (yesterdayPrice != 0 and realTimePrice != 0 and yesterdayPrice >= ma5 and realTimePrice <= ma5):
                # 击穿5日均线，并下跌
                result.append(
                    unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '5down', yesterdayPrice, realTimePrice, ma5,
                                                                name).encode(
                        'gbk'))
                writeLog(unicode("[5down] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma5: {3}").format(code,
                                                                                                               yesterdayPrice,
                                                                                                               realTimePrice,
                                                                                                               ma5))

            if (yesterdayPrice != 0 and realTimePrice != 0 and yesterdayPrice >= ma10 and realTimePrice <= ma10):
                # 击穿10日均线，并下跌
                result.append(
                    unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '10down', yesterdayPrice, realTimePrice, ma10,
                                                                name).encode(
                        'gbk'))
                writeLog(unicode("[10down] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma10: {3}").format(code,
                                                                                                                 yesterdayPrice,
                                                                                                                 realTimePrice,
                                                                                                                 ma10))

            if (yesterdayPrice != 0 and realTimePrice != 0 and yesterdayPrice >= ma30 and realTimePrice <= ma30):
                # 击穿30日均线，并下跌
                result.append(
                    unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '30down', yesterdayPrice, realTimePrice, ma30,
                                                                name).encode(
                        'gbk'))
                writeLog(unicode("[30down] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma30: {3}").format(code,
                                                                                                                 yesterdayPrice,
                                                                                                                 realTimePrice,
                                                                                                                 ma30))

            if (yesterdayPrice != 0 and realTimePrice != 0 and yesterdayPrice >= ma60 and realTimePrice <= ma60):
                # 击穿60日均线，并下跌
                result.append(
                    unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '60down', yesterdayPrice, realTimePrice, ma60,
                                                                name).encode(
                        'gbk'))
                writeLog(unicode("[60down] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma60: {3}").format(code,
                                                                                                                 yesterdayPrice,
                                                                                                                 realTimePrice,
                                                                                                                 ma60))

            if (yesterdayPrice != 0 and realTimePrice != 0 and yesterdayPrice >= ma120 and realTimePrice <= ma120):
                # 击穿120日均线，并下跌
                result.append(
                    unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '120down', yesterdayPrice, realTimePrice, ma120,
                                                                name).encode(
                        'gbk'))
                writeLog(unicode("[120down] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma120: {3}").format(code,
                                                                                                                   yesterdayPrice,
                                                                                                                   realTimePrice,
                                                                                                                   ma120))

            if (yesterdayPrice != 0 and realTimePrice != 0 and yesterdayPrice >= ma250 and realTimePrice <= ma250):
                # 击穿250日均线，并下跌
                result.append(
                    unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '250down', yesterdayPrice, realTimePrice, ma250,
                                                                name).encode(
                        'gbk'))
                writeLog(unicode("[250down] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma250: {3}").format(code,
                                                                                                                   yesterdayPrice,
                                                                                                                   realTimePrice,
                                                                                                                   ma250))
            i = i + 1
        except Exception, e:
            writeErrorLog(unicode("checkAvgLineFailed, code:{0}, i:{1}, e:{2}").format(code, i, str(e)))
            i = i + 1
        time.sleep(0.5)

    saveFile(fileName, result)
    if (needSaveToDb):
        saveToDb(result)


def saveToDb(result):
    date = datetime.now()
    weekday = datetime.today().weekday()
    diff = 0 if weekday < 5 else weekday - 4
    date = (date - timedelta(days=diff)).strftime('%Y-%m-%d')

    insertSql = unicode("INSERT INTO s_avgline VALUES(%s,%s,%s,%s,%s,%s,%s,%s)")
    parameters = []
    for i in range(1, len(result)):
        data = result[i].replace("\n", "").decode('GBK').split(',')
        parameters.append(
            [data[0], date, data[1], int(time.time()), data[3], data[4], data[5], data[2]])
    batchInsert(insertSql, parameters)


def runTask():
    if datetime.today().weekday() < 5 and datetime.now().hour >= 20 and datetime.now().hour < 21 and datetime.now().minute < 20:
        sendMessageToMySelf(unicode("开始获取AvgLine数据"))
        begin = datetime.now()

        initMysql()
        stockList = getCodeList()
        checkAvgLine("avgline.csv", stockList, False)

        stockList = select(unicode("SELECT code,name from s_stock_info")) #loadJsonConfig(os.path.abspath(os.path.join(os.getcwd(), "../config/goodStockList.json")))
        checkAvgLine("avgline_all.csv", stockList)
        disconnect()

        end = datetime.now()
        sendMessageToMySelf(unicode("今日获取AvgLine的任务执行完毕,当前时间：{0}，执行用时：{1}").format(datetime.now(), end - begin))

    t = Timer(900, runTask)
    t.start()


def main(argv):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    runTask()


if __name__ == '__main__':
    main(sys.argv)
