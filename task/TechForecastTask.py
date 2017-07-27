# coding=utf-8
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))

from common.JsonHelper import loadJsonConfig
from db.MysqlUtil import initMysql, execute, select, batchInsert, disconnect

import time
from threading import Timer
from wechat.weChatSender import sendMessageToMySelf
from datetime import datetime, timedelta
from common.LoggerHelper import writeErrorLog, writeLog


def startForecast():
    date = datetime.now().strftime('%Y-%m-%d')
    weekday = datetime.today().weekday()
    if weekday == 5 or weekday == 6:
        return

    tomorrow = (datetime.now() + timedelta(days=(3 if weekday == 4 else 1))).strftime('%Y-%m-%d')

    stockList = loadJsonConfig(os.path.abspath(os.path.join(os.getcwd(), "../config/goodStockList.json")))
    i = 0
    while i < len(stockList):
        code = stockList[i][0]
        checkMACD(code, tomorrow)
        i = i + 1


def checkMACD(code, tomorrow):
    sql = unicode(
        "SELECT dif,macd,dea,date from s_stock_tech where code='{0}' and date<'{1}' ORDER by date desc limit 5").format(
        code, tomorrow)
    data = select(sql)

    if data is None or len(data) < 5:
        return

    isGoldFork = isMACDGoldFork(data)  # 黄金叉
    isBottomFallAway = isMACDBottomFallAway(data)  # 底背离

    needBuy = isGoldFork or isBottomFallAway
    buyRemark = unicode("可以考虑买入，原因：{0}，{1}").format("出现黄金叉" if isGoldFork else "", "出现底背离" if isBottomFallAway else "")

    isDeadFork = isMACDDeadFork(data)  # 死叉
    isTopFallAway = isMACDTopFallAway(data)  # 顶背离
    needSell = isDeadFork or isTopFallAway
    sellRemark = unicode("可以考虑卖出，原因：{0}，{1}").format("出现死叉" if isDeadFork else "", "出现顶背离" if isTopFallAway else "")

    writeLog(unicode("[买入卖出信号] code:{0}, date:{1}, remark:{2}").format(code, tomorrow, buyRemark if needBuy else (
        sellRemark if needSell else "")))


# MACD柱线递增
def isMACDUp(data):
    result = True
    for i in range(len(data) - 3, 0):
        if (data[i][1] < data[i + 1][1]):
            result = False
            break
    return result


# MACD柱线递减
def isMACDUp(data):
    result = True
    for i in range(len(data) - 3, 0):
        if (data[i][1] > data[i + 1][1]):
            result = False
            break
    return result


# 判断底背离
def isMACDBottomFallAway(data):
    result = True
    i = len(data) - 2
    while i >= 1:
        if (data[i][0] > data[i + 1][0]):
            result = False
            break
        i = i - 1

    if result == True:  # 说明前面的DIF一直是递减的
        if (data[0][0] >= data[1][0]):  # 说明最后一天的DIF没有继续递减（相等或者增加），则认为是底背离
            return True
        return False

    return False


# 判断顶背离
def isMACDTopFallAway(data):
    result = True
    i = len(data) - 2
    while i >= 1:
        if (data[i][0] < data[i + 1][0]):
            result = False
            break
        i = i - 1

    if result == True:  # 说明前面的DIF一直是递增的
        if (data[0][0] <= data[1][0]):  # 说明最后一天的DIF没有继续递增（相等或者减少），则认为是顶背离
            return True
        return False

    return False


# 判断死叉
def isMACDDeadFork(data):
    try:
        for i in range(0, len(data)):
            MACD = data[0][1]
            yesterdayMACD = data[1][1]

            # 死叉：1. 前一天macd>=0,今天macd<=0
            if (yesterdayMACD >= 0 and MACD <= 0):
                return True
            return False
    except Exception, e:
        writeErrorLog(unicode("[买入卖出信号异常] data:{0}, e:{1}").format(data, e))
        return False


# 判断黄金叉
def isMACDGoldFork(data):
    try:
        for i in range(0, len(data)):
            MACD = data[0][1]
            yesterdayMACD = data[1][1]

            # 黄金叉：1. 前一天macd<=0,今天macd>=0  2. macd指标在0轴上方（此条件暂时忽略）
            if (yesterdayMACD <= 0 and MACD >= 0):
                return True
            return False
    except Exception, e:
        writeErrorLog(unicode("[买入卖出信号异常] data:{0}, e:{1}").format(data, e))
        return False


def runTask():
    if datetime.today().weekday() < 5 and datetime.now().hour >= 22 and datetime.now().hour < 23 and datetime.now().minute < 20:
        sendMessageToMySelf(unicode("开始进行明日技术指标预测"))
        begin = datetime.now()

        initMysql()

        disconnect()

        end = datetime.now()
        sys.setdefaultencoding('utf-8')
        sendMessageToMySelf(unicode("明日技术指标预测的任务执行完毕,当前时间：{0}，执行用时：{1}").format(datetime.now(), end - begin))

    t = Timer(900, runTask)
    t.start()


def main(argv):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    # runTask()
    initMysql()
    startForecast()


if __name__ == '__main__':
    main(sys.argv)
