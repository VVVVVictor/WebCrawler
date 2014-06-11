#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = "Wang Miaofei"

import urllib, urllib2, cookielib
import sys, string, time, os, re, json
import csv
from bs4 import BeautifulSoup
import socket
from tools_kickstarter import *

#constant
SORT_TYPE = 'launch_date'

#for crawl
urlHost = u'https://www.kickstarter.com'
urlStart = u'http://www.my089.com/Loan/default.aspx'
#filedirectory = u'D:\datas\pythondatas\renrendai\\'
headers={'Accept':'application/json, text/javascript, */*; q=0.01', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36', 'Host':'www.kickstarter.com', 'X-Requested-With':'XMLHttpRequest'}

titles = ([u"link",u"dataDate",u"dataClock",u"Category",u"Title",u"Updates", u"Backers",u"Comments", u"PAdd",u"Video",u"DesLength",u'DesPics', u'DescriptionContent', u"RiskLength", u'RiskContent', u"FAQQ",u"FAQA",u"货币单位",u"Bkrs",u"PlgAmt",u"Goal",u"DaysToGo",u"BgnDate",u"EndDate",u"SpanDays",u"CreatorNM",u"CAdd",u"FB",u"CreatorID",u"BioLength",u"LastLoginDate",u"JoinedDate",u"NBacked",u"NCreated",u"Art",u"Comics",u"Dance",u"Design",u"Fashion",u"Film&Video",u"Food",u"Games",u"Music",u"Photograph",u"Publishing",u"Technology",u"Theater"], ['link', u"dataDate",u"dataClock",u"Category",u"Title",u"CreatorID",u"BackerNM",u"BackerID",u"BackerLocation", u"NBP"], ['link', u"dataDate",u"dataClock", u'Category', u'Title', u'CreatorID', 'updateTitle', 'updateDate', 'likeNumber','updateContent'], ['link', u"dataDate",u"dataClock", u'Category', u'Title', u'CreatorID', u'commentator', u'commentatorID', u'commentDate', u'commentContent'], ['link', u"dataDate",u"dataClock", 'Category', 'Title', 'CreatorID', 'Amount', 'backersNumber', 'Description', 'DeliveryDate'], ['link', u"dataDate",u"dataClock", 'Category', 'Title', 'CreatorID', 'Question', 'Answer'])

orderCount = 0
allCount = 0
categoryIdList = [1, 3, 6, 7, 9, 10, 11, 12, 14, 15, 16, 17, 18]
categoryNameList = ['','Art', '', 'Comics','','','Dance','Design','','Fashion','Food','Film&Video','Games','','Music','Photography','Technology','Theater', 'Publishing']
sheetName = ['projects', 'backers', 'updates', 'comments', 'rewards', 'FAQs']

def createWriters(filedirectory, prefix):
    writers = [] #csv writer list
    for i in range(1, 7):
        name_sheet = filedirectory+prefix+'_'+strtime+'_'+sheetName[i-1]+'.csv'
        flag_newfile = True
        if os.path.isfile(name_sheet):
            flag_newfile = False
        file_sheet = open(name_sheet, 'wb')
        file_sheet.write('\xEF\xBB\xBF') #防止windows下excel打开显示乱码
        
        writer = csv.writer(file_sheet)
        writers.append(writer)
        if flag_newfile:
            writer.writerow(titles[i-1])
    return writers

#----------------------------------------------
def getCategory(filedirectory, categoryNo, startPage, endPage):
    starttime = time.clock()
    #lastpage = begin_page #记录抓取的最后一个有效页面
    
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    
    categoryId = categoryIdList[categoryNo-1]
    categoryName = categoryNameList[categoryId]
    subFolder = filedirectory+categoryName+'/'
    createFolder(subFolder)
    writers = createWriters(subFolder, categoryName+'_'+str(startPage)+'-'+str(endPage))
    
    i = categoryId
    pageCount = startPage-1
    while True:
        pageCount += 1
        if pageCount > endPage:
            break
        print('************************************************************')
        print('* CATEGORY ID='+str(i)+';  '+'CATEGORY NAME='+categoryName+'; PAGE='+str(pageCount)+' ')
        print('************************************************************')
        req = urllib2.Request(urlCategory+'page='+str(pageCount)+'&category_id='+str(i)+'&sort='+SORT_TYPE, headers=headers)
        try:
            response = urllib2.urlopen(req)
            m = response.read()
            scriptData = json.loads(m)
            projList = scriptData['projects']
            if(len(projList) == 0):
                break
            for proj in projList:
                url = proj['urls']['web']['project']
                print url
                analyzeData(url, writers)
            response.close()
        except (urllib2.URLError) as e:
            if hasattr(e, 'code'):
                print('[ERROR]'+str(e.code)+' '+str(e.reason))
            print(str(e.reason))
            print('url = ')
        except socket.error as e:
            print('[ERROR] Socket error: '+str(e.errno))
            continue
        #endwhile
    #end for
    
    endtime = time.clock()
    print(u'[execute time]:'+str(endtime-starttime)+'s') #50:47.9s
    return
#----------------------------------------------
def getAllCategory(filedirectory):
    starttime = time.clock()
    #lastpage = begin_page #记录抓取的最后一个有效页面
    
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    
    writers = createWriters(filedirectory)
    
    for i in categoryIdList:
        pageCount = 0
        while True:
            pageCount += 1
            print('CATEGORY ID: '+str(i)+';  PAGE: '+str(pageCount))
            req = urllib2.Request(urlCategory+'page='+str(pageCount)+'&category_id='+str(i)+'&sort='+SORT_TYPE, headers=headers)
            try:
                response = urllib2.urlopen(req)
                m = response.read()
                scriptData = json.loads(m)
                projList = scriptData['projects']
                if(len(projList) == 0):
                    break
                for proj in projList:
                    url = proj['urls']['web']['project']
                    print url
                    analyzeData(url, writers)
                response.close()
            except (urllib2.URLError) as e:
                if hasattr(e, 'code'):
                    print('[ERROR]'+str(e.code)+' '+str(e.reason))
                print(str(e.reason))
                print('url = ')
            except socket.error as e:
                print('[ERROR] Socket error: '+str(e.errno))
                continue
        #endwhile
    #end for
    
    endtime = time.clock()
    print(u'[execute time]:'+str(endtime-starttime)+'s') #50:47.9s
    return
#end def getData()
#---------------------------
def getInput():
    global categoryNo, startPage, endPage
    while True:
        try:
            raw_categoryNo = raw_input(u'Input category number(1-13, default=1):\n')
            categoryNo = int(raw_categoryNo)
            if categoryNo < 1 or categoryNo > 13:
                print('Category number illegal! Please input again!')
                continue
            break
        except:
            if(raw_categoryNo == ''):
                categoryNo = 1
                break
            print('Not a number. Please input again!')
            continue
    while True:
        try:
            raw_startPage = raw_input('Input start page(default=1):\n')
            startPage = int(raw_startPage)
            if startPage < 1:
                print('Start page illegal! Please input again!')
                continue
            break
        except:
            if(raw_startPage == ''):
                startPage = 1
                break
            print('Not a number. Please input again!')
            continue
        
    while True:
        try:
            raw_endPage = raw_input('Input end page(default=100000):\n')
            endPage = int(raw_endPage)
            if endPage < 1:
                print('End page illegal! Please input again!')
                continue
            break
        except:
            if(raw_endPage == ''):
                endPage = 100000
                break
            print('Not a number. Please input again!')
            continue
#----------------------------
#main
reload(sys)
sys.setdefaultencoding('utf-8') #系统输出编码置为utf8
sys.setrecursionlimit(1000000)#设置递归调用深度

urlTest = 'https://www.kickstarter.com/projects/truelovehealth/strongest-hearts-documentary-series-on-vegan-athle'
filedirectory = getConfig()

categoryNo = 1
startPage = 1
endPage = 100000

if login():
    getInput()
    print '------------INPUT INFORMATION---------------------'
    print '- CategoryNumber='+str(categoryNo)
    print '- StartPage='+str(startPage)
    print '- EndPage='+str(endPage)
    print '------------INPUT INFORMATION---------------------'
    #print('Login success!')
    #test()
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    
    #writers = createWriters(filedirectory)
    #analyzeData(urlTest, writers)
    #getAllCategory(filedirectory)
    getCategory(filedirectory, categoryNo, startPage, endPage)

