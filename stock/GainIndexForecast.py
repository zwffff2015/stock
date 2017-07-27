# coding:utf-8

from StockTechStatus import StockTechStatus

# 指标分类，0：趋向指标，1：能量指标，2：超买超卖指标，3：成交量指标
indexType = {'MACD': 0, 'DMI': 0, 'DMA': 0, 'EMV': 0, 'EXPMA': 0, 'TRIX': 0, 'WVAD': 0, 'VR': 1, 'CR': 1, 'AR': 1,
             'PSY': 1, 'KDJ': 2, 'RSI': 2, 'MTM': 2, 'WR': 2, 'CCI': 2, 'OBV': 3}


def getGainForecast(stockTechStatus):
    maxBulls = getMaxBulls(stockTechStatus)
    bullsShow = getBullsShow(stockTechStatus)

    BGB = stockTechStatus.bulls > stockTechStatus.bears  # 多头大于空头
    BGB_DIFF4 = stockTechStatus.bulls > stockTechStatus.bears and stockTechStatus.bulls - stockTechStatus.bears >= 4  # 多头大于空头，且相差4以上
    TrendMax = maxBulls[0]  # 趋向指标多头数量最多
    EnergyMax = maxBulls[1]  # 能量指标多头数量最多
    OBOSMax = maxBulls[2]  # 超买超卖指标多头数量最多
    TrendEnergyShow = bullsShow[0] and bullsShow[1]  # 趋向指标和能量指标同时出现多头
    TrendOBOSShow = bullsShow[0] and bullsShow[2]  # 趋向指标和超买超卖指标同时出现多头
    EnergyOBOSShow = bullsShow[1] and bullsShow[2]  # 能量指标和超买超卖指标同时出现多头
    TrendEnergyOBOSShow = bullsShow[0] and bullsShow[1] and bullsShow[2]  # 趋向指标、能量指标和超买超卖指标同时出现多头
    TE_BGBShow = bullsShow[0] and bullsShow[
        1] and stockTechStatus.bulls > stockTechStatus.bears  # 趋向指标和能量指标同时出现多头，且总多头大于空头
    TOBOS_BGBShow = bullsShow[0] and bullsShow[
        2] and stockTechStatus.bulls > stockTechStatus.bears  # 趋向指标和超买超卖指标同时出现多头，且总多头大于空头
    EOBOS_BGBShow = bullsShow[1] and bullsShow[
        2] and stockTechStatus.bulls > stockTechStatus.bears  # 能量指标和超买超卖指标同时出现多头，且总多头大于空头
    TEOBOS_BGBShow = bullsShow[0] and bullsShow[1] and bullsShow[
        2] and stockTechStatus.bulls > stockTechStatus.bears  # 趋向指标、能量指标和超买超卖指标同时出现多头，且总多头大于空头
    AllBulls = stockTechStatus.bulls > 0 and stockTechStatus.bears == 0  # 全部是多头
    AllBulls_DIFF4 = stockTechStatus.bulls > 0 and stockTechStatus.bears == 0 and stockTechStatus.bulls - stockTechStatus.bears >= 4  # 全部是多头，且相差4以上

    forecastInfo = ForecastInfo(BGB, BGB_DIFF4, TrendMax, EnergyMax, OBOSMax, TrendEnergyShow, TrendOBOSShow,
                                EnergyOBOSShow,
                                TrendEnergyOBOSShow, TE_BGBShow, TOBOS_BGBShow, EOBOS_BGBShow, TEOBOS_BGBShow, AllBulls,
                                AllBulls_DIFF4)
    return forecastInfo


'''
    获取趋向指标、能量指标和超买超卖指标，多头数量最多的情况
    考虑到最多的情况，可能会同时出现多种，因此返回结果为数量为4的数组
    格式为：[趋向指标是否最多，能量指标是否最多，超买超卖指标是否最多，成交量指标是否最多]
'''


def getMaxBulls(stockTechStatus):
    typeCount = [0, 0, 0, 0]  # 各个指标分类，多头数量，位置对应关系（0：趋向指标，1：能量指标，2：超买超卖指标，3：成交量指标）
    for item in indexType:
        #print item, getattr(stockTechStatus, item)
        type = indexType[item]  # 所属指标分类
        if getattr(stockTechStatus, item) == 0:  # 属于多头预测
            typeCount[type] = typeCount[type] + 1

    maxCount = max(typeCount)
    return [True if x == maxCount else False for x in typeCount]


'''
    获取各个指标分类出现多头的情况，返回结果为数量为4的数组
    格式为：[趋向指标是否出现多头，能量指标是否出现多头，超买超卖指标是否出现多头，成交量指标是否出现多头]
'''


def getBullsShow(stockTechStatus):
    typeBullsShow = [False, False, False, False]  # 各个指标分类是否出现多头，位置对应关系（0：趋向指标，1：能量指标，2：超买超卖指标，3：成交量指标）
    for item in indexType:
        type = indexType[item]  # 所属指标分类
        if typeBullsShow[type] == False and getattr(stockTechStatus, item) == 0:
            typeBullsShow[type] = True

    return typeBullsShow


def trueConvertToZero(data):
    return 0 if data else 1


class ForecastInfo:
    def __init__(self, BGB, BGB_DIFF4, TrendMax, EnergyMax, OBOSMax, TrendEnergyShow, TrendOBOSShow, EnergyOBOSShow,
                 TrendEnergyOBOSShow, TE_BGBShow, TOBOS_BGBShow, EOBOS_BGBShow, TEOBOS_BGBShow, AllBulls,
                 AllBulls_DIFF4):
        self.BGB = trueConvertToZero(BGB)
        self.BGB_DIFF4 = trueConvertToZero(BGB_DIFF4)
        self.TrendMax = trueConvertToZero(TrendMax)
        self.EnergyMax = trueConvertToZero(EnergyMax)
        self.OBOSMax = trueConvertToZero(OBOSMax)
        self.TrendEnergyShow = trueConvertToZero(TrendEnergyShow)
        self.TrendOBOSShow = trueConvertToZero(TrendOBOSShow)
        self.EnergyOBOSShow = trueConvertToZero(EnergyOBOSShow)
        self.TrendEnergyOBOSShow = trueConvertToZero(TrendEnergyOBOSShow)
        self.TEOBOS_BGBShow = trueConvertToZero(TEOBOS_BGBShow)
        self.TE_BGBShow = trueConvertToZero(TE_BGBShow)
        self.EOBOS_BGBShow = trueConvertToZero(EOBOS_BGBShow)
        self.TOBOS_BGBShow = trueConvertToZero(TOBOS_BGBShow)
        self.AllBulls = trueConvertToZero(AllBulls)
        self.AllBulls_DIFF4 = trueConvertToZero(AllBulls_DIFF4)
