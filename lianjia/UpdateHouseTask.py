# coding=utf-8

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))

import json
import re
import time
import random

import traceback
from common.FileHelper import saveFile, writeFile
from common.HttpHelper import httpGet
from api.GDMapApi import getDistanceAndTime, getGeoCodes, getDistanceAndTimeByLngLat, getDirectionByLngLat
from common.FileHelper import saveFile, writeFile


def getHouseListByPage(page):
    url = "https://tj.lianjia.com/ershoufang/pg" + str(page) + "co32sf1ba45ea10000ep131"
    res = httpGet(url, {'Host': 'tj.lianjia.com',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                        'Cookie': 'lianjia_uuid=dfcb3cfc-1367-44d0-ab71-a4371c024f14; _jzqy=1.1497172963.1497172963.1.jzqsr=baidu|jzqct=%E9%93%BE%E5%AE%B6.-; UM_distinctid=15c96766dee1d-02c0d24031f09b-57e1b3c-100200-15c96766def2d0; lianjia_token=2.001caa2ee5666b6ddd0d0707d40582481c; Hm_lvt_efa595b768cc9dc7d7f9823368e795f1=1497173127; select_city=120000; all-lj=6341ae6e32895385b04aae0cf3d794b0; _jzqx=1.1501484606.1501816686.2.jzqsr=tj%2Elianjia%2Ecom|jzqct=/ershoufang/co32sf1ep131/.jzqsr=captcha%2Elianjia%2Ecom|jzqct=/; _jzqckmp=1; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1501566186,1501632151,1501727320,1501816685; Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1501817428; _smt_uid=593d0be2.3137f8c0; CNZZDATA1253477585=1433138464-1497169384-null%7C1501812237; CNZZDATA1254525948=1005085447-1497168099-null%7C1501812362; CNZZDATA1255633284=2082143268-1497171373-null%7C1501817197; CNZZDATA1255604082=911884105-1497168620-null%7C1501813499; _qzja=1.1430239548.1497172962788.1501727321514.1501816685601.1501817373141.1501817428734.0.0.0.86.20; _qzjb=1.1501816685601.5.0.0.0; _qzjc=1; _qzjto=5.1.0; _jzqa=1.3807096351994737700.1497172963.1501727322.1501816686.20; _jzqc=1; _jzqb=1.5.10.1501816686.1; _ga=GA1.2.457334799.1497172965; _gid=GA1.2.1962824039.1501816690; lianjia_ssid=11e953d7-b086-4fcf-a424-b43314c76cca'})

    pattern = re.compile(r'<ul class=\"sellListContent\".*?>(.*?)</ul>')
    contentUl = pattern.search(res)

    pattern = re.compile(r'<li[^>]*?>([\s\S]*?)</li>')
    houseInfoList = pattern.findall(contentUl.group())

    pattern = re.compile(r'\"totalPage\":(.*?),')
    totalPages = pattern.findall(res)

    totalPages = 0 if len(totalPages) <= 0 else totalPages[0]
    return (totalPages, houseInfoList)


def handleHouseList(houseInfoList, geoCodeHome, geoCodeHerOffice, geoCodeMyOffice, result, i):
    for houseInfo in houseInfoList:
        print houseInfo
        print i
        i = i + 1
        if i < 14:
            continue
        try:
            pattern = re.compile(r'<div class=\"houseInfo\">([\s\S]*?)</div>')
            houseInfoDiv = pattern.findall(houseInfo)[0]

            pattern = re.compile(r'<a[^>]*?>([\s\S]*?)</a>')
            village = pattern.findall(houseInfoDiv)[0].strip()  # 小区名称

            other = re.subn(r'<[span|a][^>]*?>([\s\S]*?)</[span|a]>', '', houseInfoDiv)[0]

            pattern = re.compile(r'<div class=\"positionInfo\">([\s\S]*?)</div>')
            positionInfoDiv = pattern.findall(houseInfo)[0]

            pattern = re.compile(r'<a[^>]*?>([\s\S]*?)</a>')
            street = pattern.findall(positionInfoDiv)[0].strip()  # 街道名称

            pattern = re.compile(r'<span class=\"subway\">([\s\S]*?)</span>')
            subwayInfo = pattern.findall(houseInfo)
            subwayInfo = '' if len(subwayInfo) <= 0 else subwayInfo[0].strip()  # 地铁信息
            lineIndex = subwayInfo.find('线')
            stationIndex = subwayInfo.find('站')
            subway = ''
            if (lineIndex >= 0 and stationIndex >= 0):
                subway = subwayInfo[lineIndex + 3:stationIndex]

            pattern = re.compile(r'<div class=\"totalPrice\"><span>([\s\S]*?)</span>')
            totalPrice = pattern.findall(houseInfo)[0]  # 总价

            pattern = re.compile(r'<div class=\"unitPrice\".*?><span>([\s\S]*?)</span>')
            unitPrice = pattern.findall(houseInfo)[0][6:-10]  # 单价

            pattern = re.compile(r'<div class=\"followInfo\"><span.*?></span>([\s\S]*?)</div>')
            dateInfo = pattern.findall(houseInfo)  # 发布时间
            dateInfo = dateInfo[0].split('/')[2]

            pattern = re.compile(r'<a class=\"img \" href=\"(.*?)\"')
            linkUrl = pattern.findall(houseInfo)[0]

            linkRes = httpGet(linkUrl, {
                'Cookie': 'lianjia_uuid=dfcb3cfc-1367-44d0-ab71-a4371c024f14; _jzqy=1.1497172963.1497172963.1.jzqsr=baidu|jzqct=%E9%93%BE%E5%AE%B6.-; UM_distinctid=15c96766dee1d-02c0d24031f09b-57e1b3c-100200-15c96766def2d0; lianjia_token=2.001caa2ee5666b6ddd0d0707d40582481c; Hm_lvt_efa595b768cc9dc7d7f9823368e795f1=1497173127; select_city=120000; all-lj=6341ae6e32895385b04aae0cf3d794b0; _jzqx=1.1501484606.1501816686.2.jzqsr=tj%2Elianjia%2Ecom|jzqct=/ershoufang/co32sf1ep131/.jzqsr=captcha%2Elianjia%2Ecom|jzqct=/; _jzqckmp=1; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1501566186,1501632151,1501727320,1501816685; Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1501817441; _smt_uid=593d0be2.3137f8c0; CNZZDATA1253477585=1433138464-1497169384-null%7C1501812237; CNZZDATA1254525948=1005085447-1497168099-null%7C1501812362; CNZZDATA1255633284=2082143268-1497171373-null%7C1501817197; CNZZDATA1255604082=911884105-1497168620-null%7C1501813499; _qzja=1.1430239548.1497172962788.1501727321514.1501816685601.1501817428734.1501817441713.0.0.0.87.20; _qzjb=1.1501816685601.6.0.0.0; _qzjc=1; _qzjto=6.1.0; _jzqa=1.3807096351994737700.1497172963.1501727322.1501816686.20; _jzqc=1; _jzqb=1.6.10.1501816686.1; _ga=GA1.2.457334799.1497172965; _gid=GA1.2.1962824039.1501816690; lianjia_ssid=11e953d7-b086-4fcf-a424-b43314c76cca',
                'Host': 'tj.lianjia.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'})
            pattern = re.compile(r'<div class="areaName">.*?</div>')
            areaDiv = pattern.search(linkRes)

            pattern = re.compile(r'<a.*?>(.*?)</a>')
            aData = pattern.findall(areaDiv.group())

            areaData = '' if aData is None or len(aData) <= 0 else aData[0]

            geoCodeVillage = getGeoCodes(u'天津市{0}'.format(village))[0]  # 小区坐标
            distanceAndTime = getDistanceAndTimeByLngLat(geoCodeHome, geoCodeVillage)  # 路径规划信息，获取距离和时间（自驾）

            babyDirection = getDirectionByLngLat(geoCodeHerOffice, geoCodeVillage)
            babyDirectionStr = '\"'
            for item in babyDirection:
                babyDirectionStr = babyDirectionStr + unicode('{0}\n').format(item)
            babyDirectionStr = babyDirectionStr + '\"'

            meDirection = getDirectionByLngLat(geoCodeMyOffice, geoCodeVillage)
            meDirectionStr = '\"'
            for item in meDirection:
                meDirectionStr = meDirectionStr + unicode('{0}\n').format(item)
            meDirectionStr = meDirectionStr + '\"'

            result.append(
                unicode("{0},{1},{10},{2},{3},{9},{4},{5},{6},{7},{8}\n").format(village, street, totalPrice,
                                                                                 unitPrice,
                                                                                 u'距离：{0}，时间：{1}'.format(
                                                                                     distanceAndTime[0],
                                                                                     distanceAndTime[1]), other, subway,
                                                                                 babyDirectionStr,
                                                                                 meDirectionStr, dateInfo,
                                                                                 areaData).encode(
                    'gbk'))
            saveFile("houselist1.csv",
                     unicode("{0},{1},{10},{2},{3},{9},{4},{5},{6},{7},{8}\n").format(village, street, totalPrice,
                                                                                      unitPrice,
                                                                                      u'距离：{0}，时间：{1}'.format(
                                                                                          distanceAndTime[0],
                                                                                          distanceAndTime[1]), other,
                                                                                      subway,
                                                                                      babyDirectionStr,
                                                                                      meDirectionStr, dateInfo,
                                                                                      areaData).encode(
                         'gbk'), 'a')
        except Exception, e:
            traceback.print_exc()
            time.sleep(random.randint(2, 5))
    return i


def getHouseList(append=False):
    geoCodes = getGeoCodes(u'天津市义兴里|天津市海光寺|天津市咸阳路')
    geoCodeHome = geoCodes[0]  # 义兴里小区坐标
    geoCodeHerOffice = geoCodes[1]  # 海光寺坐标
    geoCodeMyOffice = geoCodes[2]  # 咸阳路坐标

    tableData = []
    if not append:
        tableData.append(
            unicode("{0},{1},{10},{2},{3},{9},{4},{5},{6},{7},{8}\n").format("小区", "街道", "总价（万）", "单价（元/平米）",
                                                                             "距离",
                                                                             "其他信息", "地铁信息",
                                                                             "her",
                                                                             "me", "发布时间", "所属区域").encode(
                'gbk'))
        saveFile("houselist1.csv", tableData, 'a')
    page = 61
    listInfo = getHouseListByPage(page)
    totalPages = listInfo[0]

    i = 0
    while page <= totalPages:
        print page
        i = handleHouseList(listInfo[1], geoCodeHome, geoCodeHerOffice, geoCodeMyOffice, tableData, i)
        page = page + 1
        listInfo = getHouseListByPage(page)
        time.sleep(5)

        # saveFile("houselist.csv", tableData, 'a')


def main(argv):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    getHouseList(True)


if __name__ == '__main__':
    main(sys.argv)
