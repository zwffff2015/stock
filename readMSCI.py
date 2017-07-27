# coding=utf-8

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))
from common.JsonHelper import loadJsonConfig


def loadMSCIStock(fileName):
    index = 1
    result = '['
    for line in open(fileName):
        line = line.strip()
        if (line == ''):
            continue

        indexLength = len(str(index))
        code = line[indexLength:indexLength + 6]
        index = index + 1
        result = result + '"' + code + '",'
    #print index
    return result


def main(argv):
    result = loadMSCIStock("msci.txt")
    print result

if __name__ == '__main__':
    main(sys.argv)
