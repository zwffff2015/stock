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


def reminder():
    reminderCodeList = open(os.path.abspath(os.path.join(os.getcwd(), "../config/reminder.csv")), 'r').readlines()

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
        dictReminder[code] = ReminderInfo(maxPrice, minPrice, upPercent, downPercent, receiver, code, name)

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
                name = getPE(code)[0]
                maxPrice = float(infos[1])
                minPrice = float(infos[2])
                upPercent = float(infos[3])
                downPercent = float(infos[4])
                receiver = int(infos[5])

                stockInfo = getStockInfo(code)
                if stockInfo is None:
                    continue

                highPrice = float(stockInfo['highPrice'])
                closePrice = float(stockInfo['closePrice'])
                changePercent = float(stockInfo['changePercent'])
                newMinPrice = getAboveNumber(closePrice * 0.97)
                minPrice = minPrice if minPrice == -1 or changePercent <= 0 or newMinPrice <= minPrice else newMinPrice
                maxPrice = maxPrice if maxPrice == -1 or changePercent <= 0 else getAboveNumber(highPrice * 1.03)
                result.append(
                    unicode("{0},{1},{2},{3},{4},{5}\n").format(code, maxPrice, minPrice, upPercent, downPercent,
                                                                receiver).encode(
                        'gbk'))

            saveFileName = os.path.abspath(
                os.path.join(os.getcwd(), "../config/reminder.csv"))
            writeFile(saveFileName, result)
            writeLog(unicode("止损表已经修正为以下值：{0}").format(result))
            sendMessageToMySelf(unicode("止损表已经修正为以下值：{0}").format(result))
            break

        for key in dictReminder:
            df = ts.get_realtime_quotes(key)
            reminderInfo = dictReminder[key]

            price = float(df['price'].values[0])
            pre_close = float(df['pre_close'].values[0])
            currentUpPercent = 0 if price <= pre_close else round((price - pre_close) * 100 / pre_close, 2)
            currentDownPercent = 0 if price >= pre_close else round((price - pre_close) * 100 / pre_close, 2)

            print key, price, reminderInfo.maxPrice, reminderInfo.minPrice, currentUpPercent, currentDownPercent
            if (price != 0 and reminderInfo.maxPrice != -1 and price >= reminderInfo.maxPrice):
                checkKey = unicode('{0}_{1}_{2}').format(date, key, 'max')
                if checkDict.has_key(checkKey) == False:
                    message = unicode('股票代码：{0}，名称：{3}，当前价格为：{1}，已经超过您预设的{2}').format(key, price,
                                                                                      reminderInfo.maxPrice,
                                                                                      reminderInfo.name)
                    writeInfoLog(message)
                    sendMessageToMySelf(message) if reminderInfo.receiver == 1 else sendMessageToBaby(message)
                    checkDict[checkKey] = True

            if (price != 0 and reminderInfo.minPrice != -1 and price <= reminderInfo.minPrice):
                checkKey = unicode('{0}_{1}_{2}').format(date, key, 'min')
                if checkDict.has_key(checkKey) == False:
                    message = unicode('股票代码：{0}，名称：{3}，当前价格为：{1}，已经低于您预设的{2}').format(key, price,
                                                                                      reminderInfo.minPrice,
                                                                                      reminderInfo.name)
                    writeInfoLog(message)
                    sendMessageToMySelf(message) if reminderInfo.receiver == 1 else sendMessageToBaby(message)
                    checkDict[checkKey] = True

            if (price != 0 and reminderInfo.upPercent != -1 and currentUpPercent >= reminderInfo.upPercent):
                checkKey = unicode('{0}_{1}_{2}').format(date, key, 'up')
                if checkDict.has_key(checkKey) == False:
                    message = unicode('股票代码：{0}，名称：{4}，当前价格为：{1}，涨幅为：{2}%，已经超过您预设的{3}%').format(key, price,
                                                                                                currentUpPercent,
                                                                                                reminderInfo.upPercent,
                                                                                                reminderInfo.name)
                    writeInfoLog(message)
                    sendMessageToMySelf(message) if reminderInfo.receiver == 1 else sendMessageToBaby(message)
                    checkDict[checkKey] = True

            if (price != 0 and reminderInfo.downPercent != -1 and currentDownPercent <= -reminderInfo.downPercent):
                checkKey = unicode('{0}_{1}_{2}').format(date, key, 'down')
                if checkDict.has_key(checkKey) == False:
                    message = unicode('股票代码：{0}，名称：{4}，当前价格为：{1}，跌幅为：{2}%，已经低于您预设的{3}%').format(key, price,
                                                                                                currentDownPercent,
                                                                                                -reminderInfo.downPercent,
                                                                                                reminderInfo.name)
                    writeInfoLog(message)
                    sendMessageToMySelf(message) if reminderInfo.receiver == 1 else sendMessageToBaby(message)
                    checkDict[checkKey] = True

        time.sleep(1)


def runTask():
    if datetime.today().weekday() < 5 and datetime.now().hour >= 9 and datetime.now().hour < 10 and datetime.now().minute <= 20:
        begin = datetime.now()
        sendMessageToMySelf(unicode("启动今日提醒程序"))

        reminder()

        end = datetime.now()
        sendMessageToMySelf(unicode("今日提醒程序运行结束,当前时间：{0}，执行用时：{1}").format(datetime.now(), end - begin))

    t = Timer(900, runTask)
    t.start()


def main(argv):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    runTask()


if __name__ == '__main__':
    main(sys.argv)
