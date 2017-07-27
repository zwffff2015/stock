# coding=utf-8

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))
from db.MysqlUtil import initMysql, execute, select, batchInsert, disconnect
from stock.StockTechStatus import StockTechStatus
from stock.GainIndexForecast import getGainForecast
from task.StockTechTask import saveStockTechForecastToDb
from common.StringHelper import toString


def updateForecast():
    forecastData = select(unicode("select * from s_stock_forecast"))
    for item in forecastData:
        dictStatus = {}

        code = item[0]
        date = item[1]
        dictStatus['MACD'] = toString(item[2])
        dictStatus['ADX'] = toString(item[3])
        dictStatus['DMA'] = toString(item[4])
        dictStatus['EXPMA1'] = toString(item[5])
        dictStatus['EMV'] = toString(item[6])
        dictStatus['TRIX'] = toString(item[7])
        dictStatus['WVAD'] = toString(item[8])
        dictStatus['VR'] = toString(item[9])
        dictStatus['CR'] = toString(item[10])
        dictStatus['AR'] = toString(item[11])
        dictStatus['PSY'] = toString(item[12])
        dictStatus['K'] = toString(item[13])
        dictStatus['RSI1'] = toString(item[14])
        dictStatus['MTM'] = toString(item[15])
        dictStatus['W&R'] = toString(item[16])
        dictStatus['CCI'] = toString(item[17])
        dictStatus['OBV'] = toString(item[18])
        bulls = item[19]
        bears = item[20]
        notsure = item[21]

        stockTechStatus = StockTechStatus(code, dictStatus, bulls, bears, notsure)
        forecastInfo = getGainForecast(stockTechStatus)
        saveStockTechForecastToDb(stockTechStatus, forecastInfo, date)


def main(argv):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    initMysql()
    updateForecast()


if __name__ == '__main__':
    main(sys.argv)
