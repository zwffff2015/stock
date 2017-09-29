# coding=utf-8

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))

import random
import time
import shutil
import json

from api.tushareApi import getHistoryData
from common.FileHelper import saveFile, writeFile
from common.HttpHelper import httpGet
from stock.StockInfo import getPE
from stock.StockInfo import getPEG, getShAvgPe, getSzAvgPe
from common.JsonHelper import loadJsonConfig
from datetime import datetime, timedelta
from threading import Timer
from db.MysqlUtil import initMysql, execute, select, batchInsert, disconnect
from wechat.weChatSender import sendMessageToMySelf, sendMessageToBaby
from common.LoggerHelper import writeLog, writeWarningLog, writeErrorLog, writeDebugLog
from common.Logger import Logger


def getListData(code, page):
    url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=" + code + "&sty=FCOIATA&sortType=I&sortRule=1&page=" + str(
        page) + "&pageSize=20&js=var%20quote_123%3d{rank:[(x)],pages:(pc)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.148125620" + str(
        random.randint(1000000, 9999999))

    res = httpGet(url).decode("utf-8")
    # print res
    index = res.find("=")
    if (index < 0):
        return

    res = res[14:].replace("rank", "\"rank\"").replace("pages", "\"pages\"")
    # print res
    jo = json.loads(res)
    return jo


def getStockListData(index, code, avgPE):
    page = 1
    listData = getListData(code, page)
    if listData is None:
        writeWarningLog("没有获取到第" + str(page) + "页的股票数据")
        return

    result = []
    dicDuplicate = {}
    result.append(
        unicode("{0},{1},{2},{3},{4},{5},{6},{7},{8}\n").format("代码", "名称", "PE", "E2017", "E2018", "E2019", "复合", "排名",
                                                                "PEG").encode('gbk'))

    needFetchNextPage = handleListData(listData["rank"], avgPE, result, dicDuplicate)

    totalPages = listData["pages"]
    if needFetchNextPage is None:
        for i in range(2, totalPages + 1):
            listData = getListData(code, i)
            if listData is None:
                writeWarningLog("没有获取到第" + str(i) + "页的股票数据")
                return

            needFetchNextPage = handleListData(listData["rank"], avgPE, result, dicDuplicate)
            if (needFetchNextPage == -1):
                break;

    saveFile("bigData_" + code + ".csv", result)
    saveToDb(index + 1, result)


def handleListData(listData, avgPE, result, dicDuplicate):
    i = 0
    while i < len(listData):
        writeDebugLog(unicode("获取股票数据, {0}").format(listData[i]))
        info = listData[i].strip().split(",")
        if (len(info) < 25):
            i = i + 1
            continue

        code = info[1]
        name = info[2]
        pe = info[24]
        writeDebugLog(unicode("获取股票数据, code: {0} , name:{1}, pe: {2}, avgPE: {3}").format(code, name, pe, avgPE))

        try:
            if (float(pe) > float(avgPE)):
                return -1  # 如果已经大于当前平均PE，则不再继续获取

            pegData = getPEG(code)
            # print pegData[0],pegData[1]
            if not dicDuplicate.has_key(code):
                result.append(
                    unicode("{0},{1},{2},{3},{4},{5},{6},{7},{8}\n").format(code, name, pe, pegData[3], pegData[4],
                                                                            pegData[5],
                                                                            pegData[2], pegData[0], pegData[1]).encode(
                        'gbk'))
            i = i + 1
        except Exception, e:
            writeErrorLog(unicode("getPEGFailed, code: {0} ,e: {1}").format(code, str(e)))
        time.sleep(0.2)


def handleSpecifiedStock(codeList):
    result = []
    result.append(
        unicode("{0},{1},{2},{3},{4},{5},{6},{7},{8}\n").format("代码", "名称", "PE", "E2017", "E2018", "E2019", "复合", "排名",
                                                                "PEG").encode('gbk'))
    for i in range(0, len(codeList)):
        code = codeList[i]
        try:
            peInfo = getPE(code)
            pegData = getPEG(code)

            writeDebugLog(unicode("获取指定股票数据, code: {0} , i:{1}, info: {2}").format(code, i, peInfo))
            result.append(
                unicode("{0},{1},{2},{3},{4},{5},{6},{7},{8}\n").format(code, peInfo[0], peInfo[1], pegData[3],
                                                                        pegData[4],
                                                                        pegData[5], pegData[2], pegData[0],
                                                                        pegData[1]).encode('gbk'))
            time.sleep(0.2)
        except Exception, e:
            logger.exception(unicode("code: {0} , e: {1}".format(code, str(e))))

    return result


def getStockListByPE(peDiff):
    codeList = ['C._A', 'C.2', 'C._SZAME', 'C.13', 'C.80']  # 沪深A,上A,深A,中小板,创业板
    avgPE = [getShAvgPe(), getShAvgPe()] + getSzAvgPe()
    for i in range(0, len(codeList)):
        getStockListData(i, codeList[i], avgPE[i] + peDiff)


def getSh50():
    sh50 = loadJsonConfig(os.path.abspath(os.path.join(os.getcwd(), "../config/sh50.json")))
    sh50Result = handleSpecifiedStock(sh50)
    saveFile("sh50.csv", sh50Result)
    saveToDb(6, sh50Result)


def getSh300():
    sh300 = loadJsonConfig(os.path.abspath(os.path.join(os.getcwd(), "../config/sh300.json")))
    sh300Result = handleSpecifiedStock(sh300)
    saveFile("sh300.csv", sh300Result)
    saveToDb(7, sh300Result)


def getMSCI():
    msci = loadJsonConfig(os.path.abspath(os.path.join(os.getcwd(), "../config/msci.json")))
    msciResult = handleSpecifiedStock(msci)
    saveFile("msci.csv", msciResult)
    saveToDb(8, msciResult)


# type: 1=沪深A PE<=上证平均市盈率，2：沪A，3：深A，4：中小板，5：创业板，6：上证50，7：沪深300，8：msci
def saveToDb(type, result):
    initMysql()
    date = datetime.now().strftime('%Y-%m-%d')
    insertSql = unicode("INSERT INTO b_peg VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
    parameters = []
    for i in range(1, len(result)):
        data = result[i].replace("\n", "").decode('GBK').split(',')
        parameters.append(
            [data[0], date, data[1], int(time.time()), data[2], data[3], data[4], data[5], data[6], data[7],
             data[8],
             type])
    batchInsert(insertSql, parameters)
    disconnect()


def updateLatestGoodStockListToConfig():
    selectSql = unicode("SELECT  DISTINCT code,name from b_peg where date=(SELECT max(date) FROM b_peg)")
    result = select(selectSql)

    dictData = {}
    data = []
    for row in result:
        code = row[0].zfill(6)
        if code not in dictData:
            dictData[code] = 1
            data.append([code, row[1]])

    saveFileName = os.path.abspath(
        os.path.join(os.getcwd(), "../config/goodStockList.json"))
    backupFileName = os.path.abspath(
        os.path.join(os.getcwd(), "../backup/goodStockList_" + datetime.now().strftime('%Y-%m-%d') + ".json"))
    if os.path.exists(saveFileName):
        shutil.move(saveFileName, backupFileName)

    writeFile(saveFileName, json.dumps(data))


def updateNewGoodList():
    weekday = datetime.now().weekday()
    lastSaturday = (datetime.now() + timedelta(days=(-2 - weekday))).strftime('%Y-%m-%d')
    saturday = (datetime.now() + timedelta(days=(5 - weekday))).strftime('%Y-%m-%d')

    for i in range(1, 9):
        lastWeekSql = unicode("select code from b_peg where dataType={0} and date='{1}'").format(i, lastSaturday)
        oldData = select(lastWeekSql)

        dic = {}
        for item in oldData:
            dic[item[0]] = 1

        newList = select(
            unicode("select code,name,pe,peg from b_peg where dataType={0} and date='{1}'").format(i, saturday))

        result = []
        result.append(
            unicode("{0},{1},{2},{3}\n").format("代码", "名称", "PE", "PEG").encode('gbk'))

        for item in newList:
            if item[0] not in dic:
                result.append(
                    unicode("{0},{1},{2},{3}\n").format(item[0], item[1], item[2], item[3]).encode('gbk'))
        saveFile("newGoodList_{0}.csv".format(i), result)


# 此处有问题了，需要修正来查找新的股票
def updateNewList():
    oldList = loadJsonConfig(os.path.abspath(
        os.path.join(os.getcwd(), "../backup/goodStockList_" + datetime.now().strftime('%Y-%m-%d') + ".json")))
    dic = {}
    for item in oldList:
        dic[item[0]] = 1

    stockList = select(unicode(
        "SELECT code,name from s_stock_info"))  # loadJsonConfig(os.path.abspath(os.path.join(os.getcwd(), "../config/goodStockList.json")))
    newList = []
    for item in stockList:
        if item[0] not in dic:
            newList.append([item[0], item[1]])

    saveFileName = os.path.abspath(
        os.path.join(os.getcwd(), "../config/newStockList.json"))
    writeFile(saveFileName, json.dumps(newList))


def getStockHistoryInfo():
    stockList = loadJsonConfig(os.path.abspath(os.path.join(os.getcwd(), "../config/newStockList.json")))
    startDate = '2014-07-01'
    endDate = '2017-07-06'
    writeLog(unicode("开始查询股票历史行情数据，股票池：{0}").format(stockList))
    for stock in stockList:
        code = stock[0]
        data = getHistoryData(code, startDate, endDate)

        insertSql = unicode(
            "INSERT INTO s_stock VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
        parameters = []
        for i in range(0, len(data)):
            date = data.index[i]
            open = data.iloc[i]['open']
            close = data.iloc[i]['close']
            high = data.iloc[i]['high']
            low = data.iloc[i]['low']
            volume = data.iloc[i]['volume']
            changePercent = data.iloc[i]['p_change']
            turnover = data.iloc[i]['turnover']
            parameters.append(
                [code, date, -1, -1, -1, volume, -1, high, low, open, close, changePercent, -1, turnover, -1, -1, -1,
                 -1, -1, -1, -1, int(time.mktime(time.strptime(date, '%Y-%m-%d'))), -1, -1, -1, -1, -1, -1, -1, -1, -1,
                 -1])

        batchInsert(insertSql, parameters)
    writeLog(unicode("查询股票历史行情数据完成"))


def runTask():
    # 周六执行每周任务
    if datetime.today().weekday() == 5 and datetime.now().hour >= 9 and datetime.now().hour < 10 and datetime.now().minute < 20:
        begin = datetime.now()

        # 执行每周任务
        initMysql()
        getStockListByPE(0)
        getSh50()
        getSh300()
        getMSCI()
        updateLatestGoodStockListToConfig()
        updateNewList()
        updateNewGoodList()
        # getStockHistoryInfo()
        disconnect()

        end = datetime.now()
        sendMessageToMySelf(unicode("本周获取PEG的任务执行完毕,当前时间：{0}，执行用时：{1}").format(datetime.now(), end - begin))

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
