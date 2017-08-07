# coding=utf-8

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))

import stock.StockIndex as StockIndex
from db.MysqlUtil import initMysql, execute, select, batchInsert, disconnect
import time
from datetime import datetime, timedelta
from threading import Timer
from wechat.weChatSender import sendMessageToMySelf
from common.FileHelper import saveFile
from common.Logger import Logger
import logging


def saveStockIndexToDb(stockIndexInfo, date):
    checkExistSql = unicode("select count(*) from s_index where code='{0}' and date='{1}'").format(stockIndexInfo.code,
                                                                                                   date)
    count = select(checkExistSql, False)[0]
    if count > 0:
        updateSql = unicode(
            "update s_index set name='{0}',`index`={1},upNumber={2},downNumber={3},equalNumber={4},highIndex={7},lowIndex={8},openIndex={9},changePercent={10},changeAmount={11},volume={12},amount='{13}',turnOverRatio={14},internalPan={15},externalPan={16},upDownPercent={17},avgPE={18} where code='{5}' and date='{6}'").format(
            stockIndexInfo.name, stockIndexInfo.index, stockIndexInfo.upNumber, stockIndexInfo.downNumber,
            stockIndexInfo.equalNumber, stockIndexInfo.code, date, stockIndexInfo.high, stockIndexInfo.low,
            stockIndexInfo.open, stockIndexInfo.changePercent, stockIndexInfo.changeAmount, stockIndexInfo.volume,
            stockIndexInfo.amount, stockIndexInfo.turnOverRatio, stockIndexInfo.internalPan, stockIndexInfo.externalPan,
            stockIndexInfo.upDownPercent, stockIndexInfo.avgPE)
        execute(updateSql)
    else:
        insertSql = unicode(
            "insert into s_index(code,date,name,`index`,upNumber,downNumber,equalNumber,highIndex,lowIndex,openIndex,changePercent,changeAmount,volume,amount,turnOverRatio,internalPan,externalPan,upDownPercent,avgPE,timestamp) VALUES (\'{0}\',\'{1}\',\'{2}\',{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},\'{13}\',{14},{15},{16},{17},{18},{19})").format(
            stockIndexInfo.code, date, stockIndexInfo.name, stockIndexInfo.index, stockIndexInfo.upNumber,
            stockIndexInfo.downNumber, stockIndexInfo.equalNumber, stockIndexInfo.high, stockIndexInfo.low,
            stockIndexInfo.open, stockIndexInfo.changePercent, stockIndexInfo.changeAmount, stockIndexInfo.volume,
            stockIndexInfo.amount, stockIndexInfo.turnOverRatio, stockIndexInfo.internalPan, stockIndexInfo.externalPan,
            stockIndexInfo.upDownPercent, stockIndexInfo.avgPE, int(time.mktime(time.strptime(date, '%Y-%m-%d'))))
        execute(insertSql)


def updateOBOS(index, timestamp):
    selectSql = unicode(
        "update s_index set obos=(select count from (SELECT SUM(b.upNumber)-Sum(b.downNumber) as count FROM s_index as b WHERE b.timestamp<={1} and b.code='{0}' ORDER by b.timestamp desc limit 10) as c) where code='{0}' and timestamp={1}").format(
        index,
        timestamp)
    execute(selectSql)


def saveStockIndex():
    date = datetime.now()
    weekday = datetime.today().weekday()
    diff = 0 if weekday < 5 else weekday - 4
    date = (date - timedelta(days=diff)).strftime('%Y-%m-%d')

    # 获取今日指数数据
    result = StockIndex.getTotalStockNumber()
    for stockIndex in result:
        saveStockIndexToDb(stockIndex, date)

    indexType = ['0000011', '0000161', '0003001', '3990012', '3990052', '3990062']
    # 更新今日指数的OBOS数据
    timestamp = int(time.mktime(time.strptime(date, '%Y-%m-%d')))
    for index in indexType:
        updateOBOS(index, timestamp)


def runTask():
    if datetime.today().weekday() < 5 and datetime.now().hour >= 19 and datetime.now().hour < 20 and datetime.now().minute < 20:
        sendMessageToMySelf(unicode("开始获取今日指数数据"))
        begin = datetime.now()

        initMysql()
        saveStockIndex()
        disconnect()

        end = datetime.now()
        sendMessageToMySelf(unicode("今日获取指数数据的任务执行完毕,当前时间：{0}，执行用时：{1}").format(datetime.now(), end - begin))

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
