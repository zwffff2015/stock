# coding=utf-8
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))

from common.FileHelper import writeFile
from stock.StockInfo import getPE, getNAvg, getNPrice, getBiasData
from datetime import datetime, timedelta
from db.MysqlUtil import select, initMysql, disconnect
from common.LoggerHelper import writeLog


def main(argv):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    initMysql()
    codeList = ['600758', '600393', '601318', '600282', '600029']

    result = []
    result.append(
        unicode("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13}\n").format("代码", "名称", "ma5", "ma10",
                                                                                        "ma20",
                                                                                        "ma30", "ma60", "ma120",
                                                                                        "ma200",
                                                                                        "ma240", "BIAS1（6日）",
                                                                                        "BIAS2（12日）",
                                                                                        "BIAS3（24日）", "10收盘价").encode(
            'gbk'))
    date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    for code in codeList:
        sql = unicode(
            "SELECT code,date,MA5,MA10,MA20,MA30,MA60,MA120,MA250,closePrice from s_stock where code='{0}' and date='{1}'").format(
            code, date)
        data = select(sql)

        if (len(data) <= 0):
            (unicode("没有获取到均值数据, code: {0}, date: {1}").format(code, date))
            i = i + 1
            continue

        ma5 = data[0][2]
        ma10 = data[0][3]
        ma30 = data[0][5]
        ma60 = data[0][6]
        ma120 = data[0][7]
        ma250 = data[0][8]
        closePrice = float(data[0][9])

        nvg6 = getMAData(6, code, date)
        nvg12 = getMAData(12, code, date)
        nvg24 = getMAData(24, code, date)

        bias1 = round((closePrice - nvg6) * 100 / nvg6, 2)
        bias2 = round((closePrice - nvg12) * 100 / nvg12, 2)
        bias3 = round((closePrice - nvg24) * 100 / nvg24, 2)

        peInfo = getPE(code)


def getMAData(dayCount, code, date):
    sql = unicode(
        "select if(count(*)<{0},0,sum(closePrice)/{0}) from ( select closePrice from s_stock where code='{1}' and date<='{2}' order by timestamp desc limit {0}) as t").format(
        dayCount, code, date)
    data = select(sql)
    if len(data) <= 0:
        return 0
    else:
        return float(data[0][0])


if __name__ == '__main__':
    main(sys.argv)
