# coding=utf-8

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))
from entity.ReminderInfo import ReminderInfo
import tushare as ts
from threading import Timer
from datetime import datetime, timedelta
from common.NumberHelper import getAboveNumber
from stock.StockInfo import getPE, getStockInfo
from common.FileHelper import writeFile
from wechat.weChatSender import sendMessageToBaby, sendMessageToMySelf
from common.LoggerHelper import writeDebugLog, writeInfoLog, writeWarningLog, writeErrorLog, writeLog
from db.MysqlUtil import initMysql, select, disconnect


def reminder():
    reminderCodeList = open(os.path.abspath(os.path.join(os.getcwd(), "../config/myreminder.csv")), 'r').readlines()

    dictReminder = {}
    for i in range(1, len(reminderCodeList)):
        infos = reminderCodeList[i].split(',')
        code = infos[0].strip().zfill(6)
        name = getPE(code)[0]
        maxPrice = float(infos[1])
        minPrice = float(infos[2])
        upPercent = float(infos[3])
        downPercent = float(infos[4])
        receiver = int(infos[5])
        sql = unicode(
            "SELECT changePercent,closePrice from s_stock where code='{0}' ORDER by date desc limit 30").format(code)
        data = select(sql)

        totalChangePercentBefore = 0
        yesterdayChangePercent = 0
        if data is not None:
            yesterdayChangePercent = data[0][0]
            for i in range(1, len(data)):
                changePercent = data[i][0]
                if (changePercent < 0):
                    break
                totalChangePercentBefore = totalChangePercentBefore + changePercent
            totalChangePercentBefore = totalChangePercentBefore + yesterdayChangePercent

        dictReminder[code] = ReminderInfo(maxPrice, minPrice, upPercent, downPercent, receiver, code, name,
                                          float(yesterdayChangePercent), float(totalChangePercentBefore))

    checkDict = {}  # 用于检查今天是否已经发送过某类信息
    date = datetime.now().strftime('%Y-%m-%d')
    result = []
    result.append(
        unicode("{0},{1},{2},{3},{4},{5}\n").format('股票代码', '股票涨到多少元', '股票跌到多少元', '股票涨幅超过多少（%）', '股票跌幅超过多少（%）',
                                                    '发给谁（0：期待，1：踏雪)').encode(
            'gbk'))

    while 1 == 1:
        if datetime.now().hour >= 16:
            # 更新提醒数据
            for i in range(1, len(reminderCodeList)):
                infos = reminderCodeList[i].split(',')
                code = infos[0].strip().zfill(6)
                maxPrice = float(infos[1])
                minPrice = float(infos[2])
                upPercent = float(infos[3])
                downPercent = float(infos[4])
                receiver = int(infos[5])

                stockInfo = getStockInfo(code)

                highPrice = float(stockInfo['highPrice'])
                closePrice = float(stockInfo['closePrice'])
                changePercent = float(stockInfo['changePercent'])
                newMinPrice = getAboveNumber(closePrice * 0.958)
                minPrice = minPrice if minPrice == -1 or changePercent <= 0 or newMinPrice <= minPrice else newMinPrice
                maxPrice = maxPrice if maxPrice == -1 or changePercent <= 0 else getAboveNumber(highPrice * 1.03)
                result.append(
                    unicode("{0},{1},{2},{3},{4},{5}\n").format(code, maxPrice, minPrice, upPercent, downPercent,
                                                                receiver).encode(
                        'gbk'))

            saveFileName = os.path.abspath(
                os.path.join(os.getcwd(), "../config/myreminder.csv"))
            writeFile(saveFileName, result)
            sendMessageToMySelf(unicode("止损表已经修正为以下值：{0}").format(result))
            break

        for key in dictReminder:
            df = ts.get_realtime_quotes(key)
            reminderInfo = dictReminder[key]

            price = float(df['price'].values[0])
            highPrice = float(df['high'].values[0])
            pre_close = float(df['pre_close'].values[0])
            todayUpPercent = 0 if price <= pre_close else round((price - pre_close) * 100 / pre_close, 2)
            todayDownPercent = 0 if price >= pre_close else round((price - pre_close) * 100 / pre_close, 2)
            highPercent = round((highPrice - pre_close) * 100 / pre_close, 2)
            currentPercent = round((price - pre_close) * 100 / pre_close, 2)

            # 今日最高价与当前价，跌幅超过了4.5
            if (highPercent > 0 and highPercent - currentPercent > 4.5):
                checkKey = unicode('{0}_{1}_{2}').format(date, key, 'highdown')
                if checkDict.has_key(checkKey) == False:
                    message = unicode(
                        '股票代码：{0}，名称：{1}，今日最高价：{2}, 当前价格为：{3}，最高涨幅：{4}%，当前涨幅为：{5}%，两者跌幅已经您预设的{6}%').format(key,
                                                                                                           reminderInfo.name,
                                                                                                           highPrice,
                                                                                                           price,
                                                                                                           highPercent,
                                                                                                           currentPercent,
                                                                                                           4.5,
                                                                                                           )
                    writeInfoLog(message)
                    sendMessageToMySelf(message) if reminderInfo.receiver == 1 else sendMessageToBaby(message)
                    checkDict[checkKey] = True

            # 当前涨幅已经超过预设的涨幅，目前为8%
            if (reminderInfo.upPercent != -1 and todayUpPercent >= reminderInfo.upPercent):
                checkKey = unicode('{0}_{1}_{2}').format(date, key, 'cup')
                if checkDict.has_key(checkKey) == False:
                    message = unicode('股票代码：{0}，名称：{4}，当前价格为：{1}，涨幅为：{2}%，已经超过您预设的{3}%').format(key, price,
                                                                                                todayUpPercent,
                                                                                                reminderInfo.upPercent,
                                                                                                reminderInfo.name)
                    writeInfoLog(message)
                    sendMessageToMySelf(message) if reminderInfo.receiver == 1 else sendMessageToBaby(message)
                    checkDict[checkKey] = True

            # 昨天和当前总跌幅已经超过25%
            if (todayUpPercent + reminderInfo.totalChangePercentLast30Days >= 25):
                checkKey = unicode('{0}_{1}_{2}').format(date, key, 'tup')
                if checkDict.has_key(checkKey) == False:
                    message = unicode('股票代码：{0}，名称：{4}，当前价格为：{1}，累计涨幅为：{2}%，已经超过您预设的{3}%').format(key, price,
                                                                                                  todayUpPercent + reminderInfo.totalChangePercentLast30Days,
                                                                                                  25,
                                                                                                  reminderInfo.name)
                    writeInfoLog(message)
                    sendMessageToMySelf(message) if reminderInfo.receiver == 1 else sendMessageToBaby(message)
                    checkDict[checkKey] = True

            # 当前跌幅已经超过预设的跌幅，目前为4.2%
            if (reminderInfo.downPercent != -1 and todayDownPercent <= -reminderInfo.downPercent):
                checkKey = unicode('{0}_{1}_{2}').format(date, key, 'cdown')
                if checkDict.has_key(checkKey) == False:
                    message = unicode('股票代码：{0}，名称：{4}，当前价格为：{1}，跌幅为：{2}%，已经低于您预设的{3}%').format(key, price,
                                                                                                todayDownPercent,
                                                                                                -reminderInfo.downPercent,
                                                                                                reminderInfo.name)
                    writeInfoLog(message)
                    sendMessageToMySelf(message) if reminderInfo.receiver == 1 else sendMessageToBaby(message)
                    checkDict[checkKey] = True

            # 昨天和当前总跌幅已经超过4.2%
            if (todayDownPercent + reminderInfo.yesterdayChangePercent <= -4.2):
                checkKey = unicode('{0}_{1}_{2}').format(date, key, 'tdown')
                if checkDict.has_key(checkKey) == False:
                    message = unicode('股票代码：{0}，名称：{4}，当前价格为：{1}，昨日和当前总跌幅为：{2}%，已经低于您预设的{3}%').format(key, price,
                                                                                                      todayDownPercent + reminderInfo.yesterdayChangePercent,
                                                                                                      -4.2,
                                                                                                      reminderInfo.name)
                    writeInfoLog(message)
                    sendMessageToMySelf(message) if reminderInfo.receiver == 1 else sendMessageToBaby(message)
                    checkDict[checkKey] = True

        time.sleep(1)


def runTask():
    if (datetime.now().hour >= 9 and datetime.now().hour < 10 and datetime.now().minute <= 20):
        begin = datetime.now()
        sendMessageToMySelf(unicode("启动今日涨跌幅提醒程序"))

        initMysql()
        reminder()
        disconnect()

        end = datetime.now()
        sendMessageToMySelf(unicode("今日涨跌幅提醒程序运行结束,当前时间：{0}，执行用时：{1}").format(datetime.now(), end - begin))

    t = Timer(900, runTask)
    t.start()


def main(argv):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    runTask()


if __name__ == '__main__':
    main(sys.argv)
