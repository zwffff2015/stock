from common.StringHelper import toInt


class StockTechStatus:
    def __init__(self, code, dictStatus, bulls, bears, notsure):
        self.code = code
        self.MACD = toInt(dictStatus['MACD'])
        self.DMI = toInt(dictStatus['ADX'])
        self.DMA = toInt(dictStatus['DMA'])
        self.EXPMA = toInt(dictStatus['EXPMA1'])
        self.EMV = toInt(dictStatus['EMV'])
        self.TRIX = toInt(dictStatus['TRIX'])
        self.WVAD = toInt(dictStatus['WVAD'])
        self.VR = toInt(dictStatus['VR'])
        self.CR = toInt(dictStatus['CR'])
        self.AR = toInt(dictStatus['AR'])
        self.PSY = toInt(dictStatus['PSY'])
        self.KDJ = toInt(dictStatus['K'])
        self.RSI = toInt(dictStatus['RSI1'])
        self.MTM = toInt(dictStatus['MTM'])
        self.WR = toInt(dictStatus['W&R'])
        self.CCI = toInt(dictStatus['CCI'])
        self.OBV = toInt(dictStatus['OBV'])
        self.bulls = int(bulls)
        self.bears = int(bears)
        self.notsure = int(notsure)
