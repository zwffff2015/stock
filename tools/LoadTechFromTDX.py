# coding=utf-8

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))
import time
from datetime import datetime, timedelta
from common.LoggerHelper import writeErrorLog, writeInfoLog
from db.MysqlUtil import initMysql, select, execute, batchInsert, disconnect
from common.NumberHelper import getDicValue

'''
    将通达信导出的数据，导入到数据库
'''


def loadData(startDate, endDate):
    date = startDate
    while (date <= endDate):
        dateStr = date.strftime('%Y%m%d')
        macd_kdj_dmi_expma = getMACD_KDJ_DMI_EXPMA(dateStr)
        emv_trix_wvad = getEMV_TRIX_WVAD(dateStr)
        vr_cr_arbr = getVR_CR_ARBR(dateStr)
        psy_rsi_mtm = getPSY_RSI_MTM(dateStr)
        wr_cci_obv = getWR_CCI_OBV(dateStr)
        dma_boll_bias = getDMA_BOLL_BIAS(dateStr)
        if macd_kdj_dmi_expma is None or emv_trix_wvad is None or vr_cr_arbr is None or psy_rsi_mtm is None or wr_cci_obv is None or dma_boll_bias is None:
            date = date + timedelta(days=1)
            continue

        lenarr = [len(macd_kdj_dmi_expma), len(emv_trix_wvad), len(vr_cr_arbr), len(psy_rsi_mtm), len(wr_cci_obv),
                  len(dma_boll_bias)]
        dicArr = [macd_kdj_dmi_expma, emv_trix_wvad, vr_cr_arbr, psy_rsi_mtm, wr_cci_obv, dma_boll_bias]

        max = 0
        maxIndex = 0
        for i in range(0, len(lenarr)):
            if (lenarr[i] > max):
                max = lenarr[i]
                maxIndex = i

        print dateStr
        for key in dicArr[maxIndex]:
            # print date, key
            saveStockTechToDb(key, date.strftime('%Y-%m-%d'), macd_kdj_dmi_expma.get(key), emv_trix_wvad.get(key),
                              vr_cr_arbr.get(key),
                              psy_rsi_mtm.get(key), wr_cci_obv.get(key), dma_boll_bias.get(key))
        date = date + timedelta(days=1)


def saveStockTechToDb(code, date, macd_kdj_dmi_expmaDic, emv_trix_wvadDic, vr_cr_arbrDic, psy_rsi_mtmDic, wr_cci_obvDic,
                      dma_boll_biasDic):
    checkExistSql = unicode("select count(*) from s_stock_tech where code='{0}' and date='{1}'").format(code,
                                                                                                        date)
    count = select(checkExistSql, False)[0]

    if count > 0:
        updateSql = unicode(
            "update s_stock_tech set MACD={2},DIF={3},DEA={4},ADX={5},ADXR={6},INCDI={7},DECDI={8},DMA={9},AMA={10},EXPMA1={11},EXPMA2={12},EMV={13},TRIX={14}, TMA={15},WVAD={16},VR={17},CR={18},AR={19},BR={20},PSY={21},K={22},D={23},J={24},RSI1={25},RSI2={26},MTM={27},MA={28},WR1={29},CCI={30},OBV={31},RSI3={32},WR2={33},MID={34},UPP={35},LOW={36},BIAS1={37},BIAS2={38},BIAS3={39} where code='{0}' and date='{1}'").format(
            code, date, getDicValue(macd_kdj_dmi_expmaDic, 'MACD'), getDicValue(macd_kdj_dmi_expmaDic, 'DIF'),
            getDicValue(macd_kdj_dmi_expmaDic, 'DEA'),
            getDicValue(macd_kdj_dmi_expmaDic, 'ADX'),
            getDicValue(macd_kdj_dmi_expmaDic, 'ADXR'), getDicValue(macd_kdj_dmi_expmaDic, 'PDI'),
            getDicValue(macd_kdj_dmi_expmaDic, 'MDI'),
            getDicValue(dma_boll_biasDic, 'DMA'), getDicValue(dma_boll_biasDic, 'AMA'),
            getDicValue(macd_kdj_dmi_expmaDic, 'EXP1'), getDicValue(macd_kdj_dmi_expmaDic, 'EXP2'),
            getDicValue(emv_trix_wvadDic, 'EMV'),
            getDicValue(emv_trix_wvadDic, 'TRIX'),
            getDicValue(emv_trix_wvadDic, 'TMA'),
            getDicValue(emv_trix_wvadDic, 'WVAD'), getDicValue(vr_cr_arbrDic, 'VR'), getDicValue(vr_cr_arbrDic, 'CR')
            , getDicValue(vr_cr_arbrDic, 'AR'), getDicValue(vr_cr_arbrDic, 'BR'), getDicValue(psy_rsi_mtmDic, 'PSY'),
            getDicValue(macd_kdj_dmi_expmaDic, 'K'),
            getDicValue(macd_kdj_dmi_expmaDic, 'D'), getDicValue(macd_kdj_dmi_expmaDic, 'J'),
            getDicValue(psy_rsi_mtmDic, 'RSI1'), getDicValue(psy_rsi_mtmDic, 'RSI2'),
            getDicValue(psy_rsi_mtmDic, 'MTM'), getDicValue(psy_rsi_mtmDic, 'MTMMA'),
            getDicValue(wr_cci_obvDic, 'WR1'),
            getDicValue(wr_cci_obvDic, 'CCI'), getDicValue(wr_cci_obvDic, 'OBV'), getDicValue(psy_rsi_mtmDic, 'RSI3'),
            getDicValue(wr_cci_obvDic, 'WR2'),
            getDicValue(dma_boll_biasDic, 'MID'), getDicValue(dma_boll_biasDic, 'UPP'),
            getDicValue(dma_boll_biasDic, 'LOW'), getDicValue(dma_boll_biasDic, 'BIAS1'),
            getDicValue(dma_boll_biasDic, 'BIAS2'), getDicValue(dma_boll_biasDic, 'BIAS3'))
        # execute(updateSql)
    else:
        insertSql = unicode(
            "insert into s_stock_tech(code,date,timestamp,MACD,DIF,DEA,ADX,ADXR,INCDI,DECDI,DMA,AMA,EXPMA1,EXPMA2,EMV,TRIX,TMA,WVAD,VR,CR,AR,BR,PSY,K,D,J,RSI1,RSI2,MTM,MA,WR1,CCI,OBV,RSI3,WR2,MID,UPP,LOW,BIAS1,BIAS2,BIAS3) VALUES (\'{0}\',\'{1}\',{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18},{19},{20},{21},{22},{23},{24},{25},{26},{27},{28},{29},{30},{31},{32},{33},{34},{35},{36},{37},{38},{39},{40})").format(
            code,
            date, int(
                time.mktime(time.strptime(date, '%Y-%m-%d'))), getDicValue(macd_kdj_dmi_expmaDic, 'MACD'),
            getDicValue(macd_kdj_dmi_expmaDic, 'DIF'),
            getDicValue(macd_kdj_dmi_expmaDic, 'DEA'),
            getDicValue(macd_kdj_dmi_expmaDic, 'ADX'),
            getDicValue(macd_kdj_dmi_expmaDic, 'ADXR'), getDicValue(macd_kdj_dmi_expmaDic, 'PDI'),
            getDicValue(macd_kdj_dmi_expmaDic, 'MDI'),
            getDicValue(dma_boll_biasDic, 'DMA'), getDicValue(dma_boll_biasDic, 'AMA'),
            getDicValue(macd_kdj_dmi_expmaDic, 'EXP1'), getDicValue(macd_kdj_dmi_expmaDic, 'EXP2'),
            getDicValue(emv_trix_wvadDic, 'EMV'),
            getDicValue(emv_trix_wvadDic, 'TRIX'),
            getDicValue(emv_trix_wvadDic, 'TMA'),
            getDicValue(emv_trix_wvadDic, 'WVAD'), getDicValue(vr_cr_arbrDic, 'VR'), getDicValue(vr_cr_arbrDic, 'CR')
            , getDicValue(vr_cr_arbrDic, 'AR'), getDicValue(vr_cr_arbrDic, 'BR'), getDicValue(psy_rsi_mtmDic, 'PSY'),
            getDicValue(macd_kdj_dmi_expmaDic, 'K'),
            getDicValue(macd_kdj_dmi_expmaDic, 'D'), getDicValue(macd_kdj_dmi_expmaDic, 'J'),
            getDicValue(psy_rsi_mtmDic, 'RSI1'), getDicValue(psy_rsi_mtmDic, 'RSI2'),
            getDicValue(psy_rsi_mtmDic, 'MTM'), getDicValue(psy_rsi_mtmDic, 'MTMMA'),
            getDicValue(wr_cci_obvDic, 'WR1'),
            getDicValue(wr_cci_obvDic, 'CCI'), getDicValue(wr_cci_obvDic, 'OBV'), getDicValue(psy_rsi_mtmDic, 'RSI3'),
            getDicValue(wr_cci_obvDic, 'WR2'),
            getDicValue(dma_boll_biasDic, 'MID'), getDicValue(dma_boll_biasDic, 'UPP'),
            getDicValue(dma_boll_biasDic, 'LOW'), getDicValue(dma_boll_biasDic, 'BIAS1'),
            getDicValue(dma_boll_biasDic, 'BIAS2'), getDicValue(dma_boll_biasDic, 'BIAS3'))
        execute(insertSql)


def getMACD_KDJ_DMI_EXPMA(date):
    fileName = unicode("沪深Ａ股{0}").format(date)
    fileName = os.path.abspath(os.path.join(os.getcwd(), "../config/import/" + fileName + ".txt"))
    if not os.path.exists(fileName):
        return None

    i = -1
    dict = {}
    for line in open(fileName):
        i = i + 1
        if i < 2:
            continue

        line = line.strip()
        if (line == ''):
            continue

        lineInfo = line.split('\t')
        if (len(lineInfo) <= 2):
            continue

        data = {}
        data['code'] = lineInfo[0]

        try:
            data['DIF'] = lineInfo[6]
            data['DEA'] = lineInfo[7]
            data['MACD'] = lineInfo[8]
            data['K'] = lineInfo[9]
            data['D'] = lineInfo[10]
            data['J'] = lineInfo[11]
            data['PDI'] = lineInfo[12]
            data['MDI'] = lineInfo[13]
            data['ADX'] = lineInfo[14]
            data['ADXR'] = lineInfo[15]
            data['EXP1'] = lineInfo[16]
            data['EXP2'] = lineInfo[17]
            dict[lineInfo[0]] = data
        except Exception, e:
            writeErrorLog(unicode("[getMACD_KDJ_DMI_EXPMAfailed]code:{0}, e:{1}").format(lineInfo, str(e)))

    return dict


def getEMV_TRIX_WVAD(date):
    fileName = unicode("沪深Ａ股{0}").format(date)
    fileName = os.path.abspath(os.path.join(os.getcwd(), "../config/import/" + fileName + "_1.txt"))
    if not os.path.exists(fileName):
        return None

    i = -1
    dict = {}
    for line in open(fileName):
        i = i + 1
        if i < 2:
            continue

        line = line.strip()
        if (line == ''):
            continue

        lineInfo = line.split('\t')
        if (len(lineInfo) <= 2):
            continue

        data = {}
        data['code'] = lineInfo[0]
        try:
            data['EMV'] = lineInfo[9]
            data['TRIX'] = lineInfo[11]
            data['TMA'] = -1 if len(lineInfo) < 13 else lineInfo[12]
            data['WVAD'] = -1 if len(lineInfo) < 14 else lineInfo[13]
            dict[lineInfo[0]] = data
        except Exception, e:
            writeErrorLog(unicode("[getEMV_TRIX_WVADfailed]code:{0}, e:{1}").format(lineInfo, str(e)))

    return dict


def getVR_CR_ARBR(date):
    fileName = unicode("沪深Ａ股{0}").format(date)
    fileName = os.path.abspath(os.path.join(os.getcwd(), "../config/import/" + fileName + "_2.txt"))
    if not os.path.exists(fileName):
        return None

    i = -1
    dict = {}
    for line in open(fileName):
        i = i + 1
        if i < 2:
            continue

        line = line.strip()
        if (line == ''):
            continue

        lineInfo = line.split('\t')
        if (len(lineInfo) <= 2):
            continue

        data = {}
        data['code'] = lineInfo[0]
        try:
            data['VR'] = lineInfo[9]
            data['CR'] = -1 if len(lineInfo) < 12 else lineInfo[11]
            data['BR'] = -1 if len(lineInfo) < 17 else lineInfo[16]
            data['AR'] = -1 if len(lineInfo) < 18 else lineInfo[17]
            dict[lineInfo[0]] = data
        except Exception, e:
            writeErrorLog(unicode("[getVR_CR_ARBRfailed]code:{0}, e:{1}").format(lineInfo, str(e)))

    return dict


def getPSY_RSI_MTM(date):
    fileName = unicode("沪深Ａ股{0}").format(date)
    fileName = os.path.abspath(os.path.join(os.getcwd(), "../config/import/" + fileName + "_3.txt"))
    if not os.path.exists(fileName):
        return None

    i = -1
    dict = {}
    for line in open(fileName):
        i = i + 1
        if i < 2:
            continue

        line = line.strip()
        if (line == ''):
            continue

        lineInfo = line.split('\t')
        if (len(lineInfo) <= 2):
            continue

        data = {}
        data['code'] = lineInfo[0]
        try:
            data['PSY'] = lineInfo[9]
            data['RSI1'] = -1 if len(lineInfo) < 12 else lineInfo[11]
            data['RSI2'] = -1 if len(lineInfo) < 13 else lineInfo[12]
            data['RSI3'] = -1 if len(lineInfo) < 14 else  lineInfo[13]
            data['MTM'] = -1 if len(lineInfo) < 15 else lineInfo[14]
            data['MTMMA'] = -1 if len(lineInfo) < 16 else  lineInfo[15]
            dict[lineInfo[0]] = data
        except Exception, e:
            writeErrorLog(unicode("[getPSY_RSI_MTMfailed]code:{0}, e:{1}").format(lineInfo, str(e)))

    return dict


def getWR_CCI_OBV(date):
    fileName = unicode("沪深Ａ股{0}").format(date)
    fileName = os.path.abspath(os.path.join(os.getcwd(), "../config/import/" + fileName + "_4.txt"))
    if not os.path.exists(fileName):
        return None

    i = -1
    dict = {}
    for line in open(fileName):
        i = i + 1
        if i < 2:
            continue

        line = line.strip()
        if (line == ''):
            continue

        lineInfo = line.split('\t')
        if (len(lineInfo) <= 2):
            continue

        data = {}
        data['code'] = lineInfo[0]
        try:
            data['WR1'] = lineInfo[9]
            data['WR2'] = -1 if len(lineInfo) < 11 else lineInfo[10]
            data['CCI'] = -1 if len(lineInfo) < 12 else lineInfo[11]
            data['OBV'] = -1 if len(lineInfo) < 13 else  lineInfo[12]
            dict[lineInfo[0]] = data
        except Exception, e:
            writeErrorLog(unicode("[getWR_CCI_OBVfailed]code:{0}, e:{1}").format(lineInfo, str(e)))

    return dict


def getDMA_BOLL_BIAS(date):
    fileName = unicode("沪深Ａ股{0}").format(date)
    fileName = os.path.abspath(os.path.join(os.getcwd(), "../config/import/" + fileName + "_5.txt"))
    if not os.path.exists(fileName):
        return None

    i = -1
    dict = {}
    for line in open(fileName):
        i = i + 1
        if i < 2:
            continue

        line = line.strip()
        if (line == ''):
            continue

        lineInfo = line.split('\t')
        if (len(lineInfo) <= 2):
            continue

        data = {}
        data['code'] = lineInfo[0]
        try:
            data['DMA'] = -1 if len(lineInfo) < 10 else lineInfo[9]
            data['AMA'] = -1 if len(lineInfo) < 11 else lineInfo[10]
            data['MID'] = -1 if len(lineInfo) < 12 else  lineInfo[11]
            data['UPP'] = -1 if len(lineInfo) < 13 else lineInfo[12]
            data['LOW'] = -1 if len(lineInfo) < 14 else lineInfo[13]
            data['BIAS1'] = -1 if len(lineInfo) < 15 else  lineInfo[14]
            data['BIAS2'] = -1 if len(lineInfo) < 16 else lineInfo[15]
            data['BIAS3'] = -1 if len(lineInfo) < 17 else lineInfo[16]
            dict[lineInfo[0]] = data
        except Exception, e:
            writeErrorLog(unicode("[getDMA_BOLL_BIASfailed]code:{0}, e:{1}").format(lineInfo, str(e)))

    return dict


def main(argv):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    initMysql()
    loadData(datetime.strptime("20170718", "%Y%m%d"), datetime.strptime("20170725", "%Y%m%d"))
    disconnect()


if __name__ == '__main__':
    main(sys.argv)
