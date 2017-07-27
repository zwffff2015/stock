# coding=utf-8

import sys
from wechat_sender import Sender
from common.LoggerHelper import writeDebugLog, writeInfoLog, writeWarningLog, writeErrorLog, writeLog

SENDER = None


def sendMessageToBaby(message):
    sendMessage('期待', message)


def sendMessageToMySelf(message):
    sendMessage('踏雪', message)


def sendMessage(receiver, message):
    try:
        global SENDER
        if SENDER is None:
            initWeChatSender()

        SENDER.sendWeChatMessage(receiver, message)
    except Exception, e:
        writeErrorLog(unicode("send message error: {0}").format(str(e)))


def initWeChatSender():
    global SENDER
    SENDER = weChatSender('47.95.6.27', '295cc3d8-c977-11e6-a341-0090f5f61084', '9090', ['踏雪', '期待'])


class weChatSender:
    def __init__(self, host, token, port, senderList):
        reload(sys)
        sys.setdefaultencoding('utf-8')

        self.host = host
        self.token = token
        self.port = port

        dictSender = {}
        for sender in senderList:
            dictSender[sender] = Sender(token=token, receivers=unicode(sender), host='http://' + host, port=port)

        self.senders = dictSender

    def sendWeChatMessage(self, receiver, message):
        try:
            if self.senders.has_key(receiver):
                self.senders.get(receiver).send(message)
            else:
                writeWarningLog('sender is not exist: receiver: {0}, message: {1}'.format(receiver, message))
        except Exception, e:
            writeErrorLog('send we chat failed: receiver: {0}, message: {1}, e: {2}'.format(receiver, message, str(e)))
