#!/bin/bash

source activate python27

python AvgLinePriceCheckTask.py &  # 获取每日均线数据，工作日20点以后获取
python StockIndexTask.py &  # 获取每日各个主要指数数据，工作日19点以后获取
python StockTechTask.py &  # 获取每日各个股票的技术指标数据，工作日19点以后获取
python StockInfoTask.py &  # 获取每日各个股票的行情数据，工作日19点以后获取
python UpdateMADataTask.py & #更新今日均线数据，工作日20点以后获取
python RealTimeRemindTask.py & #启动每日提醒任务
python DownPercentRemindTask.py & #启动每日涨跌幅提醒任务
python StockChooseTask.py &  # 每周更新PEG数据
