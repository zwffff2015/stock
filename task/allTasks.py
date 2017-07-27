# coding=utf-8

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))
import tushare as ts

print ts.get_k_data('000001',autype='qfq', start='2014-07-29', end='2014-08-05')

'''os.system("python AvgLinePriceCheckTask.py &")  # 获取每日均线数据，工作日20点以后获取
os.system("python StockIndexTask.py &")  # 获取每日各个主要指数数据，工作日19点以后获取
os.system("python StockTechTask.py &")  # 获取每日各个股票的技术指标数据，工作日19点以后获取
os.system("python StockInfoTask.py &")  # 获取每日各个股票的行情数据，工作日19点以后获取
os.system("python UpdateMADataTask.py &") #更新今日均线数据，工作日20点以后获取
os.system("python RealTimeRemindTask.py &") #启动每日提醒任务
os.system("python DownPercentRemindTask.py &") #启动每日涨跌幅提醒任务
os.system("python StockChooseTask.py &")  # 每周更新PEG数据'''
