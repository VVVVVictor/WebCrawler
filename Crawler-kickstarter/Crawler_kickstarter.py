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
categoryName = ['','Art', '', 'Comics','','','Dance','Design','','Fashion','Food','Film&Video','Games','','Music','Photography','Technology','Theater', 'Publishing']
sheetName = ['projects', 'backers', 'updates', 'comments', 'rewards', 'FAQs']

def createWriters(filedirectory):
    writers = [] #csv writer list
    for i in range(1, 7):
        name_sheet = filedirectory+strtime+'_'+sheetName[i-1]+'.csv'
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

def getData(filedirectory):
    starttime = time.clock()
    lostPageCount = 0 #记录连续404的页面个数
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

#----------------------------
#main
reload(sys)
sys.setdefaultencoding('utf-8') #系统输出编码置为utf8
sys.setrecursionlimit(1000000)#设置递归调用深度

urlTest = 'https://www.kickstarter.com/projects/truelovehealth/strongest-hearts-documentary-series-on-vegan-athle'
filedirectory = getConfig()
strTest = 'At Dear Kate, we’ve engineered a new type of yoga pant that means you’ll never again find your undies in a bunch at the end of a workout. Incorporating a small inset of our patent-pending Underlux fabric, these pants have your back if you decide to “go commando.” Imagine the freedom of no more VPL (visible panty lines), no bunching or riding up, and no stress over winging it without underwear. We’re done with flimsy leggings: Dear Kate Yoga Pants and Shorts are designed to give you comfort, a killer looking backside, and most importantly, freedom of movement.  Our Story: Dear Kate redefined underwear with our patent-pending Underlux blend of fabric that is wicking, stain-releasing, and leak-resistant. We knew if we were going to expand beyond underwear, our new line had to be equally revolutionary. Our customers had an answer for us: they wanted a reinvented Yoga Pant. '
if login():
    #print('Login success!')
    #test()
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    
    #writers = createWriters(filedirectory)
    #analyzeData(urlTest, writers)
    getData(filedirectory)
'''
    req = urllib2.Request(urlCategory+'page='+str(95)+'&category_id='+str(6)+'&sort='+SORT_TYPE, headers=headers)
    try:
        response = urllib2.urlopen(req);
        m = response.read();
        scriptData = json.loads(m)
        projList = scriptData['projects']
        for proj in projList:
            url = proj['urls']['web']['project']
            print url
        response.close();
    except (urllib2.URLError) as e:
        if hasattr(e, 'code'):
            print('[ERROR]'+str(e.code)+' '+str(e.reason))
        print(str(e.reason))
        print('url = ')
    except socket.error as e:
        print('[ERROR] Socket error: '+str(e.errno))

            #i = lastpage


    createFolder('log')
    bf = BloomFilter(100000000, 0.001, 'log/'+strtime+'filter'+'.bloom')
    print "num_bits: "+str(bf.num_bits)
    print "num_hashes: "+str(bf.num_hashes)
    #bf.clear_all()

    #orderCount = 0
    #allCount = 0

    logf1 = open('log/'+strtime+'log1'+'.log', 'wb') #记录处理过的页面
    logf2 = open('log/'+strtime+'log2'+'.log', 'wb') #记录处理过的页面
    logAll = open('log/'+strtime+'all'+'.log', 'wb') #记录所有找到的链接
    aList.append(urlDefault)
    aList.append(urlSucceed)

    allCount += len(aList)
    for item in aList:
        bf.add(item)
    handlePage(aList.pop(0))
    logf.close()
    logAll.close()
'''
