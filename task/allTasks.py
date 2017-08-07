# coding=utf-8

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))

os.system("python AvgLinePriceCheckTask.py &")  # 获取每日均线数据，工作日20点以后获取
os.system("python StockIndexTask.py &")  # 获取每日各个主要指数数据，工作日19点以后获取
os.system("python StockTechTask.py &")  # 获取每日各个股票的技术指标数据，工作日22点以后获取
os.system("python StockInfoTask.py &")  # 获取每日各个股票的行情数据，工作日19点以后获取
os.system("python UpdateMADataTask.py &") #更新今日均线数据，工作日21点以后获取
os.system("python UpdateBiasDataTask.py &") #更新今日bias数据，工作日21点以后获取
os.system("python RealTimeRemindTask.py &") #启动每日提醒任务，工作日9点以后启动
os.system("python DownPercentRemindTask.py &") #启动每日涨跌幅提醒任务，工作日9点以后启动
os.system("python StockChooseTask.py &")  # 每周更新PEG数据


# 更新股票名称
'''
initMysql()
sql = unicode("SELECT code from s_stock_tech GROUP by code order by code asc")
data = select(sql)

for item in data:
    code = item[0]
    name = getPE(code)[0]
    print code, name
    addSql = unicode("insert into s_stock_info(code,name) values('{0}','{1}')").format(code, name)
    execute(addSql)
'''