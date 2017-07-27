import os
from datetime import datetime


def writeFile(fileName, data):
    file_object = open(fileName, 'w')
    file_object.writelines(data)
    file_object.close()


def saveFile(fileName, content):
    folderPath = os.path.abspath(
        os.path.join(os.getcwd(), "../data/" + datetime.now().strftime('%Y-%m-%d'))) + os.sep
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
    saveFileName = folderPath + fileName
    writeFile(saveFileName, content)
