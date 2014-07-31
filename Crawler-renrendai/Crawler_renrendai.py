#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = "Wang Miaofei"

import urllib, urllib2, cookielib, httplib, threading
import sys, string, time, os, re, argparse
import csv
from bs4 import BeautifulSoup
import socket
from tools_renrendai import *

#constant
LOST_PAGE_LIMIT = int(20)

#for crawl
urlLoan = u'http://www.renrendai.com/lend/detailPage.action?loanId='
#filedirectory = u'D:\datas\pythondatas\renrendai\\'
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36', 'Host':'www.renrendai.com'}

sheetName = [u'1标的详情', u'2投标记录', u'3还款表现', u'4债权信息', u'5转让记录', u'6发标人信息', u'7留言板', u'8催收跟进']
titles = ([u'抓取日期', u'抓取时间', u'序号', u'类型', u'认证或担保机构', u'标题', u'总额（元）', u'利率(%)', u'还款期限（月）', u'状态', u'保障方式', u'提前还款率(%)', u'还款方式', u'月还本息', u'投标进度(%)', u'满标用时', u'用户ID', u'用户名', u'性别', u'年龄', u'学历', u'学校', u'婚姻', u'公司行业', u'公司规模', u'岗位职责', u'工作城市', u'工作时间', u'收入范围', u'房产', u'房贷', u'车产', u'车贷', u'工作类型', u'信用等级', u'申请借款（笔）', u'成功还款（笔）', u'还清笔数（笔）', u'信用额度', u'借款总额', u'待还本息（元）', u'逾期金额（元）', u'逾期次数（次）', u'严重逾期', u'信用报告', u'信用报告通过日期', u'身份认证', u'身份认证通过日期', u'工作认证', u'工作认证通过日期', u'收入认证', u'收入认证通过日期', u'房产认证', u'房产认证通过日期', u'购车认证', u'购车认证通过日期', u'结婚认证', u'结婚认证通过日期', u'学历认证', u'学历认证通过日期', u'技术职称认证', u'技术职称认证通过日期', u'手机认证', u'手机认证通过日期', u'微博认证', u'微博认证通过日期', u'居住地证明', u'居住地证明通过日期', u'视频认证', u'视频认证通过日期', u'借款描述'], [u'抓取日期', u'抓取时间', u'序号', u'投标人ID', u'投标人昵称', u'投标金额', u'投标日期', u'投标时间', u'是否理财计划自动投标', u'理财计划期数'], [u'抓取日期', u'抓取时间', u'序号', u'合约还款日期', u'状态', u'应还本息', u'应付罚息', u'实际还款日期'], [u'抓取日期', u'抓取时间', u'序号', u'债权人ID', u'债权人昵称', u'待收本金（元）', u'持有份数（份）', u'是否理财计划自动投标', u'理财计划期数'], [u'抓取日期', u'抓取时间', u'序号', u'债权买入者ID', u'债权买入者昵称', u'债权卖出者ID', u'债权卖出者昵称', u'交易金额', u'交易日期', u'交易时间'], [u'抓取日期', u'抓取时间', u'发标人ID', u'发标人昵称', u'注册时间', u'持有债权数量（笔）', u'持有理财计划数量（笔）', u'发布借款数量', u'成功借款数量（笔）', u'未还清借款数量', u'逾期次数', u'逾期金额', u'严重逾期笔数'], [u'抓取日期', u'抓取时间', u'序号', u'留言者ID', u'留言者昵称', u'留言日期', u'留言时间', u'留言内容'], [u'抓取日期', u'抓取时间', u'序号', u'催收时间', u'联系人', u'描述'])

#----------------------------------------------
def createWriters(filedirectory, prefix=''):
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
            print('Thread '+str(self.tId)+': downloading Loan: '+str(pageNo)+'...')
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
def getData(begin_page, end_page, filedirectory):
    starttime = time.clock()
    lostPageCount = 0 #记录连续404的页面个数
    lastpage = begin_page #记录抓取的最后一个有效页面
    
    writers = createWriters(filedirectory, 'rrdai_'+str(begin_page)+'-'+str(end_page))

    for i in range(begin_page, end_page+1):
        print('Downloading Loan ID:'+str(i)+'...')
        req = urllib2.Request(urlLoan+str(i), headers = getRandomHeaders())
        try:
            response = urllib2.urlopen(req)
            m = response.read()
            #print(m)
            lastpage = i
            #response.close()
            if(len(m) < 100):
                print('webcontent too short!')
                login()
                continue
        except (urllib2.URLError) as e:
            if hasattr(e, 'code'):
                print(str(e.code)+': '+str(e.reason))
            else:
                print(e.reason)
            i = lastpage
            continue
        except socket.error as e:
            print('ERROR] Socket error: '+str(e.errno))
            i = lastpage 
            continue
        #end try&except
        
        if analyzeData(m, writers):
            lostPageCount = 0
        else:
            print('Page 404!')
            lostPageCount += 1
            if(lostPageCount > LOST_PAGE_LIMIT):
                print('You have got the latest page!')
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
            raw_startID = raw_input('Input start order ID:')
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
            raw_endID = raw_input('Input end order ID:')
            endID = int(raw_endID)
            if endID < 1:
                print('End ID illegal! Please input again!')
                continue
            break
        except:
            if(raw_endID == ''):
                endID = startID+3000
                break
            print('Not a number! Please input again!')
            continue
#----------------------------
#global variable
startID = 1
endID = 1000
pageNo = 0
threadCount = 3 #并发线程数
exitFlag = False
lostPageCount = 0
sleepTime = 2
#----------------------------
#main
if __name__=='__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8') #系统输出编码置为utf8
    #reset timeout
    timeout = 100
    socket.setdefaulttimeout(timeout)

    httplib.HTTPConnection._http_vsn = 10
    httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'

    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.add_argument('-s', '--start', action='store', dest='startid', help='Set start order ID')
    parser.add_argument('-e', '--end', action='store', dest='endid', help='Set last order ID')
    parser.add_argument('-t', '--threadcount', action='store', dest='threadCount', help='Set thread number', default=3)
    args = parser.parse_args()
    
    if(args.startid != None and args.endid != None):
        startID = int(args.startid)
        endID = int(args.endid)
    else:
        getInput()
    threadCount = int(args.threadCount)
    
    filedirectory = getConfig()
    if login():
        print '------------INPUT INFORMATION---------------------'
        print '- StartID = '+str(startID)
        print '- EndID   = '+str(endID)
        print '------------INPUT INFORMATION---------------------'
        
        startTime = time.clock()
        pageNo = startID
        pageLock = threading.Lock()
        #getData(startID, endID, filedirectory)
        threads = []
        writers = createWriters(filedirectory, 'rrdai_'+str(startID)+'-'+str(endID))
        for i in xrange(threadCount):
            thread = DataFetcher(i+1, writers)
            threads.append(thread)
        for t in threads:
            t.start()
            
        while(pageNo <= endID):
            pass
        exitFlag = True
        
        for t in threads:
            t.join()
        print 'Exiting Main Thread'
        endTime = time.clock()
        print('[Total order number]:'+str(pageNo-startID))
        print(u'[Total execute time]:'+str(endTime-startTime)+'s')