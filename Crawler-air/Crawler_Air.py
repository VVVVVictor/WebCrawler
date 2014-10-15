# -*- coding: utf-8 -*-

import urllib, urllib2, cookielib, httplib, threading
import sys, string, time, os, re
import csv
from bs4 import BeautifulSoup
import socket
from random import randint

airUrlpre = 'http://datacenter.mep.gov.cn/report/air_daily/air_dairy_aqi.jsp?'

#for headers
ipAddress = ['191.124.5.2', '178.98.24.45, 231.67.9.28']
host = 'datacenter.mep.gov.cn'
userAgent = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36']
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36', 'Host':'datacenter.mep.gov.cn'}

#全局变量
gWriter = ''

title = [u'序号', u'城市', u'日期', u'污染指数', u'首要污染物', u'空气质量级别', u'空气质量状况']

#-------------------------------------------------
class DataFetcher(threading.Thread):
    def __init__(self, tId, writer):
        threading.Thread.__init__(self)
        self.tId = tId
        self.writer = writer
    def run(self):
        global pageNo, exitFlag
        while not exitFlag:
            pageLock.acquire()
            #print('pageNo = ' + str(pageNo))
            #print('pageMax = ' + str(pageMax))
            if(pageNo > pageMax):
                #print('if')
                exitFlag = True
                break
            curPage = pageNo
            pageNo += 1
            pageLock.release()
            print('Thread '+str(self.tId)+': download page '+str(curPage)+'...')
            data = {'city':'', 'startdate':startDate, 'enddate':endDate, 'page':curPage}
            postData = urllib.urlencode(data)
            req = urllib2.Request(airUrlpre, postData, getRandomHeaders())
            try:
                response = urllib2.urlopen(req)
                m = response.read()
                #print(m)
            except (urllib2.URLError) as e:
                if hasattr(e, 'code'):
                    print(str(e.code)+': '+str(e.reason))
                else:
                    print(e.reason)
                continue
            except socket.error as e:
                print('ERROR] Socket error: '+str(e.errno))
                continue
            
            if not analyzeWeb(m, self.writer):
                exitFlag = True
#end class DataFetcher
            
#--------------------------------------------------
def analyzeWeb(webcontent, writer):
    soup = BeautifulSoup(webcontent)
    table = soup.find('table', {'id':'report1'})
    list_tr = table.find_all('tr')
    itemCount = 0
    for item in list_tr:
        itemCount += 1
        if(itemCount < 3):continue;
        if(itemCount > 32): break;
        if(item['height'] != '30'): break;
        buffer = []
        list_td = item.find_all('td')
        for td in list_td:
            buffer.append(td.get_text())
        writer.writerow(buffer)
    return True
#end def analyzeWeb
#-------------------------------------------------
def getPageMax(startDate, endDate):
    global pageMax
    data = {'city':'', 'startdate':startDate, 'enddate':endDate, 'page':'1'}
    postData = urllib.urlencode(data)
    req = urllib2.Request(airUrlpre, postData, getRandomHeaders())
    m = urllib2.urlopen(req).read()
    pageMax = BeautifulSoup(m).find('td', class_='report1_11').find('font').find_next('font').get_text()
    pageMax = int(pageMax)
    print('\nTotal Page Number:'+str(pageMax))
#edn def getPageMax
#--------------------------------------------------
#查看文件夹是否存在：若不存在，则创建
def createFolder(filedirectory):
    if os.path.isdir(filedirectory):
        pass
    else:
        os.makedirs(filedirectory) #可以创建多级目录
    return
#end def createFolder
#----------------------------------------------
def createWriter(filedirectory, i_startDate, i_endDate, prefix=''):
    writers = [] #csv writer list
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    name_sheet = filedirectory+i_startDate+'-'+i_endDate+'.csv';
    flag_newfile = True
    if(os.path.isfile(name_sheet)):
        flag_newfile = False
    file_sheet = open(name_sheet, 'wb')
    file_sheet.write('\xEF\xBB\xBF')
    
    writer = csv.writer(file_sheet)
    if(flag_newfile):
        writer.writerow(title)
        
    return writer
#end def createWriters
#--------------------------------------------------
#生成一个随机的headers
def getRandomHeaders():
    ipNumber = len(ipAddress)
    agentNumber = len(userAgent)
    headers = {'User-Agent': userAgent[randint(0, agentNumber-1)], 'Host': host, 'X-Forwarded-For': ipAddress[randint(0, ipNumber-1)]}
    return headers
#--------------------------------------------------
#global variable
startDate = ''
endDate = ''
threadCount = 2
pageNo = 1 #当前的页码
pageMax = 100000 #最大页数
exitFlag = False
#main
if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8') #系统输出编码置为utf8，解决输出时的乱码问题
    
    print '*******************************'
    print '*    Air dairy Spider v1015   *'
    print '*******************************'
    
    while True:
        try:
            raw_start = raw_input(u'start date:')
            i_startDate = int(raw_start)
            if i_startDate < 20100101:
                print('Start date must be after 20100101.')
                continue;
            break
        except:
            print('Illegal date. Input again!')
            continue;
        
    while True:
        try:
            raw_end = raw_input(u'end date:')
            i_endDate = int(raw_end);
            if i_endDate < i_startDate:
                print('End date must be after start date.');
                continue;
            break
        except:
            print('Illegal date. Input again!')
            continue;

    filedirectory = 'datas/'
    createFolder(filedirectory)
    #getProxyList()
    i_startDate = str(i_startDate)+''
    i_endDate = str(i_endDate)+''
    startDate = i_startDate[0:4]+'-'+i_startDate[4:6]+'-'+i_startDate[6:8]
    endDate = i_endDate[0:4]+'-'+i_endDate[4:6]+'-'+i_endDate[6:8]
    
    print('[Start Date] '+startDate)
    print('[End   Date] '+endDate)
    print('[Data  Path] '+filedirectory)
    gWriter = createWriter(filedirectory, i_startDate, i_endDate)
    getPageMax(startDate, endDate)
    #20100101
    pageLock = threading.Lock()
    threads = []
    for i in xrange(threadCount):
        thread = DataFetcher(i+1, gWriter)
        threads.append(thread)
    for t in threads:
        t.start()
        
    while(pageNo <= pageMax): pass
    exitFlag = True
    
    for t in threads: t.join()
    print('Exit main thread.')
#end main