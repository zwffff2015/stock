import sys
from wechat_sender import Sender

reload(sys)  
sys.setdefaultencoding('utf-8')

host = 'http://47.95.6.27'
token = '295cc3d8-c977-11e6-a341-0090f5f61084'
sender = Sender(token=token, receivers=unicode('踏雪'), host=host, port='9090')
sender.send('阿斯蒂芬')