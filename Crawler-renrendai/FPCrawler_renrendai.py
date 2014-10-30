#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = "Wang Miaofei"

import urllib, urllib2, cookielib, httplib
import sys, string, time, os, re, json
import csv
from bs4 import BeautifulSoup
import socket
from tools_renrendai import *

#constant
LOST_PAGE_LIMIT = int(20)

#for crawl
urlLoan = u'http://www.renrendai.com/lend/detailPage.action?loanId='
urlUList_json = u'https://www.renrendai.com/financeplan/listPlan!listPlanJson.action?category='
urlUP = u'http://www.renrendai.com/financeplan/listPlan!detailPlan.action?financePlanId='
fpFolder = 'FinancePlan/'
#filedirectory = u'D:\datas\pythondatas\renrendai\\'
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36', 'Host':'www.renrendai.com'}
jsonheaders={'Accept':'application/json, text/javascript, */*; q=0.01', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36', 'Host':'www.renrendai.com', 'X-Requested-With':'XMLHttpRequest'}

sheetName = [u'计划概况', u'计划详情', u'预定记录', u'加入记录', u'计划表现']
titles = ([u'抓取日期', u'抓取时间', u'计划名称', u'计划id', u'计划金额（元）', u'加入人次', u'预期年化收益', u'累计收益（元）', u'状态'], [u'抓取日期', u'抓取时间', u'计划名称',u'计划ID', u'计划金额', u'预期收益（%/年）', u'投标范围', u'保障方式', u'计划状态', u'预定开始时间', u'预定结束时间', u'支付截止时间', u'开放加入时间', u'进入锁定时间', u'退出时间', u'加入条件（元）', u'加入上限（元）',u'定金', u'加入费率', u'退出费率', u'提前退出费率', u'加入总人次', u'满额用时', u'自动投标次数', u'帮助借款用户', u'为用户赚取（元）'], [u'计划名称', u'计划id', u'理财人昵称', u'理财人id', u'加入金额', u'预定日期', u'预定时间', u'来源', u'状态'], [u'计划名称', u'计划id', u'理财人昵称', u'理财人ID', u'加入金额', u'加入日期', u'加入时间'], [u'优选理财计划期数', u'自动投标次数', u'平均年利率', u'优选理财计划总额', u'资金利用率', u'累积赚取（元）', u'借款者人数'])

#----------------------------------------------
def createWriters(filedirectory, prefix=''):
    createFolder(filedirectory)
    writers = [] #csv writer list
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    for i in range(1, len(sheetName)+1):
        name_sheet = filedirectory+prefix+'_'+sheetName[i-1]+'.csv'
        flag_newfile = True
        if os.path.isfile(name_sheet):
            flag_newfile = False
        file_sheet = open(name_sheet, 'wb')
        file_sheet.write('\xEF\xBB\xBF')

        writer = csv.writer(file_sheet)
        writers.append(writer)
        if flag_newfile:
            writer.writerow(titles[i-1])
    return writers
#------------------------------------------------
def getList():
    for X in ['A', 'B']:
        print(u'抓取U计划'+X+'...')
        pageIndex = 1
        while(True):
            m = readFromUrl(urlUList_json+X+'&pageIndex='+str(pageIndex), headers = jsonheaders)
            #print m
            scriptData = json.loads(m)
            totalPage = scriptData['data']['totalPage']
            
            ulist = scriptData['data']['plans']
            for item in ulist:
                buffer = []
                currentDate = getTime('%Y-%m-%d')
                currentClock = getTime('%H:%M:%S')
                stateCode = item['status']
                state = stateCode
                if stateCode == '6': state = u'收益中'
                elif stateCode == '2': state = u'预定满额'
                elif stateCode == '7': state = u'开放期'
                elif stateCode == '0': state = u'等待预定'
                elif stateCode == '5': state = u'计划满额'
                    
                buffer = [currentDate, currentClock, item['name'], item['id'], item['amount'], item['subPointCount'], item['expectedYearRate'], item['earnInterest'], state]
                writers[0].writerow(buffer)
                
                content = readFromUrl(urlUP+str(item['id']))
                analyzeUPData(content, item['id'], writers)
            
            if(totalPage > pageIndex): pageIndex += 1
            else: break;
#end def getList()
#------------------------------------------------
def getData(begin_phase, end_phase, filedirectory):
    starttime = time.clock()
    lostPageCount = 0 #记录连续404的页面个数
    #lastpage = begin_page #记录抓取的最后一个有效页面
    
    writers = createWriters(filedirectory+fpFolder, 'FP_'+str(begin_phase)+'-'+str(end_phase))

    for i in range(begin_phase, end_phase+1):
        print('Getting No.'+str(i)+' Financial Plan...')
        req = urllib2.Request(urlFP+str(i), headers = getRandomHeaders())
        try:
            response = urllib2.urlopen(req)
            m = response.read()
            #print(m)
            #lastpage = i
            #response.close()
        except (urllib2.URLError) as e:
            if hasattr(e, 'code'):
                print(str(e.code)+': '+str(e.reason))
            else:
                print(e.reason)
            #i = lastpage
            continue
        except socket.error as e:
            print('ERROR] Socket error: '+str(e.errno))
            #i = lastpage 
            continue
        #end try&except
        
        if analyzeFPData(m, i, writers):
            lostPageCount = 0
        else:
            print('[ERROR] Financial plan No.'+str(i)+' has not established!')
            break
    #end for
    
    endtime = time.clock()
    print(u'[execute time]:'+str(endtime-starttime)+'s')
    return
#end def getData()
        
#----------------------------------------
def getInput():
    global startID, endID
    while True:
        try:
            raw_startID = raw_input('Input start Financial Plan ID:')
            startID = int(raw_startID)
            if startID < 1:
                print('Start ID illegal! Please input again!')
                continue
            break
        except:
            if(raw_startID == ''):
                startID = 1
                break
            print('Not a number! Please input again!')
            continue
    while True:
        try:
            raw_endID = raw_input('Input last  Financial Plan ID:')
            endID = int(raw_endID)
            if endID < 1:
                print('Last ID illegal! Please input again!')
                continue
            break
        except:
            if(raw_endID == ''):
                endID = 1000
                break
            print('Not a number! Please input again!')
            continue    
#----------------------------
#global variable
startID = 1
endID = 1000
writers = []
#----------------------------
#main
if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8') #系统输出编码置为utf8
    timeout = 100
    socket.setdefaulttimeout(timeout)
    httplib.HTTPConnection._http_vsn = 10
    httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'

    print '***************************************'
    print '*Renrendai U Finance Plan Spider v1027*'
    print '***************************************'

    filedirectory = getConfig()[0]
    if login():
        writers = createWriters(filedirectory, 'U')
        getList()
        #getInput()
        '''
        print '------------INPUT INFORMATION---------------------'
        print '- StartID = '+str(startID)
        print '- EndID   = '+str(endID)
        print '------------INPUT INFORMATION---------------------'
        '''
        #getData(startID, endID, filedirectory)
