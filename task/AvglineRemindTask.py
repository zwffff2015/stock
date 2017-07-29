# coding=utf-8

'''
用于判断当前价格是否突破了N日均线上涨或者下跌
'''

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))

from threading import Timer
from datetime import datetime, timedelta
from wechat.weChatSender import sendMessageToBaby, sendMessageToMySelf
from db.MysqlUtil import initMysql, execute, select, batchInsert, disconnect
from common.LoggerHelper import writeLog, writeErrorLog
from stock.StockInfo import getNPrice
from api.tushareApi import getRealTimeData
from common.JsonHelper import loadJsonConfig
import time


def checkAvgline(stockList):
    date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    dictLastRemindPrice = {}
    while 1 == 1:
        if datetime.now().hour >= 16:
            # 今日提醒程序结束
            return

        for stock in stockList:
            code = stock[0]
            name = stock[1]
            try:
                sql = unicode(
                    "SELECT code,date,MA5,MA10,MA20,MA30,MA60,MA120,MA250 from s_stock where code='{0}' and date='{1}'").format(
                    code, date)
                data = select(sql)
                if (len(data) <= 0):
                    writeLog(unicode("没有获取到均值数据, code: {0}, date: {1}").format(code, date))
                    continue

                ma5 = data[0][2]
                ma10 = data[0][3]
                ma30 = data[0][5]
                ma60 = data[0][6]
                ma120 = data[0][7]
                ma250 = data[0][8]

                lastPrice = getNPrice(code, 1, 'high') if not dictLastRemindPrice.has_key(
                    code) else dictLastRemindPrice.get(code)
                realTimePrice = float(getRealTimeData(code))
                print name, lastPrice, realTimePrice

                if (lastPrice != 0 and realTimePrice != 0 and lastPrice <= ma5 and realTimePrice >= ma5):
                    # 击穿5日均线，并上涨
                    sendMessageToMySelf(
                        unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '5up', lastPrice, realTimePrice, ma5,
                                                                    name))
                    writeLog(
                        unicode("[remind_5up] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma5: {3}").format(code,
                                                                                                                   lastPrice,
                                                                                                                   realTimePrice,
                                                                                                                   ma5))

                if (lastPrice != 0 and realTimePrice != 0 and lastPrice <= ma10 and lastPrice >= ma10):
                    # 击穿10日均线，并上涨
                    sendMessageToMySelf(
                        unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '10up', lastPrice, realTimePrice, ma10,
                                                                    name))
                    writeLog(
                        unicode("[remind_10up] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma10: {3}").format(
                            code,
                            lastPrice,
                            realTimePrice,
                            ma10))

                if (lastPrice != 0 and realTimePrice != 0 and lastPrice <= ma30 and realTimePrice >= ma30):
                    # 击穿30日均线，并上涨
                    sendMessageToMySelf(
                        unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '30up', lastPrice, realTimePrice, ma30,
                                                                    name))
                    writeLog(
                        unicode("[remind_30up] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma30: {3}").format(
                            code,
                            lastPrice,
                            realTimePrice,
                            ma30))

                if (lastPrice != 0 and realTimePrice != 0 and lastPrice <= ma60 and realTimePrice >= ma60):
                    # 击穿60日均线，并上涨
                    sendMessageToMySelf(
                        unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '60up', lastPrice, realTimePrice, ma60,
                                                                    name))
                    writeLog(
                        unicode("[remind_60up] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma60: {3}").format(
                            code,
                            lastPrice,
                            realTimePrice,
                            ma60))

                if (lastPrice != 0 and realTimePrice != 0 and lastPrice <= ma120 and realTimePrice >= ma120):
                    # 击穿120日均线，并上涨
                    sendMessageToMySelf(
                        unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '120up', lastPrice, realTimePrice, ma120,
                                                                    name))
                    writeLog(
                        unicode("[remind_120up] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma120: {3}").format(
                            code,
                            lastPrice,
                            realTimePrice,
                            ma120))

                if (lastPrice != 0 and realTimePrice != 0 and lastPrice <= ma250 and realTimePrice >= ma250):
                    # 击穿250日均线，并上涨
                    sendMessageToMySelf(
                        unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '250up', lastPrice, realTimePrice, ma250,
                                                                    name))
                    writeLog(
                        unicode("[remind_250up] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma250: {3}").format(
                            code,
                            lastPrice,
                            realTimePrice,
                            ma250))

                if (lastPrice != 0 and realTimePrice != 0 and lastPrice >= ma5 and realTimePrice <= ma5):
                    # 击穿5日均线，并下跌
                    sendMessageToMySelf(
                        unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '5down', lastPrice, realTimePrice, ma5,
                                                                    name))
                    writeLog(
                        unicode("[remind_5down] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma5: {3}").format(
                            code,
                            lastPrice,
                            realTimePrice,
                            ma5))

                if (lastPrice != 0 and realTimePrice != 0 and lastPrice >= ma10 and realTimePrice <= ma10):
                    # 击穿10日均线，并下跌
                    sendMessageToMySelf(
                        unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '10down', lastPrice, realTimePrice, ma10,
                                                                    name))
                    writeLog(
                        unicode("[remind_10down] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma10: {3}").format(
                            code,
                            lastPrice,
                            realTimePrice,
                            ma10))

                if (lastPrice != 0 and realTimePrice != 0 and lastPrice >= ma30 and realTimePrice <= ma30):
                    # 击穿30日均线，并下跌
                    sendMessageToMySelf(
                        unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '30down', lastPrice, realTimePrice, ma30,
                                                                    name))
                    writeLog(
                        unicode("[remind_30down] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma30: {3}").format(
                            code,
                            lastPrice,
                            realTimePrice,
                            ma30))

                if (lastPrice != 0 and realTimePrice != 0 and lastPrice >= ma60 and realTimePrice <= ma60):
                    # 击穿60日均线，并下跌
                    sendMessageToMySelf(
                        unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '60down', lastPrice, realTimePrice, ma60,
                                                                    name))
                    writeLog(
                        unicode("[remind_60down] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma60: {3}").format(
                            code,
                            lastPrice,
                            realTimePrice,
                            ma60))

                if (lastPrice != 0 and realTimePrice != 0 and lastPrice >= ma120 and realTimePrice <= ma120):
                    # 击穿120日均线，并下跌
                    sendMessageToMySelf(
                        unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '120down', lastPrice, realTimePrice, ma120,
                                                                    name))
                    writeLog(
                        unicode(
                            "[remind_120down] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma120: {3}").format(
                            code,
                            lastPrice,
                            realTimePrice,
                            ma120))

                if (lastPrice != 0 and realTimePrice != 0 and lastPrice >= ma250 and realTimePrice <= ma250):
                    # 击穿250日均线，并下跌
                    sendMessageToMySelf(
                        unicode("{0},{5},{1},{2},{3},{4}\n").format(code, '250down', lastPrice, realTimePrice, ma250,
                                                                    name))
                    writeLog(
                        unicode(
                            "[remind_250down] code：{0}, yesterdayPrice: {1}, realTimePrice: {2}, ma250: {3}").format(
                            code,
                            lastPrice,
                            realTimePrice,
                            ma250))

                dictLastRemindPrice[code] = realTimePrice
            except Exception, e:
                writeErrorLog(unicode("remind_checkAvgLineFailed, code:{0}, e:{1}").format(code, str(e)))

        time.sleep(1)


def runTask():
    if datetime.today().weekday() < 5 and datetime.now().hour >= 9 and datetime.now().hour < 10 and datetime.now().minute <= 20:
        begin = datetime.now()
        sendMessageToMySelf(unicode("启动均线数据提醒"))

        initMysql()
        stockList = loadJsonConfig(os.path.abspath(os.path.join(os.getcwd(), "../config/avglineReminder.json")))
        checkAvgline(stockList)
        disconnect()

        end = datetime.now()
        sendMessageToMySelf(unicode("今日均线数据提醒程序运行结束,当前时间：{0}，执行用时：{1}").format(datetime.now(), end - begin))

    t = Timer(900, runTask)
    t.start()


def main(argv):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    runTask()


if __name__ == '__main__':
    main(sys.argv)
