# coding:utf-8

import json
import random
import re
import sys
from datetime import datetime, timedelta

from api import tushareApi
from common.HttpHelper import httpGet
from StockTechInfo import StockTechInfo
from StockTechStatus import StockTechStatus
from GainIndexForecast import getGainForecast
from common.LoggerHelper import writeErrorLog, writeWarningLog, writeInfoLog, writeDebugLog, writeLog

reload(sys)
sys.setdefaultencoding('utf-8')


def getPE(code):
    bit = 1 if code.startswith("60") else 2
    url = "http://hqdigi2.eastmoney.com/EM_Quote2010NumericApplication/CompatiblePage.aspx?Type=fs&jsName=js&stk=" + code + str(
        bit) + "&Reference=xml&rt=0.40404130" + str(random.randint(1000000, 9999999))
    res = httpGet(url).decode("utf-8")
    index = res.find("=")
    if (index < 0):
        return
    res = res[7:].replace("skif", "\"skif\"").replace("bsif", "\"bsif\"").replace("dtif", "\"dtif\"").replace("dpif",
                                                                                                              "\"dpif\"")
    jo = json.loads(res[:-1])
    info = jo["skif"].strip().split(",")
    name = info[2]
    pe = info[13]
    # print name, pe
    return (name, pe)


def getPEG(code):
    url = "http://f10.eastmoney.com/f10_v2/IndustryAnalysis.aspx?code=sh" + code + "&timetip=63634083190" + str(
        random.randint(1000000, 9999999))
    res = httpGet(url).decode("utf-8")

    rate = 0
    PEG = 0

    pattern = re.compile(r'id=\"Table2\">.*</table>')
    match = pattern.search(res)

    if match is not None:
        pattern = re.compile(r'<td.*?>(.*?)</td>')
        guzhiData = pattern.findall(match.group())

        if (guzhiData[1] != code):
            "估值比较的股票代码没找到,实际代码：" + code + ",当前代码：" + guzhiData[1]
        else:
            rate = guzhiData[0].replace(",", "")
            PEG = guzhiData[3].replace(",", "")
            PEG = 0 if '--' in PEG else PEG

    pattern = re.compile(r'id=\"Table1\">.*</table>')
    match = pattern.search(res)
    if match is None:
        return (rate, PEG, 0, 0, 0, 0)

    pattern = re.compile(r'<td.*?>(.*?)</td>')
    growthData = pattern.findall(match.group())

    # print growthData

    e2017 = 0
    e2018 = 0
    e2019 = 0
    mixThree = 0

    if (growthData[1] != code):
        writeWarningLog("成长性比较的股票代码没找到,实际代码：" + code + ",当前代码：" + growthData[1])
    else:
        mixThree = growthData[3].replace(",", "")
        e2017 = growthData[6].replace(",", "")
        e2018 = growthData[7].replace(",", "")
        e2019 = growthData[8].replace(",", "")

    return (rate, PEG, mixThree, e2017, e2018, e2019)


def getNAvg(code, days):
    weekday = datetime.today().weekday()
    endDate = datetime.now() if datetime.now().hour >= 19 else datetime.now() - timedelta(days=1)
    if datetime.now().hour >= 19:
        remainDays = days - (weekday + 1 if weekday <= 4 else 5)
    else:
        remainDays = days - (weekday if weekday <= 4 else 5)
    diff = (remainDays / 5) * 7 + (2 if remainDays % 5 != 0 else 0) + remainDays % 5 + weekday + (
        0 if datetime.now().hour >= 19 else -1)
    # print (remainDays / 5) * 7, 2 if remainDays % 5 != 0 else 0, remainDays % 5, weekday, 0 if datetime.now().hour >= 19 else -1

    startDate = endDate - timedelta(days=diff)
    data = tushareApi.getSpecifiedPriceHistoryData(code, startDate.strftime('%Y-%m-%d'), endDate.strftime('%Y-%m-%d'))

    sum = 0
    for date in data:
        sum = sum + data[date]
    # print sum, sum / days, round(sum / days, 2)
    nAvg = round(sum / days, 2)
    return nAvg


def getBiasData(code, days):
    nAvg = getNAvg(code, days)

    '''weekday = datetime.today().weekday()
    datediff = 0
    if weekday % 7 == 0:
        datediff = 3
    elif weekday > 4:
        datediff = weekday - 4
    else:
        datediff = 1

    datediff = 0 if datetime.now().hour >= 19 else datediff
    startdate = (datetime.now() - timedelta(days=datediff)).strftime('%Y-%m-%d')
    print startdate, datediff'''

    today = datetime.now().strftime('%Y-%m-%d')
    data = tushareApi.getOneSpecifiedPriceHistoryData(code, today,
                                                      today) if datetime.now().hour >= 19 else tushareApi.getRealTimeData(
        code)

    if data <= 0:
        writeWarningLog(unicode('未获取到今日收盘价:' + code))
        return 0

    todayClosePrice = float(data)

    # print data, todayClosePrice
    return (todayClosePrice - nAvg) * 100 / nAvg


def getNPrice(code, days, priceType='close'):
    weekday = datetime.today().weekday()
    endDate = datetime.now() if datetime.now().hour >= 19 else datetime.now() - timedelta(days=1)
    if datetime.now().hour >= 19:
        remainDays = days - (weekday + 1 if weekday <= 4 else 5)
    else:
        remainDays = days - (weekday if weekday <= 4 else 5)
    diff = (remainDays / 5) * 7 + (2 if remainDays % 5 != 0 else 0) + remainDays % 5 + weekday + (
        0 if datetime.now().hour >= 19 else -1)
    # print (remainDays / 5) * 7, 2 if remainDays % 5 != 0 else 0, remainDays % 5, weekday, 0 if datetime.now().hour >= 19 else -1

    startDate = endDate - timedelta(days=diff)
    # print startDate, endDate, weekday, remainDays, diff
    return tushareApi.getOneSpecifiedPriceHistoryData(code, startDate.strftime('%Y-%m-%d'),
                                                      endDate.strftime('%Y-%m-%d'),
                                                      priceType) if days == 1 else tushareApi.getSpecifiedPriceHistoryData(
        code, startDate.strftime('%Y-%m-%d'), endDate.strftime('%Y-%m-%d'),
        priceType)


def getNRSV(code, days):
    todayClosePriceInfo = getNPrice('600393', 1)
    todayClosePrice = 0
    for price in todayClosePriceInfo:
        todayClosePrice = todayClosePriceInfo[price]

    max = getNMaxHigh(code, days)
    min = getNMinLow(code, days)
    return round((todayClosePrice - min) * 100 / (max - min), 2)


def getShAvgPe():
    url = "http://www.sse.com.cn/"
    res = httpGet(url)
    # print res
    pattern = re.compile(r'RATIO_OF_PE.*')
    match = pattern.search(res)
    matchData = match.group()
    pattern = re.compile(r'\d+\.\d+')
    pe = pattern.search(matchData).group()
    return round(float(pe), 2)


def getSzAvgPe():
    # sys.setdefaultencoding('gb18030')
    url = "http://www.szse.cn/"
    res = httpGet(url)

    pattern = re.compile(r'<table.*?id=\"REPORTID_tab1\".*?>(.*?)</table>')
    tables = pattern.findall(res)

    PEs = [0, 0, 0]  # [主板，中小板，创业板]
    for i in range(1, len(tables)):
        if tables[i] is not None:
            pattern = re.compile(r'<td.*?>(.*?)</td>')
            tdDatas = pattern.findall(tables[i])
            PEs[i - 1] = round(float(tdDatas[7]), 2)

    return PEs


def getTechParamter(code):
    sys.setdefaultencoding('gbk')
    url = 'http://stock.quote.stockstar.com/tech_' + code + '.shtml'
    res = httpGet(url)

    pattern = re.compile(r'<div class=\"listInfo\">([\s\S]*)</table>')
    tableData = pattern.search(res)

    pattern = re.compile(r'<td.*?>(.*?)</td>')
    tdData = pattern.findall(tableData.group())

    dictData = {}
    dictStatus = {}
    writeLog(unicode("getTech: code: {0}, url:{1}").format(code, url))
    for i in range(0, len(tdData) - 2):
        key = tdData[i].strip()
        data = tdData[i + 1]

        dictData[key] = 0 if '--' in data else data
        dictStatus[key] = unicode(tdData[i + 2])

        # print code, dictData
    stockTechInfo = StockTechInfo(code, dictData)

    pattern = re.compile(r'<p class=\"lf\">(.*?)</p>')
    techStatus = pattern.search(res)

    bulls = 0
    bears = 0
    notsure = 0
    if techStatus is not None:
        pattern = re.compile(r'\d+')
        numbers = pattern.findall(techStatus.group())
        if numbers is not None:
            bulls = numbers[1]
            bears = numbers[2]
            notsure = numbers[3]

    stockTechStatus = StockTechStatus(code, dictStatus, bulls, bears, notsure)
    forecastInfo = getGainForecast(stockTechStatus)
    return (stockTechInfo, stockTechStatus, forecastInfo)


def getStockInfo(code):
    bit = 1 if code.startswith("60") else 2
    url = 'http://nuff.eastmoney.com/EM_Finance2015TradeInterface/JS.ashx?id=' + code + str(bit) + '&_=149941' + str(
        random.randint(1000000, 9999999))
    res = httpGet(url)
    res = res[9:-1]
    writeLog(unicode("getStockInfo, url:{0}, resule:{1} ").format(url, res))
    jo = json.loads(res)
    data = jo['Value']

    result = {}
    result['limitUp'] = data[23]
    result['limitDown'] = data[24]
    result['avgPrice'] = data[26]
    result['volume'] = data[31]
    result['amount'] = data[35]
    result['highPrice'] = data[30]
    result['lowPrice'] = data[32]
    result['openPrice'] = data[28]
    result['closePrice'] = data[25]
    result['changePercent'] = data[29]
    result['changeAmount'] = data[27]
    result['turnOverRatio'] = data[37]
    result['QRR'] = data[36]
    result['totalValue'] = data[46]
    result['circulatedValue'] = data[45]
    result['PE'] = 0 if data[38] == '-' else data[38]
    result['PTB'] = 0 if data[43] == '-' else data[43]
    result['internalPan'] = data[40]
    result['externalPan'] = data[39]
    result['code'] = code

    return None if float(result['closePrice']) == 0 else result


def getNMaxHigh(code, days):
    priceInfo = getNPrice(code, days, priceType='high')
    # print priceInfo
    max = 0
    for price in priceInfo:
        if (priceInfo[price] > max):
            max = priceInfo[price]

    return max


def getNMinLow(code, days):
    priceInfo = getNPrice(code, days, priceType='low')
    min = 9999999
    for price in priceInfo:
        if (priceInfo[price] < min):
            min = priceInfo[price]

    return min


def getNQuShi(code, days):
    priceInfo = getNPrice(code, days)
    maN = getNAvg(code, days)

    downTimes = 0  # 下行趋势次数
    upTimes = 0  # 上行趋势次数
    currentMaxDownTimes = 0  # 当前最大连续下行次数
    maxDownTimes = 0  # 最大连续下行次数
    maxDownStartIndex = 0  # 最大连续下行趋势起始位置
    currentMaxUpTimes = 0  # 当前最大连续上行次数
    maxUpTimes = 0  # 最大连续上行次数
    maxUpStartIndex = 0  # 最大连续上行趋势起始位置
    preStatus = -1  # 上一次趋势，上行或下行，-1：未定义，0：下行，1：上行
    lastStatus = -1  # 最后一次趋势，上行或下行，-1：未定义，0：下行，1：上行
    currentMaxLessAvgTimes = 0  # 当前最大连续小于均线次数
    maxLessAvgTimes = 0  # 最大连续小于均线次数
    maxLessAvgStartIndex = 0  # 最大连续小于均线趋势起始位置

    for i in range(0, len(priceInfo.keys()) - 1):
        price = priceInfo[priceInfo.keys()[i]]
        price1 = priceInfo[priceInfo.keys()[i + 1]]

        if (i == len(priceInfo.keys()) - 2):
            if (price <= price1):
                lastStatus = 1
            else:
                lastStatus = 0

        if (price <= maN):
            maxLessAvgTimes = maxLessAvgTimes + 1
            if (maxLessAvgTimes > currentMaxLessAvgTimes):
                maxLessAvgStartIndex = i - maxLessAvgTimes + 1
                currentMaxLessAvgTimes = maxLessAvgTimes
        else:
            maxLessAvgTimes = 0

        # print price, price1
        if (price <= price1):
            # 上行趋势
            upTimes = upTimes + 1
            if (preStatus != 1):
                preStatus = 1
                if (maxDownTimes > currentMaxDownTimes):
                    maxDownStartIndex = i - maxDownTimes
                    currentMaxDownTimes = maxDownTimes
                maxDownTimes = 0
            maxUpTimes = maxUpTimes + 1

        else:
            # 下行趋势
            downTimes = downTimes + 1
            if (preStatus != 0):
                preStatus = 0
                if (maxUpTimes > currentMaxUpTimes):
                    maxUpStartIndex = i - maxUpTimes
                    currentMaxUpTimes = maxUpTimes
                maxUpTimes = 0
            maxDownTimes = maxDownTimes + 1

            # print downTimes, upTimes, currentMaxDownTimes, maxDownStartIndex, currentMaxUpTimes, maxUpStartIndex, currentMaxLessAvgTimes, maxLessAvgStartIndex, lastStatus
