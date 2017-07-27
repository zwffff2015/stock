# coding=utf-8
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def toInt(status):
    status = status.strip()
    if status == '多头排列'.decode('utf8'):
        return 0
    elif status == '空头排列'.decode('utf8'):
        return 1
    elif status == '不确定'.decode('utf8'):
        return 2
    else:
        return -1


def toString(status):
    if status == 0:
        return unicode('多头排列')
    elif status == 1:
        return unicode('空头排列')
    elif status == 2:
        return unicode('不确定')
    else:
        return unicode('其他')
