import tushare as ts


def getOneSpecifiedPriceHistoryData(code, start, end, priceType='close'):
    data = getSpecifiedPriceHistoryData(code, start, end, priceType)
    # print data
    for item in data:
        return data[item]


def getSpecifiedPriceHistoryData(code, start, end, priceType='close'):
    # print code, start, end
    data = ts.get_k_data(code, ktype='D', autype='qfq', start=start, end=end)
    if len(data) <= 0:
        return dict({'default': 0})
    closeList = dict(data[priceType])
    return closeList


def getRealTimeData(code, priceType='price'):
    data = ts.get_realtime_quotes(code)
    # print data
    if data is None:
        return 0
    priceList = data[priceType].values[0]
    return priceList


def getSimpleHistoryData(code, start, end):
    data = ts.get_k_data(code, ktype='D', autype='qfq', start=start, end=end)
    if len(data) <= 0:
        return None
    return data


def getHistoryData(code, start, end):
    data = ts.get_hist_data(code, ktype='D', start=start, end=end)
    if len(data) <= 0:
        return None
    return data
