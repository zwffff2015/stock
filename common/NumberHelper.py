# coding=utf-8
import math
import decimal

'''
    保留两位小数，如果第三位小数大于0，则小数第二位加1，最后再舍弃第三位小数
    比如2.342会返回2.35，2.456会返回2.46
'''


def getAboveNumber(number):
    remainder = number * 1000 % 10
    data = number + 0.01 if remainder > 0 else number
    return math.floor(data * 100) / 100


'''
    保留N位小数，其余舍弃
'''


def getFloat(number, pointNumber=2):
    data = math.pow(10, pointNumber)
    result = math.floor(float(number) * data) / data
    return result


def getRound(number, pointNumber=2):
    data = math.floor(float(number) * math.pow(10, pointNumber + 1)) % 10
    return round(number, pointNumber) if data != 5 else getFloat(number, pointNumber)


def getDicValue(dic, key):
    result = -1 if dic == None else (dic.get(key) if dic.has_key(key) else -1)
    if result == '':
        return -1
    return result
