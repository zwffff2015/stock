# coding=utf-8
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))

from common.JsonHelper import loadJsonConfig
from stock.StockInfo import getTechParamter
from db.MysqlUtil import initMysql, execute, select, batchInsert, disconnect

import time
from threading import Timer
from wechat.weChatSender import sendMessageToMySelf
from datetime import datetime, timedelta
from common.LoggerHelper import writeErrorLog
from common.Logger import Logger


def saveStockTechToDb(stockTechInfo, date, updateOp):
    if updateOp:
        updateSql = unicode(
            "update s_stock_tech set MACD={2},DIF={3},DEA={4},ADX={5},ADXR={6},INCDI={7},DECDI={8},DMA={9},AMA={10},EXPMA1={11},EXPMA2={12},EMV={13},TRIX={14}, TMA={15},WVAD={16},VR={17},CR={18},AR={19},BR={20},PSY={21},K={22},D={23},J={24},RSI1={25},RSI2={26},MTM={27},MA={28},WR1={29},CCI={30},OBV={31} where code='{0}' and date='{1}'").format(
            stockTechInfo.code, date, stockTechInfo.MACD, stockTechInfo.DIF, stockTechInfo.DEA, stockTechInfo.ADX,
            stockTechInfo.ADXR, stockTechInfo.INCDI, stockTechInfo.DECDI, stockTechInfo.DMA, stockTechInfo.AMA,
            stockTechInfo.EXPMA1, stockTechInfo.EXPMA2, stockTechInfo.EMV, stockTechInfo.TRIX, stockTechInfo.TMA,
            stockTechInfo.WVAD, stockTechInfo.VR, stockTechInfo.CR
            , stockTechInfo.AR, stockTechInfo.BR, stockTechInfo.PSY, stockTechInfo.K, stockTechInfo.D, stockTechInfo.J,
            stockTechInfo.RSI1, stockTechInfo.RSI2, stockTechInfo.MTM, stockTechInfo.MA, stockTechInfo.WR,
            stockTechInfo.CCI, stockTechInfo.OBV)
        execute(updateSql)
    else:
        insertSql = unicode(
            "insert into s_stock_tech(code,date,timestamp,MACD,DIF,DEA,ADX,ADXR,INCDI,DECDI,DMA,AMA,EXPMA1,EXPMA2,EMV,TRIX,TMA,WVAD,VR,CR,AR,BR,PSY,K,D,J,RSI1,RSI2,MTM,MA,WR1,CCI,OBV) VALUES (\'{0}\',\'{1}\',{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18},{19},{20},{21},{22},{23},{24},{25},{26},{27},{28},{29},{30},{31},{32})").format(
            stockTechInfo.code,
            date, int(
                time.mktime(time.strptime(date, '%Y-%m-%d'))), stockTechInfo.MACD, stockTechInfo.DIF, stockTechInfo.DEA,
            stockTechInfo.ADX, stockTechInfo.ADXR, stockTechInfo.INCDI, stockTechInfo.DECDI, stockTechInfo.DMA,
            stockTechInfo.AMA, stockTechInfo.EXPMA1, stockTechInfo.EXPMA2, stockTechInfo.EMV, stockTechInfo.TRIX,
            stockTechInfo.TMA, stockTechInfo.WVAD, stockTechInfo.VR, stockTechInfo.CR
            , stockTechInfo.AR, stockTechInfo.BR, stockTechInfo.PSY, stockTechInfo.K, stockTechInfo.D, stockTechInfo.J,
            stockTechInfo.RSI1, stockTechInfo.RSI2, stockTechInfo.MTM, stockTechInfo.MA, stockTechInfo.WR,
            stockTechInfo.CCI, stockTechInfo.OBV)
        execute(insertSql)


def saveStockTechForecastToDb(stockTechStatus, forecastInfo, date):
    checkExistSql = unicode("select count(*) from s_stock_forecast where code='{0}' and date='{1}'").format(
        stockTechStatus.code,
        date)
    count = select(checkExistSql, False)[0]
    if count > 0:
        updateSql = unicode(
            "update s_stock_forecast set MACD={2},DMI={3},DMA={4},EXPMA={5},EMV={6},TRIX={7},WVAD={8},VR={9},CR={10},AR={11},PSY={12},KDJ={13},RSI={14}, MTM={15},WR={16},CCI={17},OBV={18},bulls={19},bears={20},notsure={21},BGB={22},BGB_DIFF4={23},TrendMax={24},EnergyMax={25},OBOSMax={26},TrendEnergyShow={27},TrendOBOSShow={28},EnergyOBOSShow={29},TrendEnergyOBOSShow={30},TEOBOS_BGBShow={31},TE_BGBShow={32},EOBOS_BGBShow={33},TOBOS_BGBShow={34},AllBulls={35},AllBulls_DIFF4={36} where code='{0}' and date='{1}'").format(
            stockTechStatus.code, date, stockTechStatus.MACD, stockTechStatus.DMI,
            stockTechStatus.DMA,
            stockTechStatus.EXPMA, stockTechStatus.EMV, stockTechStatus.TRIX, stockTechStatus.WVAD, stockTechStatus.VR,
            stockTechStatus.CR
            , stockTechStatus.AR, stockTechStatus.PSY, stockTechStatus.KDJ, stockTechStatus.RSI, stockTechStatus.MTM,
            stockTechStatus.WR,
            stockTechStatus.CCI, stockTechStatus.OBV, stockTechStatus.bulls, stockTechStatus.bears,
            stockTechStatus.notsure, forecastInfo.BGB, forecastInfo.BGB_DIFF4, forecastInfo.TrendMax,
            forecastInfo.EnergyMax, forecastInfo.OBOSMax, forecastInfo.TrendEnergyShow, forecastInfo.TrendOBOSShow,
            forecastInfo.EnergyOBOSShow, forecastInfo.TrendEnergyOBOSShow, forecastInfo.TEOBOS_BGBShow,
            forecastInfo.TE_BGBShow, forecastInfo.EOBOS_BGBShow, forecastInfo.TOBOS_BGBShow, forecastInfo.AllBulls,
            forecastInfo.AllBulls_DIFF4)
        execute(updateSql)
    else:
        insertSql = unicode(
            "insert into s_stock_forecast(code,date,timestamp,MACD,DMI,DMA,EXPMA,EMV,TRIX,WVAD,VR,CR,AR,PSY,KDJ,RSI,MTM,WR,CCI,OBV,bulls,bears,notsure,BGB,BGB_DIFF4,TrendMax,EnergyMax,OBOSMax,TrendEnergyShow,TrendOBOSShow,EnergyOBOSShow,TrendEnergyOBOSShow,TEOBOS_BGBShow,TE_BGBShow,EOBOS_BGBShow,TOBOS_BGBShow,AllBulls,AllBulls_DIFF4) VALUES (\'{0}\',\'{1}\',{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18},{19},{20},{21},{22},{23},{24},{25},{26},{27},{28},{29},{30},{31},{32},{33},{34},{35},{36},{37})").format(
            stockTechStatus.code,
            date, int(
                time.mktime(time.strptime(date, '%Y-%m-%d'))), stockTechStatus.MACD, stockTechStatus.DMI,
            stockTechStatus.DMA,
            stockTechStatus.EXPMA, stockTechStatus.EMV, stockTechStatus.TRIX, stockTechStatus.WVAD, stockTechStatus.VR,
            stockTechStatus.CR
            , stockTechStatus.AR, stockTechStatus.PSY, stockTechStatus.KDJ, stockTechStatus.RSI, stockTechStatus.MTM,
            stockTechStatus.WR,
            stockTechStatus.CCI, stockTechStatus.OBV, stockTechStatus.bulls, stockTechStatus.bears,
            stockTechStatus.notsure, forecastInfo.BGB, forecastInfo.BGB_DIFF4, forecastInfo.TrendMax,
            forecastInfo.EnergyMax, forecastInfo.OBOSMax, forecastInfo.TrendEnergyShow, forecastInfo.TrendOBOSShow,
            forecastInfo.EnergyOBOSShow, forecastInfo.TrendEnergyOBOSShow, forecastInfo.TEOBOS_BGBShow,
            forecastInfo.TE_BGBShow, forecastInfo.EOBOS_BGBShow, forecastInfo.TOBOS_BGBShow, forecastInfo.AllBulls,
            forecastInfo.AllBulls_DIFF4)
        execute(insertSql)


def saveStockTech():
    date = datetime.now().strftime('%Y-%m-%d')
    weekday = datetime.today().weekday()
    if weekday == 5 or weekday == 6:
        return

    tomorrow = (datetime.now() + timedelta(days=(3 if weekday == 4 else 1))).strftime('%Y-%m-%d')

    stockList = select(unicode(
        "SELECT code,name from s_stock_info"))  # loadJsonConfig(os.path.abspath(os.path.join(os.getcwd(), "../config/goodStockList.json")))
    i = 0
    while i < len(stockList):
        code = stockList[i][0]

        checkExistSql = unicode("select count(*) from s_stock_tech where code='{0}' and date='{1}'").format(code,
                                                                                                            date)
        count = select(checkExistSql, False)[0]
        if count > 0:
            i = i + 1
            continue

        try:
            info = getTechParamter(code)
            saveStockTechToDb(info[0], date, count > 0)
            saveStockTechForecastToDb(info[1], info[2], tomorrow)
            i = i + 1
        except Exception, e:
            writeErrorLog(unicode("getTechFailed, code: {0}, e: {1}").format(code, e))
        time.sleep(1)


def runTask():
    if datetime.today().weekday() < 5 and datetime.now().hour >= 22 and datetime.now().hour < 23 and datetime.now().minute < 25:
        sendMessageToMySelf(unicode("开始获取今日股票技术指标数据"))
        begin = datetime.now()

        initMysql()
        saveStockTech()
        disconnect()

        end = datetime.now()
        sys.setdefaultencoding('utf-8')
        sendMessageToMySelf(unicode("今日获取各个股票的技术指标数据的任务执行完毕,当前时间：{0}，执行用时：{1}").format(datetime.now(), end - begin))

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
