# coding:utf-8

from common.HttpHelper import httpGet
import json
import random
from StockIndexInfo import StockIndexInfo
from StockInfo import getShAvgPe, getSzAvgPe
from common.LoggerHelper import writeErrorLog, writeWarningLog, writeInfoLog, writeDebugLog, writeLog


def getTotalStockNumber():
    url = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=0000011,3990012,3990052,3990062,0000161,0003001&sty=DFPIU&st=z&sr=&p=&ps=&cb=&js=var%20C1Cache={quotation:[(x)]}&token=44c9d251add88e27b65ed86506f6e5da&0.0530516490' + str(
        random.randint(1000000, 9999999))
    result = httpGet(url)

    index = result.find("=")
    if (index < 0):
        return

    result = result[12:].replace("quotation", "\"quotation\"")
    jo = json.loads(result)
    writeLog(unicode("getStockIndexInfo: result:{0} ").format(result))

    # 沪指
    shQuotation = jo['quotation'][0]
    shStockIndexInfo = shQuotation.split(',')
    shNumberInfo = shStockIndexInfo[6].split('|')
    shOtherData = getOtherData('0000011')
    shAvgPE = getShAvgPe()
    shIndexInfo = StockIndexInfo(shStockIndexInfo[0], shStockIndexInfo[1], shStockIndexInfo[2], shNumberInfo[0],
                                 shNumberInfo[2], shNumberInfo[1], shAvgPE, shOtherData)

    # 深圳主板
    szAvgPE = getSzAvgPe()
    szQuotation = jo['quotation'][1]
    szStockIndexInfo = szQuotation.split(',')
    szNumberInfo = szStockIndexInfo[7].split('|')
    szOtherData = getOtherData('3990012')
    szIndexInfo = StockIndexInfo(szStockIndexInfo[0], szStockIndexInfo[1], szStockIndexInfo[2], szNumberInfo[0],
                                 szNumberInfo[2], szNumberInfo[1], szAvgPE[0], szOtherData)

    # 中小板
    szSMEBoardQuotation = jo['quotation'][2]
    szSMEBoardStockIndexInfo = szSMEBoardQuotation.split(',')
    szSMEBoardNumberInfo = getOtherUpDownNumber('SZ.ZXB')
    szSMEBoardOtherData = getOtherData('3990052')
    szSMEBoardIndexInfo = StockIndexInfo(szSMEBoardStockIndexInfo[0], szSMEBoardStockIndexInfo[1],
                                         szSMEBoardStockIndexInfo[2], szSMEBoardNumberInfo[0],
                                         szSMEBoardNumberInfo[2], szSMEBoardNumberInfo[1], szAvgPE[1],
                                         szSMEBoardOtherData)

    # 创业板
    szSecondBoardQuotation = jo['quotation'][3]
    szSecondBoardStockIndexInfo = szSecondBoardQuotation.split(',')
    szSecondBoardNumberInfo = getOtherUpDownNumber('SZ.CYB')
    szSecondBoardOtherData = getOtherData('3990062')
    szSecondBoardIndexInfo = StockIndexInfo(szSecondBoardStockIndexInfo[0], szSecondBoardStockIndexInfo[1],
                                            szSecondBoardStockIndexInfo[2], szSecondBoardNumberInfo[0],
                                            szSecondBoardNumberInfo[2], szSecondBoardNumberInfo[1], szAvgPE[2],
                                            szSecondBoardOtherData)

    # 上证50
    sh50Quotation = jo['quotation'][4]
    sh50StockIndexInfo = sh50Quotation.split(',')
    sh50NumberInfo = getOtherUpDownNumber('IE0000161')
    sh50OtherData = getOtherData('0000161')
    sh50IndexInfo = StockIndexInfo(sh50StockIndexInfo[0], sh50StockIndexInfo[1],
                                   sh50StockIndexInfo[2], sh50NumberInfo[0],
                                   sh50NumberInfo[2], sh50NumberInfo[1], 0,
                                   sh50OtherData)
    # 沪深300
    hs300Quotation = jo['quotation'][5]
    hs300StockIndexInfo = hs300Quotation.split(',')
    hs300NumberInfo = getOtherUpDownNumber('IE0003001')
    hs300OtherData = getOtherData('0003001')
    hs300IndexInfo = StockIndexInfo(hs300StockIndexInfo[0], hs300StockIndexInfo[1],
                                    hs300StockIndexInfo[2], hs300NumberInfo[0],
                                    hs300NumberInfo[2], hs300NumberInfo[1], 0,
                                    hs300OtherData)
    return [shIndexInfo, szIndexInfo, szSMEBoardIndexInfo, szSecondBoardIndexInfo, sh50IndexInfo, hs300IndexInfo]


def getOtherData(code):
    url = 'http://nuff.eastmoney.com/EM_Finance2015TradeInterface/JS.ashx?id=' + code
    res = httpGet(url)
    res = res[9:-1]
    jo = json.loads(res)
    data = jo['Value']
    result = {}
    result['open'] = data[28]  # 开盘
    result['high'] = data[30]  # 最高
    result['low'] = data[32]  # 最低
    result['changePercent'] = data[29]  # 涨跌幅
    result['changeAmount'] = data[27]  # 涨跌额
    result['volume'] = data[31]  # 成交量
    result['amount'] = data[35]  # 成交额
    result['turnOverRatio'] = data[37]  # 换手率
    result['internalPan'] = data[40]  # 内盘
    result['externalPan'] = data[39]  # 外盘
    result['upDownPercent'] = data[50]  # 振幅
    return result


def getOtherUpDownNumber(code):
    url = 'http://nufm3.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=' + code + '&sty=UDFN&st=z&sr=&p=&ps=&token=44c9d251add88e27b65ed86506f6e5da'
    res = httpGet(url)
    res = res[1:-1]
    jo = json.loads(res)
    dataInfo = jo[0].split(',')
    upDownNumberInfo = dataInfo[2].split('|')
    return (upDownNumberInfo[0], upDownNumberInfo[1], upDownNumberInfo[2])  # 涨家数，平家数，跌家数
