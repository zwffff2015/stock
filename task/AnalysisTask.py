# coding=utf-8

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))
import json
import time
from datetime import datetime, date
from db.MysqlUtil import initMysql, execute, select, batchInsert, disconnect

'''
    分析当天涨幅超过5%的股票的预测结果
'''


def checkHighChangePercentStockForcase():
    date = datetime.now().strftime('%Y-%m-%d')
    timestamp = int(time.mktime(time.strptime(date, '%Y-%m-%d')))
    stockList = select(
        unicode(
            "SELECT s.changePercent,f.* FROM s_stock_forecast as f INNER JOIN (SELECT * FROM s_stock where timestamp={0} and changePercent>=5) as s on (f.code=s.code and f.date=s.date)").format(
            timestamp))

    # 指标列表
    indexList = ['', '', '', 'MACD', 'DMI', 'DMA', 'EXPMA', 'EMV', 'TRIX', 'WVAD', 'VR', 'CR', 'AR', 'PSY', 'KDJ',
                 'RSI', 'MTM', 'WR', 'CCI', 'OBV', '', '', '', '', 'BGB', 'BGB_DIFF4', 'TrendMax', 'EnergyMax',
                 'OBOSMax', 'TrendEnergyShow', 'TrendOBOSShow', 'EnergyOBOSShow', 'TrendEnergyOBOSShow',
                 'TEOBOS_BGBShow', 'TE_BGBShow', 'EOBOS_BGBShow', 'TOBOS_BGBShow', 'AllBulls', 'AllBulls_DIFF4']

    insertSql = unicode("INSERT INTO s_high_result VALUES(%s,%s,%s,%s)")
    parameters = []
    for row in stockList:
        changePercent = row[0]
        code = row[1]
        date = row[2]
        list = []
        for i in range(3, len(row)):
            indexName = indexList[i]  # 指标名称
            if (indexName == ''):  # 过滤掉不是指标的列
                continue
            if (row[i] == 0):
                list.append(indexName)
        parameters.append([code, date, changePercent, json.dumps(list)])

    batchInsert(insertSql, parameters)
