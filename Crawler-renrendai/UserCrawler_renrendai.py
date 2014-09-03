#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = "Wang Miaofei"

import urllib, urllib2, cookielib, httplib
import sys, string, time, os, re
import csv
from bs4 import BeautifulSoup
import socket
from tools_renrendai import *

#constant
LOST_PAGE_LIMIT = int(20)

#for crawl
urlLoan = u'http://www.renrendai.com/lend/detailPage.action?loanId='
urlFP = u'http://www.renrendai.com/financeplan/listPlan!detailPlan.action?financePlanId='
fpFolder = 'FinancePlan/'
#filedirectory = u'D:\datas\pythondatas\renrendai\\'
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36', 'Host':'www.renrendai.com'}

sheetName = [u'用户信息', u'借款列表']
titles = ([u'抓取日期', u'抓取时间', u'用户ID', u'用户昵称', u'信用等级', u'信用分数', u'注册时间', u'持有债权数量', u'持有理财计划数量', u'发布借款数量', u'成功借款数量', u'未还清借款数量', u'逾期次数', u'逾期金额', u'严重逾期笔数'],[u'抓取日期', u'抓取时间', u'用户ID', u'用户昵称', u'借款标题', u'借款ID', u'年利率（%）', u'金额（元）', u'期限（月）', u'逾期情况', u'借款时间', u'状态'])

#----------------------------------------------
def createWriters(filedirectory, prefix=''):
    createFolder(filedirectory)
    writers = [] #csv writer list
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    for i in range(1, len(titles)+1):
        name_sheet = filedirectory+prefix+'_'+strtime+'_'+sheetName[i-1]+'.csv'
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
class DataFetcher(threading.Thread):
    def __init__(self, tId, writers):
        threading.Thread.__init__(self)
        self.tId = tId
        self.writers = writers
    def run(self):
        global pageNo, lostPageCount, exitFlag
        while not exitFlag:
            pageLock.acquire()
            pageNo += 1
            if(pageNo > endID):
                exitFlag = True
                break
            curPage = pageNo
            print('Thread '+str(self.tId)+': downloading User: '+str(pageNo)+'...')
            req = urllib2.Request(urlLoan+str(pageNo), headers = getRandomHeaders())
            pageLock.release()
            try:
                response = urllib2.urlopen(req)
                m = response.read()
                #response.close()
            except (urllib2.URLError) as e:
                if hasattr(e, 'code'):
                    print(str(e.code)+': '+str(e.reason))
                else:
                    print(e.reason)
                continue
            except socket.error as e:
                print('ERROR] Socket error: '+str(e.errno))
                continue
            #end try&except
            if analyzeData(m, writers):
                lostPageCount = 0
            else:
                print('Loan '+str(curPage)+' is LOST!')
                lostPageCount += 1
                if(lostPageCount > LOST_PAGE_LIMIT):
                    exitFlag = True
                    print('You have got the latest page!')
            time.sleep(2)
        #end while
#end class DataFetcher
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
#main
reload(sys)
sys.setdefaultencoding('utf-8') #系统输出编码置为utf8

#reset timeout
timeout = 100
socket.setdefaulttimeout(timeout)

httplib.HTTPConnection._http_vsn = 10
httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'

startID = 1
endID = 1000

print '***************************************'
print '* Renrendai User Spider v0903 *'
print '***************************************'

filedirectory = getConfig()[0]
if login():
    getInput()
    print '------------INPUT INFORMATION---------------------'
    print '- StartID = '+str(startID)
    print '- EndID   = '+str(endID)
    print '------------INPUT INFORMATION---------------------'
    getData(startID, endID, filedirectory)
