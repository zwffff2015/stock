# coding=utf-8

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))

from common.JsonHelper import loadJsonConfig
from stock.StockInfo import getStockInfo
from db.MysqlUtil import initMysql, execute, select, batchInsert, disconnect
import time
from threading import Timer
from wechat.weChatSender import sendMessageToMySelf
from datetime import datetime, timedelta
from AnalysisTask import checkHighChangePercentStockForcase
from common.LoggerHelper import writeLog, writeDebugLog, writeWarningLog, writeErrorLog
from common.FileHelper import saveFile
from common.Logger import Logger
import logging


class IndexResult:
    def __init__(self, up_right, up_total, down_right, down_total):
        self.up_right = up_right
        self.up_total = up_total
        self.down_right = down_right
        self.down_total = down_total


def saveStockInfoToDb(info, date):
    checkExistSql = unicode("select count(*) from s_stock where code='{0}' and date='{1}'").format(
        info['code'],
        date)
    count = select(checkExistSql, False)[0]

    if count > 0:
        updateSql = unicode(
            "update s_stock set limitUp={2},limitDown={3},avgPrice={4},volume={5},amount='{6}',highPrice={7},lowPrice={8},openPrice={9},closePrice={10},changePercent={11},changeAmount={12},turnOverRatio={13},QRR={14}, totalValue={15},circulatedValue={16},PE={17},PTB={18},internalPan={19},externalPan={20} where code='{0}' and date='{1}'").format(
            info['code'], date, info['limitUp'], info['limitDown'], info['avgPrice'], info['volume'], info['amount'],
            info['highPrice'], info['lowPrice'], info['openPrice'], info['closePrice'], info['changePercent'],
            info['changeAmount'], info['turnOverRatio'], info['QRR'], info['totalValue'], info['circulatedValue'],
            info['PE'], info['PTB'], info['internalPan'], info['externalPan'])
        execute(updateSql)
    else:
        insertSql = unicode(
            "insert into s_stock(code,date,timestamp,limitUp,limitDown,avgPrice,volume,amount,highPrice,lowPrice,openPrice,closePrice,changePercent,changeAmount,turnOverRatio,QRR,totalValue,circulatedValue,PE,PTB,internalPan,externalPan) VALUES ('{0}','{1}',{2},{3},{4},{5},{6},'{7}',{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18},{19},{20},{21})").format(
            info['code'],
            date, int(
                time.mktime(time.strptime(date, '%Y-%m-%d'))), info['limitUp'], info['limitDown'], info['avgPrice'],
            info['volume'], info['amount'], info['highPrice'], info['lowPrice'], info['openPrice'], info['closePrice'],
            info['changePercent'], info['changeAmount'], info['turnOverRatio'], info['QRR'], info['totalValue'],
            info['circulatedValue'], info['PE'], info['PTB'], info['internalPan'], info['externalPan'])
        execute(insertSql)


def updateForecastResult(date):
    writeLog(unicode("beginUpdateForecastResult, date:{0}").format(date))
    selectSql = unicode(
        "select f.*,s.changePercent from s_stock_forecast as f INNER JOIN s_stock as s ON (s.code=f.code and s.date=f.date) where f.date='{0}'").format(
        date)
    data = select(selectSql)

    weekday = datetime.today().weekday()
    diff = 1 if weekday >= 1 and weekday <= 4 else (3 if weekday == 0 else weekday - 3)
    lastDay = (datetime.now() - timedelta(days=diff)).strftime('%Y-%m-%d')

    indexType = ['', '', 'MACD', 'DMI', 'DMA', 'EXPMA', 'EMV', 'TRIX', 'WVAD', 'VR', 'CR', 'AR', 'PSY', 'KDJ', 'RSI',
                 'MTM', 'WR', 'CCI', 'OBV', '', '', '', '', 'BGB']
    upIndexType = ['BGB_DIFF4', 'TrendMax', 'EnergyMax', 'OBOSMax', 'TrendEnergyShow', 'TrendOBOSShow',
                   'EnergyOBOSShow', 'TrendEnergyOBOSShow', 'TEOBOS_BGBShow', 'TE_BGBShow', 'EOBOS_BGBShow',
                   'TOBOS_BGBShow', 'AllBulls', 'AllBulls_DIFF4']

    forecastCountField = ''
    forecastCountValue = ''
    dictCount = {}
    for row in data:
        dictIndex = {}
        upDictIndex = {}
        changePercent = row[len(row) - 1]

        for i in range(0, 24):
            if (indexType[i] == ''):
                continue

            if (row[i] == 0):
                if (changePercent > 0):
                    # 预测上涨，实际上涨
                    dictIndex[indexType[i]] = 1
                elif (changePercent < 0):
                    # 预测上涨，实际下跌
                    dictIndex[indexType[i]] = 2
                else:
                    # 预测上涨，实际持平
                    dictIndex[indexType[i]] = 3
            elif (row[i] == 1):
                if (changePercent > 0):
                    # 预测下跌，实际上涨
                    dictIndex[indexType[i]] = 4
                elif (changePercent < 0):
                    # 预测下跌，实际下跌
                    dictIndex[indexType[i]] = 5
                else:
                    # 预测下跌，实际持平
                    dictIndex[indexType[i]] = 6

        for i in range(24, len(row) - 1):
            if (row[i] == 0):
                j = i - 24
                if (changePercent > 0):
                    # 预测上涨，实际上涨
                    upDictIndex[upIndexType[j]] = 1
                elif (changePercent < 0):
                    # 预测上涨，实际下跌
                    upDictIndex[upIndexType[j]] = 2
                else:
                    # 预测上涨，实际持平
                    upDictIndex[upIndexType[j]] = 3

        forecastResultField = ''
        forecastResultValue = ''

        stockForecastCountField = ''
        stockForecastCountValue = ''

        lastDayStockForecastCountData = select(
            unicode("select * from s_stock_forecast_count where code='{0}' and date='{1}'").format(row[0], lastDay))

        i = 1
        for index in indexType:
            if (index == ''):
                continue
            forecastResultField = forecastResultField + index + ','
            forecastResultValue = forecastResultValue + str(dictIndex[index] if dictIndex.has_key(index) else -1) + ','
            stockForecastCountField = "{0}{1}_up_right,{1}_up_total,{1}_down_right,{1}_down_total,".format(
                stockForecastCountField, index)
            if len(lastDayStockForecastCountData) > 0:
                up_right = lastDayStockForecastCountData[0][3 + (i - 1) * 4 + 1] + (
                    1 if dictIndex.has_key(index) and dictIndex.get(index) == 1 else 0)
                up_total = lastDayStockForecastCountData[0][3 + (i - 1) * 4 + 2] + (
                    1 if dictIndex.has_key(index) and dictIndex.get(index) <= 3 else 0)
                down_right = lastDayStockForecastCountData[0][3 + (i - 1) * 4 + 3] + (
                    1 if dictIndex.has_key(index) and dictIndex.get(index) == 5 else 0)
                down_total = lastDayStockForecastCountData[0][3 + (i - 1) * 4 + 4] + (
                    1 if dictIndex.has_key(index) and dictIndex.get(index) > 3 else 0)
                stockForecastCountValue = "{0}{1},{2},{3},{4},".format(stockForecastCountValue, up_right, up_total,
                                                                       down_right, down_total)
            else:
                up_right = (1 if dictIndex.has_key(index) and dictIndex.get(index) == 1 else 0)
                up_total = (1 if dictIndex.has_key(index) and dictIndex.get(index) <= 3 else 0)
                down_right = (1 if dictIndex.has_key(index) and dictIndex.get(index) == 5 else 0)
                down_total = (1 if dictIndex.has_key(index) and dictIndex.get(index) > 3 else 0)
                stockForecastCountValue = "{0}{1},{2},{3},{4},".format(stockForecastCountValue, up_right, up_total,
                                                                       down_right, down_total)

            forecastCount_up_right = (1 if dictIndex.has_key(index) and dictIndex.get(index) == 1 else 0)
            forecastCount_up_total = (1 if dictIndex.has_key(index) and dictIndex.get(index) <= 3 else 0)
            forecastCount_down_right = (1 if dictIndex.has_key(index) and dictIndex.get(index) == 5 else 0)
            forecastCount_down_total = (1 if dictIndex.has_key(index) and dictIndex.get(index) > 3 else 0)
            if (dictCount.has_key(index)):
                dictCount[index].up_right = dictCount[index].up_right + forecastCount_up_right
                dictCount[index].up_total = dictCount[index].up_total + forecastCount_up_total
                dictCount[index].down_right = dictCount[index].down_right + forecastCount_down_right
                dictCount[index].down_total = dictCount[index].down_total + forecastCount_down_total
            else:
                dictCount[index] = IndexResult(forecastCount_up_right, forecastCount_up_total, forecastCount_down_right,
                                               forecastCount_down_total)

            i = i + 1

        j = 1
        for index in upIndexType:
            if (index == ''):
                continue
            forecastResultField = forecastResultField + index + ','
            forecastResultValue = forecastResultValue + str(
                upDictIndex[index] if upDictIndex.has_key(index) else -1) + ','
            stockForecastCountField = "{0}{1}_up_right,{1}_up_total,".format(
                stockForecastCountField, index)
            if len(lastDayStockForecastCountData) > 0:
                up_right = lastDayStockForecastCountData[0][75 + (j - 1) * 2 + 1] + (
                    1 if upDictIndex.has_key(index) and upDictIndex.get(index) == 1 else 0)
                up_total = lastDayStockForecastCountData[0][75 + (j - 1) * 2 + 2] + (
                    1 if upDictIndex.has_key(index) else 0)
                stockForecastCountValue = "{0}{1},{2},".format(stockForecastCountValue, up_right, up_total)
            else:
                up_right = (1 if upDictIndex.has_key(index) and upDictIndex.get(index) == 1 else 0)
                up_total = (1 if upDictIndex.has_key(index) else 0)
                stockForecastCountValue = "{0}{1},{2},".format(stockForecastCountValue, up_right, up_total)

            forecastCount_up_right = (1 if upDictIndex.has_key(index) and upDictIndex.get(index) == 1 else 0)
            forecastCount_up_total = (1 if upDictIndex.has_key(index) else 0)
            if (dictCount.has_key(index)):
                dictCount[index].up_right = dictCount[index].up_right + forecastCount_up_right
                dictCount[index].up_total = dictCount[index].up_total + forecastCount_up_total
            else:
                dictCount[index] = IndexResult(forecastCount_up_right, forecastCount_up_total, 0, 0)

            j = j + 1

        forecastResultSql = unicode(
            "insert into s_stock_forecast_result(code,date,timestamp,{0}) values('{1}','{2}',{3},{4})").format(
            forecastResultField[:-1], row[0], row[1], row[22], forecastResultValue[:-1])
        stockForecastCountSql = unicode(
            "insert into s_stock_forecast_count(code,date,timestamp,updateTS,{0}) values('{1}','{2}',{3},{4},{5})").format(
            stockForecastCountField[:-1], row[0], row[1], row[22], int(time.time()), stockForecastCountValue[:-1])

        execute(forecastResultSql)
        execute(stockForecastCountSql)

    lastDayForecastCountData = select(
        unicode("select * from s_forecast_count where date='{0}'").format(lastDay))
    i = 1
    for index in indexType:
        if (index == ''):
            continue

        forecastCountField = "{0}{1}_up_right,{1}_up_total,{1}_down_right,{1}_down_total,".format(
            forecastCountField, index)
        if len(lastDayForecastCountData) > 0:
            forecastCount_up_right = lastDayForecastCountData[0][2 + (i - 1) * 4 + 1] + (
                dictCount.get(index).up_right if dictCount.has_key(index) else 0)
            forecastCount_up_total = lastDayForecastCountData[0][2 + (i - 1) * 4 + 2] + (
                dictCount.get(index).up_total if dictCount.has_key(index) else 0)
            forecastCount_down_right = lastDayForecastCountData[0][2 + (i - 1) * 4 + 3] + (
                dictCount.get(index).down_right if dictCount.has_key(index) else 0)
            forecastCount_down_total = lastDayForecastCountData[0][2 + (i - 1) * 4 + 4] + (
                dictCount.get(index).down_total if dictCount.has_key(index) else 0)
            forecastCountValue = "{0}{1},{2},{3},{4},".format(forecastCountValue, forecastCount_up_right,
                                                              forecastCount_up_total,
                                                              forecastCount_down_right,
                                                              forecastCount_down_total)
        else:
            forecastCount_up_right = (dictCount.get(index).up_right if dictCount.has_key(index) else 0)
            forecastCount_up_total = (dictCount.get(index).up_total if dictCount.has_key(index) else 0)
            forecastCount_down_right = (dictCount.get(index).down_right if dictCount.has_key(index) else 0)
            forecastCount_down_total = (dictCount.get(index).down_total if dictCount.has_key(index) else 0)
            forecastCountValue = "{0}{1},{2},{3},{4},".format(forecastCountValue, forecastCount_up_right,
                                                              forecastCount_up_total,
                                                              forecastCount_down_right,
                                                              forecastCount_down_total)
        i = i + 1

    j = 1
    for index in upIndexType:
        if (index == ''):
            continue

        forecastCountField = "{0}{1}_up_right,{1}_up_total,".format(
            forecastCountField, index)
        if len(lastDayForecastCountData) > 0:
            forecastCount_up_right = lastDayForecastCountData[0][74 + (j - 1) * 2 + 1] + (
                dictCount.get(index).up_right if dictCount.has_key(index) else 0)
            forecastCount_up_total = lastDayForecastCountData[0][74 + (j - 1) * 2 + 2] + (
                dictCount.get(index).up_total if dictCount.has_key(index) else 0)
            forecastCountValue = "{0}{1},{2},".format(forecastCountValue, forecastCount_up_right,
                                                      forecastCount_up_total)
        else:
            forecastCount_up_right = (dictCount.get(index).up_right if dictCount.has_key(index) else 0)
            forecastCount_up_total = (dictCount.get(index).up_total if dictCount.has_key(index) else 0)
            forecastCountValue = "{0}{1},{2},".format(forecastCountValue, forecastCount_up_right,
                                                      forecastCount_up_total)
        j = j + 1

    forecastCountSql = unicode(
        "insert into s_forecast_count(date,timestamp,updateTs,{0}) values('{1}',{2},{3},{4})").format(
        forecastCountField[:-1], date, int(
            time.mktime(time.strptime(date, '%Y-%m-%d'))), int(time.time()), forecastCountValue[:-1])
    execute(forecastCountSql)
    writeLog(unicode("endUpdateForecastResult, date:{0}").format(date))


def saveStockInfo():
    date = datetime.now()
    weekday = datetime.today().weekday()
    diff = 0 if weekday < 5 else weekday - 4
    date = (date - timedelta(days=diff)).strftime('%Y-%m-%d')

    stockList = select(unicode(
        "SELECT code,name from s_stock_info"))  # loadJsonConfig(os.path.abspath(os.path.join(os.getcwd(), "../config/goodStockList.json")))
    i = 0
    while i < len(stockList):
        code = stockList[i][0]

        try:
            info = getStockInfo(code)
            if info is None:
                i = i + 1
                continue

            saveStockInfoToDb(info, date)
            i = i + 1
        except Exception, e:
            writeErrorLog(unicode("getStockInfoFailed, code:{0}, e:{1}").format(code, str(e)))
        time.sleep(0.2)

    updateForecastResult(date)


def runTask():
    if datetime.today().weekday() < 5 and datetime.now().hour >= 19 and datetime.now().hour < 20 and datetime.now().minute < 20:
        sendMessageToMySelf(unicode("开始获取今日股票行情数据"))
        begin = datetime.now()

        initMysql()
        saveStockInfo()
        checkHighChangePercentStockForcase()
        disconnect()

        end = datetime.now()
        sendMessageToMySelf(unicode("今日获取各个股票的行情数据的任务执行完毕,当前时间：{0}，执行用时：{1}").format(datetime.now(), end - begin))

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
