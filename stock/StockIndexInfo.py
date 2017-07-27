class StockIndexInfo:
    def __init__(self, code, name, index, upNumber, downNumber, equalNumber, avgPE, result):
        self.code = code
        self.name = name
        self.index = index
        self.upNumber = upNumber
        self.downNumber = downNumber
        self.equalNumber = equalNumber
        self.avgPE = avgPE
        self.open = result['open']
        self.high = result['high']
        self.low = result['low']
        self.changePercent = result['changePercent']
        self.changeAmount = result['changeAmount']
        self.volume = result['volume']
        self.amount = result['amount']
        self.turnOverRatio = result['turnOverRatio']
        self.internalPan = result['internalPan']
        self.externalPan = result['externalPan']
        self.upDownPercent = result['upDownPercent']
