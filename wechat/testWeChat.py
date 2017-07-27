import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))

from wxpy import *
from wechat_sender import *
from common.LoggerHelper import writeLog, writeErrorLog

reload(sys)
sys.setdefaultencoding('utf-8')

try:
    bot = Bot('bot.pkl', console_qr=True)
    master = ensure_one(bot.friends().search(unicode('踏雪')))
    log_group = ensure_one(bot.friends().search(unicode('期待')))
    token = '295cc3d8-c977-11e6-a341-0090f5f61084'
    writeLog(unicode("receiver: {0}, {1}").format(master, log_group))
    listen(bot, [master, log_group], token=token, port=9090, status_report=True, status_receiver=master)
except Exception, e:
    writeErrorLog(unicode("receive message error: {0}").format(str(e)))
