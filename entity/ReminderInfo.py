class ReminderInfo:
    def __init__(self, maxPrice, minPrice, upPercent, downPercent, receiver, code, name, buyPrice=0,
                 yesterdayHighPrice=0,
                 yesterdayChangePercent=0,
                 totalChangePercentLast30Days=0):
        self.maxPrice = maxPrice
        self.minPrice = minPrice
        self.upPercent = upPercent
        self.downPercent = downPercent
        self.receiver = receiver
        self.code = code
        self.name = name
        self.buyPrice = buyPrice
        self.yesterdayHighPrice = yesterdayHighPrice
        self.yesterdayChangePercent = yesterdayChangePercent
        self.totalChangePercentLast30Days = totalChangePercentLast30Days
