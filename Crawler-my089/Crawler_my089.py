#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = "Wang Miaofei"

import urllib, urllib2, cookielib
import sys, string, time, os, re
import csv
from bs4 import BeautifulSoup
import socket
from pybloomfilter import BloomFilter
from tools_my089 import *

#constant
LOST_PAGE_LIMIT = int(10)

#for crawl
urlHost = u'http://www.my089.com'
urlStart = u'http://www.my089.com/Loan/default.aspx'
#filedirectory = u'D:\datas\pythondatas\renrendai\\'
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36', 'Host':'www.my089.com'}

orderPattern = re.compile(u'http://www.my089.com/Loan/Detail.aspx\?sid=(\d|-)+')
usePattern = re.compile(urlHost+u'(/Loan/Detail.aspx\?sid=(\d|-)+)|(/Loan/Succeed.aspx)|(/ConsumerInfo1.aspx?uid=(\d|\w)+)')

bf = BloomFilter(10000000, 0.01, 'filter.bloom')

def getData(begin_page, end_page, filedirectory):
    
    starttime = time.clock()
    lostPageCount = 0 #记录连续404的页面个数
    lastpage = begin_page #记录抓取的最后一个有效页面
    
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    
    writers = [] #csv writer list
    for i in range(1, 2):
        name_sheet = filedirectory+str(begin_page)+'-'+str(end_page)+'.'+strtime+'_sheet'+str(i)+'.csv'
        file_sheet = open(name_sheet, 'wb')
        file_sheet.write('\xEF\xBB\xBF') #防止windows下excel打开显示乱码
        
        writer = csv.writer(file_sheet)
        writers.append(writer)
    #end for
    
    for i in range(begin_page, end_page+1):
        req = urllib2.Request(urlLoan+str(i), headers = headers)
        try:
            response = urllib2.urlopen(req)
            m = response.read()
            #print(m)
            lastpage = i
            response.close()
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
        
        print('Downloading '+str(i)+' web page...')
        if analyzeData(m, writers[0]):
            lostPageCount = 0
        else:
            print('404')
            lostPageCount += 1
            if(lostPageCount > LOST_PAGE_LIMIT):
                print('You have got the latest page!')
                break
    #end for
    
    endtime = time.clock()
    print(u'[execute time]:'+str(endtime-starttime)+'s')
    return
#end def getData()

def handlePage(urlCur):
    print 'current = ' + urlCur
    if urlCur in bf:
        print 'dumplicate'
        return
    
    urlCur = u'http://www.my089.com/Loan/Detail.aspx?sid=14021808260150690335190015542346'
    if usePattern.match(urlCur):
        findUrl(urlCur)
        if orderPattern.match(urlCur):
            req = urllib2.Request(urlCur, headers = headers)
            response = urllib2.urlopen(req)
            m = response.read()
            #analyzeData() #tools

    bf.add(urlCur)
    logf.write(urlCur)
#end def handlePage

def findUrl(url):
    req = urllib2.Request(url, headers = headers)
    response = urllib2.urlopen(req)
    m = response.read()
#def findUrl
#----------------------------
#main
reload(sys)
sys.setdefaultencoding('utf-8') #系统输出编码置为utf8

filedirectory = getConfig()
if login():
    print('Login success!')
    bf.clear_all()
    
    logf = open('log.log', 'wb')
    handlePage(urlStart)
    logf.close()
