#!/bin/bash

source activate python27

python AvgLinePriceCheckTask.py &  # 获取每日均线数据，工作日20点以后获取
python StockIndexTask.py &  # 获取每日各个主要指数数据，工作日19点以后获取
python StockTechTask.py &  # 获取每日各个股票的技术指标数据，工作日22点以后获取
python StockInfoTask.py &  # 获取每日各个股票的行情数据，工作日19点以后获取
python UpdateMADataTask.py & #更新今日均线数据，工作日21点以后获取
python UpdateBiasDataTask.py & #更新今日bias数据，工作日21点以后获取
python RealTimeRemindTask.py & #启动每日提醒任务，工作日9点以后启动
python DownPercentRemindTask.py & #启动每日涨跌幅提醒任务，工作日9点以后启动
python StockChooseTask.py &  # 每周更新PEG数据
