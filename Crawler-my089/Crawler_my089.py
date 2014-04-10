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


aList = []#url队列

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

#--------------------------------------------------
def handlePage(urlCur):
    print 'current = ' + urlCur
    logf.write(urlCur+'\n')
    
    #广度优先
    for url in findAllUrl(urlCur):
        completeUrl = urlHost+url
        if completeUrl in bf: #去重
            #print 'dumplicate'
            continue
        bf.add(completeUrl)
        aList.append(completeUrl)
        print('ADD: '+completeUrl)
        
    if len(aList) > 0:
        urlCur = aList.pop(0)
        handlePage(urlCur)
        
    #end for

    #logf.write(urlCur+'\n')
#end def handlePage

#----------------------------
def test():
    urlTemp = 'http://www.my089.com/ConsumerInfo1.aspx?uid=0A7A965B5806C861'
    #urlTemp = 'http://www.my089.com/Loan/default.aspx'
    list_temp = findAllUrl(urlTemp)
    print(len(list_temp))
    for item in list_temp:
        print item
    
'''
    urlTest = 'http://www.my089.com/ConsumerInfo1.aspx?uid=CDFDDA8BAB5E164F'
    webcontent = readFromUrl(urlTest)
    soup = BeautifulSoup(webcontent)
    viewState = soup.find('input', {'id':'__VIEWSTATE'})['value']
    eventValidation = soup.find('input', {'id':'__EVENTVALIDATION'})['value']
        
    
    formdata = {'__EVENTTARGET':'ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder1$Pagination1$lbtnNext', '__EVENTARGUMENT':'', '__VIEWSTATE':viewState, '__EVENTVALIDATION':eventValidation}
    postdata = urllib.urlencode(formdata)
    
   
    req = urllib2.Request(urlTest, postdata, headers=headers)
    result = urllib2.urlopen(req)

    print result.geturl() #http://www.my089.com/Error/default.aspx?aspxerrorpath=/ConsumerInfo1.aspx
    '''
    #m = result.read()
    #print m
#end def test()

#----------------------------
#main
reload(sys)
sys.setdefaultencoding('utf-8') #系统输出编码置为utf8
sys.setrecursionlimit(1000000)#设置递归调用深度

urlTest = 'http://www.my089.com/ConsumerInfo1.aspx?uid=0C7C8143B7536149'
urlStart = urlTest

filedirectory = getConfig()
if login():
    print('Login success!')
    #test()
    

    bf.clear_all()
    
    logf = open('log.log', 'wb')
    aList.append(urlDefault)
    aList.append(urlSucceed)
    handlePage(aList.pop(0))
    logf.close()
 
