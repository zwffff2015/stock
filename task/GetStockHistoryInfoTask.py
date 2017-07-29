# coding=utf-8

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))

from db.MysqlUtil import initMysql, execute, select, batchInsert, disconnect
from common.JsonHelper import loadJsonConfig
from api.tushareApi import getSimpleHistoryData
from datetime import datetime, timedelta
from common.LoggerHelper import writeErrorLog, writeWarningLog, writeInfoLog, writeDebugLog, writeLog
from wechat.weChatSender import sendMessageToMySelf
from common.HttpHelper import httpGet
import time
import json


# 从同花顺抓取历史行情数据（前复权）
def updateStockHistoryInfoByTHS(stockList):
    for stock in stockList:
        code = stock[0]
        i = 2010
        thisYear = datetime.now().year
        while (i <= thisYear):
            # time.sleep(1)
            infos = getStockInfos(code, i)
            if infos is None:
                continue

            for date in infos:
                open = infos.get(date).get('open')
                close = infos.get(date).get('close')
                high = infos.get(date).get('high')
                low = infos.get(date).get('low')
                volume = infos.get(date).get('volume')
                amount = infos.get(date).get('amount')

                checkExistSql = unicode("select count(*) from s_stock where code='{0}' and date='{1}'").format(code,
                                                                                                               date)
                count = select(checkExistSql, False)[0]
                if count > 0:
                    updateSql = unicode(
                        "update s_stock set volume={2},highPrice={3},lowPrice={4},openPrice={5},closePrice={6},amount='{7}' where code='{0}' and date='{1}'").format(
                        code, date, volume, high, low, open, close, amount)
                    execute(updateSql)
                    print code, date, updateSql
                else:
                    insertSql = unicode(
                        "insert into s_stock(code,date,timestamp,volume,highPrice,lowPrice,openPrice,closePrice,amount) VALUES ('{0}','{1}',{2},{3},{4},{5},{6},{7},'{8}')").format(
                        code, date, int(time.mktime(time.strptime(date, '%Y-%m-%d'))), volume, high, low, open, close,
                        amount)
                    execute(insertSql)
                    print code, date, insertSql
            i = i + 1


# 解析同花顺年行情数据（前复权）
def getStockInfos(code, year):
    try:
        url = "http://d.10jqka.com.cn/v2/line/hs_{0}/01/{1}.js".format(code, year)
        res = httpGet(url).decode("utf-8")
        index = res.find("(")
        if (index < 0):
            writeErrorLog(unicode("解析行情失败: code:{0}, year:{1}, res:{2}").format(code, year, res))
            return []
        res = res[index + 1:-1]
        writeLog(unicode("获取股票历史行情: code: {0}, year:{1}").format(code, year))
        jo = json.loads(res)

        dataInfo = jo['data'].split(';')

        result = {}
        for item in dataInfo:
            infos = item.split(',')
            dic = {}
            dic['open'] = infos[1]
            dic['high'] = infos[2]
            dic['low'] = infos[3]
            dic['close'] = infos[4]
            dic['volume'] = infos[5]
            dic['amount'] = "{0}亿".format(round(float(infos[6]) / 100000000, 1))

            result[datetime.strptime(infos[0], '%Y%m%d').strftime('%Y-%m-%d')] = dic

        return result
    except Exception, e:
        writeErrorLog(unicode("解析行情失败: code:{0}, year:{1}, e:{2}").format(code, year, str(e)))
        if "404" in str(e):
            return []
        else:
            return None


def getStockHistoryInfoFromDb():
    sql = unicode("SELECT code,count(*) from s_stock GROUP by code HAVING count(*)<20")
    data = select(sql)
    updateStockHistoryInfoByTHS(data)


def getStockHistoryInfoFromConfig():
    stockList = loadJsonConfig(os.path.abspath(os.path.join(os.getcwd(), "../config/newStockList.json")))
    updateStockHistoryInfoByTHS(stockList)


def updateAllStockHistoryInfo():
    sql = unicode("select code,name from s_stock_info order by code asc")
    data = select(sql)
    updateStockHistoryInfoByTHS(data)


def updateStockOtherInfo():
    sql = unicode("select code,name from s_stock_info order by code asc")
    stockList = select(sql)

    for stock in stockList:
        code = stock[0]
        selectInfoSql = unicode("select date,closePrice from s_stock where code='{0}' order by date asc").format(code)
        data = select(selectInfoSql)

        writeLog(unicode("更新股票其他指标数据: code: {0}").format(code))
        updataStockBias(code, data, 6)
        updataStockBias(code, data, 12)
        updataStockBias(code, data, 24)
        updateStockMA(code, data, 5)
        updateStockMA(code, data, 10)
        updateStockMA(code, data, 20)
        updateStockMA(code, data, 30)
        updateStockMA(code, data, 60)
        updateStockMA(code, data, 120)
        updateStockMA(code, data, 250)
        updateStockChangePercent(code, data)


def updateStockChangePercent(code, data):
    for i in range(1, len(data)):
        try:
            changeAmount = data[i][1] - data[i - 1][1]
            changePercent = round(changeAmount * 100 / data[i - 1][1], 2)
            updateSql = unicode(
                "update s_stock set changePercent={0},changeAmount={1} where code='{2}' and date='{3}'").format(
                changePercent, changeAmount, code, data[i][0])
            execute(updateSql)
        except Exception, e:
            writeErrorLog(
                unicode("更新涨幅数据失败: code:{0}, i:{1}, date:{2}, closePrice:{3}").format(code, i, data[i][0], data[i][1]))


def updateStockMA(code, data, n):
    for i in range(n - 1, len(data)):
        j = i
        sum = 0
        while (i - j < n):
            sum = sum + data[j][1]
            j = j - 1
        avg = round(sum / n, 2)
        sql = unicode("update s_stock set MA{0}={1} where code='{2}' and date='{3}'").format(n, avg, code, data[i][0])
        execute(sql)


def updataStockBias(code, data, n):
    for i in range(n - 1, len(data)):
        j = i
        sum = 0
        while (i - j < n):
            sum = sum + data[j][1]
            j = j - 1
        avg = round(sum / n, 2)

        todayClosePrice = float(data[i][1])
        bias = 0 if avg == 0 else round((todayClosePrice - avg) * 100 / avg, 2)
        number = 1 if n == 6 else (2 if n == 12 else 3)
        sql = unicode("update s_stock set BIAS{0}={1} where code='{2}' and date='{3}'").format(number, bias, code,
                                                                                               data[i][0])
        execute(sql)


def main(argv):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    # sendMessageToMySelf(unicode("开始查询股票历史行情数据"))
    begin = datetime.now()
    initMysql()
    # getStockHistoryInfoFromDb()
    # getStockHistoryInfoFromConfig()
    updateStockOtherInfo()
    disconnect()
    end = datetime.now()

    message = unicode("查询股票历史行情数据的任务执行完毕,当前时间：{0}，执行用时：{1}").format(datetime.now(), end - begin)
    writeLog(message)
    sendMessageToMySelf(message)


if __name__ == '__main__':
    main(sys.argv)
