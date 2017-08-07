# coding:utf-8

import os
import sys
import json
import random

from common.HttpHelper import httpGet
from common.LoggerHelper import writeLog, writeErrorLog, writeWarningLog
import traceback

KEY = 'dacfb9273dd8cba740317191ad4daf6c'
KEY1 = 'a7b765f063397ce07d7558f81de31362'
KEY2 = 'fa7bdb2bca7f33b44945349bb5365df0'


def getKey():
    randomNumber = random.randint(0, 2)
    return KEY if randomNumber == 0 else (KEY1 if randomNumber == 1 else KEY2)


# 计算时间和距离
def getDistanceAndTime(origin, destination):
    geoCode = getGeoCodes(origin + "|" + destination)
    return getDistanceAndTimeByLngLat(geoCode[0], geoCode[1])


def getDistanceAndTimeByLngLat(origin, destination):
    url = unicode('http://restapi.amap.com/v3/direction/driving?key={0}&origin={1}&destination={2}&strategy=9').format(
        getKey(), origin, destination)
    res = httpGet(url)

    jo = json.loads(res)
    if (int(jo['status']) == 0):
        writeWarningLog(unicode("【高德】驾车 路径规划失败, origin:{0},destination:{1},原因：{2}").format(origin, destination, jo))
        return (None, None)

    paths = jo['route']['paths']
    if (len(paths) <= 0):
        writeWarningLog(unicode("【高德】驾车 没有找到相关路径, origin:{0},destination:{1},原因：{2}").format(origin, destination, jo))
        return (None, None)

    distance = unicode("{0}公里").format(round(float(paths[0]['distance']) / 1000, 1))
    minutes = int(float(paths[0]['duration']) / 60)
    hour = int(minutes / 60)
    minute = int(minutes % 60)
    time = unicode("{0}分").format(minute) if hour <= 0 else unicode("{0}小时{1}分").format(hour, minute)

    return (distance, time)


def getGeoCodes(address):
    url = unicode("http://restapi.amap.com/v3/geocode/geo?key={0}&address={1}&batch=true").format(getKey(), address)
    res = httpGet(url)

    jo = json.loads(res)

    if (int(jo['status']) == 0):
        writeWarningLog(unicode("【高德】解析地址失败, address:{0}, 原因：{1}").format(address, jo))
        return (None, None)

    result = []
    for i in range(0, len(jo['geocodes'])):
        geoCodes = jo['geocodes'][i]
        result.append(geoCodes['location'])

    return result


def getDirectionByLngLat(origin, destination):
    url = unicode(
        'http://restapi.amap.com/v3/direction/transit/integrated?key={0}&origin={1}&destination={2}&strategy=0&city=天津市').format(
        getKey(), origin, destination)
    res = httpGet(url)

    try:
        jo = json.loads(res)
        if (int(jo['status']) == 0):
            writeWarningLog(unicode("【高德】公交 路径规划失败, origin:{0},destination:{1},原因：{2}").format(origin, destination, jo))
            return None

        transits = jo['route']['transits']
        if (len(transits) <= 0):
            writeWarningLog(
                unicode("【高德】公交规划 没有找到相关路径, origin:{0},destination:{1},原因：{2}").format(origin, destination, jo))
            return None

        transit = transits[0]  # 找第一条规划路线
        segments = transit['segments']  # 路径信息

        if (len(segments) <= 0):
            writeWarningLog(
                unicode("【高德】公交规划 没有找到路径信息, origin:{0},destination:{1},原因：{2}").format(origin, destination, jo))
            return None

        result = []
        for i in range(0, len(segments)):
            segment = segments[i]
            if i == 0:
                walkingDistance = round(float(segment['walking']['distance']) / 1000, 1)
                walkingTime = int(float(segment['walking']['duration']) / 60)
                result.append(unicode("步行{0}公里：约{1}分钟").format(walkingDistance, walkingTime))

                busName = segment['bus']['buslines'][0]['name']
                busDepartureStop = segment['bus']['buslines'][0]['departure_stop']['name']
                busArrivalStop = segment['bus']['buslines'][0]['arrival_stop']['name']
                totalStops = len(segment['bus']['buslines'][0]['via_stops']) + 1
                result.append(
                    unicode("（{0}） {1} => {2} 共{3}站").format(busName, busDepartureStop, busArrivalStop, totalStops))
            elif i == len(segments) - 1:
                if segment['walking'] is not None:
                    if len(segment['walking']) <= 0:
                        continue
                    walkingDistance = round(float(segment['walking']['distance']) / 1000, 1)
                    walkingTime = int(float(segment['walking']['duration']) / 60)
                    result.append(unicode("步行{0}公里：约{1}分钟").format(walkingDistance, walkingTime))
            else:
                busName = segment['bus']['buslines'][0]['name']
                busDepartureStop = segment['bus']['buslines'][0]['departure_stop']['name']
                busArrivalStop = segment['bus']['buslines'][0]['arrival_stop']['name']
                totalStops = len(segment['bus']['buslines'][0]['via_stops']) + 1
                result.append(
                    unicode("（{0}） {1} => {2} 共{3}站").format(busName, busDepartureStop, busArrivalStop, totalStops))
        return result
    except Exception, e:
        traceback.print_exc()
        print url
        print res
        return None
