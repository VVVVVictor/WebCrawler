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

sheetName = [u'计划详情', u'加入记录', u'计划表现']
titles = ([u'优选理财计划期数', u'计划金额', u'预期收益（%/年）', u'投标范围', u'保障方式', u'计划状态', u'满额用时', u'锁定期限（月）', u'锁定结束', u'加入费率', u'服务费率', u'退出费率', u'剩余金额', u'每人可加入金额上限', u'加入总人次',u'自动投标次数', u'平均年利率', u'优选理财计划总额', u'资金利用率', u'累积赚取（元）', u'借款者人数'],[u'优选理财计划期数', u'投资人昵称', u'投资人ID', u'加入金额', u'加入日期', u'加入时间'], [u'优选理财计划期数', u'自动投标次数', u'平均年利率', u'优选理财计划总额', u'资金利用率', u'累积赚取（元）', u'借款者人数'])

#----------------------------------------------
def createWriters(filedirectory, prefix=''):
    createFolder(filedirectory)
    writers = [] #csv writer list
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    for i in range(1, 3):
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

filedirectory = getConfig()
if login():
    getInput()
    print '------------INPUT INFORMATION---------------------'
    print '- StartID = '+str(startID)
    print '- EndID   = '+str(endID)
    print '------------INPUT INFORMATION---------------------'
    getData(startID, endID, filedirectory)
