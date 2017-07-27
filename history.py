import sys
import time
from datetime import datetime, timedelta
from common.LoggerHelper import writeLog
from wechat_sender import Sender

from api import tushareApi as ts

SENDER = None


class StockData:
    def __init__(self, maxHigh, minLow, avg):
        self.maxHigh = maxHigh
        self.minLow = minLow
        self.avg = avg


class ReportInfo:
    def __init__(self, message):
        self.message = message


def getHighLowData(code):
    today = datetime.now()
    threeYearsAgo = today - timedelta(days=365 * 5)
    data = getHistoryData(code, threeYearsAgo.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
    totalHigh = 0
    maxHigh = 0
    for date in data[0]:
        totalHigh = totalHigh + data[0][date]
        if (data[0][date] > maxHigh):
            maxHigh = data[0][date]

    totalLow = 0
    minLow = 9999999
    for date in data[1]:
        totalLow = totalLow + data[1][date]
        if (data[1][date] < minLow):
            minLow = data[1][date]

    avg = (totalHigh + totalLow) / (2 * len(data[0]))
    avg = round(float(avg), 2)
    writeLog(unicode("股票代码：{5}，三年最高价：{0}，最低价：{1}，均价：{2}，最高价均价：{3}，最低价均价：{4}").format(maxHigh, minLow, avg,
                                                                                     round(float(
                                                                                         totalHigh / len(data[0])),
                                                                                         2),
                                                                                     round(
                                                                                         float(totalLow / len(data[1])),
                                                                                         2), code))
    # totalHigh,maxHigh,len(data[0]),totalLow,minLow,len(data[1])
    return StockData(maxHigh, minLow, avg)


def getHistoryData(code, start, end):
    # print code,start,end
    data = ts.get_k_data(code, ktype='D', autype='qfq', start=start, end=end)
    highList = dict(data['high'])
    lowList = dict(data['low'])
    return highList, lowList


def initWeChat():
    host = 'http://127.0.0.1'
    token = '295cc3d8-c977-11e6-a341-0090f5f61084'
    global SENDER
    SENDER = Sender(token=token, receivers=unicode('踏雪'), host=host, port='9090')


def sendWeChatMessage(message):
    global SENDER
    SENDER.send(message)


def main(argv):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    initWeChat()

    codeList = ['601318', '601939', '600282', '601166', '601633', '000002', '600104', '600393', '600029', '600971',
                '600581', '600758']
    boughtList = {'601318': 49.101, '600393': 7.493, '600282': 3.65, '600029': 8.91}
    stockDatas = {}
    for code in codeList:
        stockData = getHighLowData(code)
        stockDatas[code] = stockData
    # print '\n'

    sendAlready = {}
    while 1 == 1:
        importantData = []
        for code in codeList:
            df = ts.get_realtime_quotes(code)
            writeLog(
                unicode("代码：{0}，名称：{1}，三年最高价：{2}，最低价：{3}，均价：{4}，当前价格：{5}，竞买价：{6}，竞卖价：{7}，成交量：{8}，成交金额：{9} ").format(
                    code, df['name'].values[0], stockDatas[code].maxHigh, stockDatas[code].minLow, stockDatas[code].avg,
                    df['price'].values[0], df['bid'].values[0], df['ask'].values[0], df['volume'].values[0],
                    df['amount'].values[0]))

            canBuyPrice = float(stockDatas[code].avg * 0.8)
            canSellPrice = float(stockDatas[code].avg * 1.5)

            if (float(df['bid'].values[0]) <= canBuyPrice):
                msg = unicode('代码：{2}，名称：{3}，当前买入价为: {0}, 历史均价为：{1}, 买入价小于均价的80%，可以考虑买入\n').format(df['bid'].values[0],
                                                                                                   stockDatas[code].avg,
                                                                                                   code,
                                                                                                   df['name'].values[0])
                importantData.append(msg)

            if (float(df['ask'].values[0]) >= canSellPrice):
                msg = unicode('代码：{2}，名称：{3}，当前卖出价为: {0}, 历史均价为：{1}, 卖出价大于均价的150%，可以考虑卖出\n').format(df['ask'].values[0],
                                                                                                    stockDatas[
                                                                                                        code].avg, code,
                                                                                                    df['name'].values[
                                                                                                        0])
                importantData.append(msg)

            if boughtList.has_key(code):
                # print float(df['ask'].values[0]),float(boughtList[code])
                if (float(df['ask'].values[0]) >= float(boughtList[code])):
                    msg = unicode('代码：{2}，名称：{3}，当前卖出价为: {0}, 成本为：{1}, 可以考虑卖出\n').format(df['ask'].values[0],
                                                                                         boughtList[code], code,
                                                                                         df['name'].values[0])
                    importantData.append(msg)

        sendWeChatMessage('\n'.join(importantData))
        time.sleep(30)


if __name__ == '__main__':
    main(sys.argv)
