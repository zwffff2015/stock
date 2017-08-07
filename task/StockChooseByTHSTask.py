# coding=utf-8

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))

import random
import time
import shutil
import json
import re

from api.tushareApi import getHistoryData
from common.FileHelper import saveFile, writeFile
from common.HttpHelper import httpGet, getEncoding
from stock.StockInfo import getPEGByWC, getRankPeg, getPEByWC, getShAvgPe, getSzAvgPe
from common.JsonHelper import loadJsonConfig
from datetime import datetime, timedelta
from threading import Timer
from db.MysqlUtil import initMysql, execute, select, batchInsert, disconnect
from wechat.weChatSender import sendMessageToMySelf, sendMessageToBaby
from common.LoggerHelper import writeLog, writeWarningLog, writeErrorLog, writeDebugLog

'''
# 从问财网抓取行情列表数据。type：['A%E8%82%A1','%E4%B8%8A%E8%AF%81A%E8%82%A1','%E6%B7%B1%E8%AF%81A%E8%82%A1','%E4%B8%AD%E5%B0%8F%E6%9D%BF','%E5%88%9B%E4%B8%9A%E6%9D%BF']  A股，上证A股，深证A股,中小板，创业板
def getListData(type, page):
    referer = "http://www.iwencai.com/stockpick/search?ts=1&f=1&qs=stockhome_topbar_click&w=pe%3E0;pe%3C37.5;%20a%E8%82%A1"
    url = "http://www.iwencai.com/stockpick/cache?token=" + type + "&p=" + str(
        page) + "&perpage=70&sort={%22column%22:4,%22order%22:%22ASC%22}&showType=[%22%22,%22%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onList%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22]"

    res = httpGet(url, {"Referer": referer})
    print ""


def getStockListByPE(peDiff):
    typeList = ['de0a1053bfa2e1e3afa3e2b94bc1f573', 'ece2a10b561aae94e51581913a375d13',
                '1d7712dfd2818093adeef52b53ff969f',
                '038162f763b0e014221d0485b3a74cf1', '5fabcf09ba435960864a450532652c26']  # A股，上证A股，深证A股,中小板，创业板
    avgPE = [getShAvgPe(), getShAvgPe()] + getSzAvgPe()
    for i in range(0, len(typeList)):
        # getStockListData(i, codeList[i], avgPE[i] + peDiff)
        getListData(typeList[i], 1)
'''


def getListData(type, page):
    url = "http://q.10jqka.com.cn/index/index/board/" + type + "/field/syl/order/asc/page/" + str(page) + "/ajax/1/"

    res = httpGet(url, {"Accept-Encoding": "gzip, deflate, sdch", "Accept-Language": "zh-CN,zh;q=0.8"})
    try:
        res = res.decode(getEncoding(res))

        columnNames = ['number', 'code', 'name', 'price', 'changepercent', 'changeamount', 'changerate',
                       'turnoverratio',
                       'QRR', 'zf', 'amount', 'liutonggu', 'liutongshizhi', 'pe']
        listData = []

        pattern = re.compile(r'<tr[^>]*?>([\s\S]*?)</tr>')
        trData = pattern.findall(res)
        for tr in trData:
            pattern = re.compile(r'<td.*?>(.*?)</td>')
            tdData = pattern.findall(tr)
            if len(tdData) <= 0:
                continue

            dict = {}
            for i in range(1, len(tdData) - 1):
                if i <= 2:
                    pattern = re.compile(r'<a.*?>(.*?)</a>')
                    aData = pattern.findall(tdData[i])
                    dict[columnNames[i]] = aData[0]
                else:
                    dict[columnNames[i]] = tdData[i]
            listData.append(dict)

        return listData
    except Exception, e:
        print e, res


def getStockListData(index, type, avgPE):
    page = 1
    listData = getListData(type, page)
    if listData is None:
        writeWarningLog("没有获取到第" + str(page) + "页的股票数据")
        return

    result = []
    dicDuplicate = {}
    result.append(
        unicode("{0},{1},{2},{3},{4},{5},{6},{7}\n").format("代码", "名称", "PE", "PEG", "预测PEG", "No1(代码:名称:PEG)",
                                                            "No2(代码:名称:PEG)", "No3(代码:名称:PEG)").encode('gbk'))

    needFetchNextPage = handleListData(listData, avgPE, result, dicDuplicate)

    if needFetchNextPage is None:
        for i in range(2, 200):
            listData = getListData(type, i)
            if listData is None:
                writeWarningLog("没有获取到第" + str(i) + "页的股票数据")
                return

            needFetchNextPage = handleListData(listData, avgPE, result, dicDuplicate)
            if (needFetchNextPage == -1):
                break;

    saveFile("bigData_" + type + ".csv", result)
    saveToDb(index + 1, result)


def handleListData(listData, avgPE, result, dicDuplicate):
    i = 0
    while i < len(listData):
        # writeLog(unicode("获取股票数据, {0}").format(listData[i]))
        info = listData[i]
        if info is None:
            i = i + 1
            continue

        code = info.get('code')
        name = info.get('name')
        pe = info.get('pe')
        if pe == '--':
            i = i + 1
            continue

        pe = float(pe)
        print (unicode("获取股票数据, code: {0} , name:{1}, pe: {2}, avgPE: {3}").format(code, name, pe, avgPE))

        try:
            if (pe > float(avgPE)):
                return -1  # 如果已经大于当前平均PE，则不再继续获取

            pegData = getPEGByWC(code)
            print pegData
            rankData = getRankPeg(code)
            print rankData
            if not dicDuplicate.has_key(code):
                result.append(
                    unicode("{0},{1},{2},{3},{4},{5},{6},{7}\n").format(code, name, pe, pegData[0], pegData[1],
                                                                        rankData[0], rankData[1], rankData[2]).encode(
                        'gbk'))
            i = i + 1
        except Exception, e:
            writeErrorLog(unicode("getPEGFailed, code: {0} ,e: {1}").format(code, str(e)))
        if (i % 50 == 0):
            time.sleep(300)
        else:
            time.sleep(random.randint(10, 15))


# type: 1=沪深A PE<=上证平均市盈率，2：沪A，3：深A，4：中小板，5：创业板，6：上证50，7：沪深300，8：msci
def saveToDb(type, result):
    date = datetime.now().strftime('%Y-%m-%d')
    insertSql = unicode("INSERT INTO b_peg VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
    parameters = []
    for i in range(1, len(result)):
        data = result[i].replace("\n", "").decode('GBK').split(',')
        parameters.append(
            [data[0], date, data[1], int(time.time()), data[2], data[3], data[4], data[5], data[6], data[7], type])
    initMysql()
    batchInsert(insertSql, parameters)
    disconnect()


def handleSpecifiedStock(codeList):
    result = []
    result.append(
        unicode("{0},{1},{2},{3},{4},{5},{6},{7}\n").format("代码", "名称", "PE", "PEG", "预测PEG", "No1(代码:名称:PEG)",
                                                            "No2(代码:名称:PEG)", "No3(代码:名称:PEG)").encode('gbk'))

    i = 0
    while i < len(codeList):
        try:
            code = codeList[i]
            peInfo = getPEByWC(code)
            pegData = getPEGByWC(code)
            rankData = getRankPeg(code)

            print (unicode("获取指定股票数据, code: {0} , i:{1}, info: {2}").format(code, i, peInfo))
            result.append(
                unicode("{0},{1},{2},{3},{4},{5},{6},{7}\n").format(code, peInfo[0], peInfo[1], pegData[0], pegData[1],
                                                                    rankData[0], rankData[1], rankData[2]).encode(
                    'gbk'))
            i = i + 1
        except Exception, e:
            writeErrorLog(unicode("getPEGFailed, code: {0} ,e: {1}").format(code, str(e)))
        if (i % 50 == 0):
            time.sleep(300)
        else:
            time.sleep(random.randint(15, 20))

    return result


def getStockListByPE(peDiff):
    typeList = ['cyb']  # 全部A股,上证A,深证A,中小板,创业板
    shAvgPe = 17.37  # getShAvgPe()
    avgPE = [getSzAvgPe()[2]]
    for i in range(0, len(typeList)):
        getStockListData(i, typeList[i], avgPE[i] + peDiff)


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
    # if datetime.today().weekday() == 5 and datetime.now().hour >= 8 and datetime.now().hour < 9 and datetime.now().minute < 20:
    begin = datetime.now()

    # 执行每周任务
    getStockListByPE(0)
    getSh50()
    getSh300()
    getMSCI()
    # updateLatestGoodStockListToConfig()
    # updateNewList()
    # updateNewGoodList()
    # getStockHistoryInfo()

    end = datetime.now()
    sendMessageToMySelf(unicode("本周获取PEG的任务执行完毕,当前时间：{0}，执行用时：{1}").format(datetime.now(), end - begin))

    # t = Timer(900, runTask)
    # t.start()


def main(argv):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    runTask()


if __name__ == '__main__':
    main(sys.argv)
