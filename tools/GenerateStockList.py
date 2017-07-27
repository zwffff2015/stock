# coding=utf-8

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))
from common.FileHelper import writeFile
from datetime import datetime
import shutil
import json


def loadStockList(fileName):
    dictData = {}
    for line in open(fileName):
        line = line.strip().zfill(6)
        if line not in dictData:
            dictData[line] = 1

    saveFileName = os.path.abspath(
        os.path.join(os.getcwd(), "../config/goodStockList.json"))
    backupFileName = os.path.abspath(
        os.path.join(os.getcwd(), "../backup/goodStockList_" + datetime.now().strftime('%Y-%m-%d') + ".json"))
    if os.path.exists(saveFileName):
        shutil.move(saveFileName, backupFileName)

    writeFile(saveFileName, json.dumps(dictData.keys()))


def main(argv):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    loadStockList('goodStocks.txt')


if __name__ == '__main__':
    main(sys.argv)
