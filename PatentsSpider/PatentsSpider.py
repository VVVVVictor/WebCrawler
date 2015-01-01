# -*- coding: utf-8 -*-

import urllib, urllib2, cookielib, httplib, threading
import sys, string, time, os, re
import csv
from bs4 import BeautifulSoup
import socket
from random import randint

requestUrl = 'http://epub.sipo.gov.cn/patentoutline.action'

#for headers
ipAddress = ['191.124.5.2', '178.98.24.45, 231.67.9.28']
host = 'epub.sipo.gov.cn'
userAgent = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36']
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36', 'Host':'epub.sipo.gov.cn'}

#全局变量
gWriter = ''

title = [u'关键词', u'类型', u'名称', u'申请公布号', u'申请公布日', u'申请号', u'申请日', u'申请人', u'发明人', u'地址', u'分类号', u'摘要']

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
    boxList = soup.find_all('div', class_='cp_box')
    for box in boxList:
        buffer = []
        title = box.h1.get_text().strip()
        liList = box.ul.find_all('li')
        publishId = re.match(u'(申请公布号|授权公告号)：(\w+)', liList[0].get_text()).group(2)
        publishDate = re.match(u'(申请公布日|授权公告日)：(\S+)', liList[1].get_text()).group(2)
        appId = re.match(u'(申请号)：(\d+)', liList[2].get_text()).group(2)
        appDate = re.match(u'(申请日)：(\S+)', liList[3].get_text().strip()).group(2)
        applicant = re.match(u'(申请人)：(\S+)', liList[4].get_text()).group(2)
        inventor = re.match(u'(发明人)：(.+)', liList[5].get_text()).group(2)
        address = re.match(u'(地址)：(\S+)', liList[7].get_text()).group(2)
        classCode = re.match(u'(分类号)：(\S+)全部', removeSpace(liList[8].get_text())).group(2)
        #print cleanString(box.find('div', class_='cp_jsh').get_text().strip())
        abstract = re.match(u'摘要：\s*(\S+)全部', removeSpace(box.find('div', class_='cp_jsh').get_text().strip())).group(1)
        buffer.extend([title, publishId, publishDate, appId, appDate, applicant, inventor, address, classCode, abstract])
        writer.writerow(buffer)
    #end for
    '''
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
    '''
    return True
#end def analyzeWeb
#-------------------------------------------------
def getPageMax(startDate, endDate):
    global pageMax
    data = {'city':'', 'startdate':startDate, 'enddate':endDate, 'page':'1'}
    postData = urllib.urlencode(data)
    req = urllib2.Request(airUrlpre, postData, getRandomHeaders())
    m = urllib2.urlopen(req).read()
    pageMaxStr = BeautifulSoup(m).find('a', text=re.compile(u'末页'))['href']
    pageMax = int(re.search('\d+', pageMaxStr).group())
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
def createWriter(filedirectory, prefix=''):
    writers = [] #csv writer list
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    name_sheet = filedirectory+'patent_'+strtime+'.csv';
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
def readKeywordsFile(filename):
    global keywordList
    lineCount = 0
    try:
        configfile = open(filename, 'r')
        for line in configfile:
            keywordList.append(line)
            lineCount += 1
        configfile.close()
    except:
        print('open keywords file ERROR!')
    
    print('Keywords number:'+str(lineCount))
#end def readKeywordsFile
#--------------------------------------------------
def removeSpace(str):
    str = str.replace('\r\n', '')
    str = str.replace('\n', '')
    str = str.replace('\u00A0', '')
    return str.strip()
#--------------------------------------------------
def test(keyword):
    data = {'showType':'1', 'strWord':'申请（专利权）人=\'%'+keyword+'%\'', 'seleted':'fmgb', 'numFMGB':'0', 'numFMSQ':'0', 'numSYXX':'0', 'numWGSQ':'0', 'pageSize':'3', 'pageNow':'1'}
    postData = urllib.urlencode(data)
    req = urllib2.Request(requestUrl, postData, getRandomHeaders())
    try:
        response = urllib2.urlopen(req)
        m = response.read()
        return m
    except:
        print "test error"
#--------------------------------------------------
#global variable
startDate = ''
endDate = ''
threadCount = 2
pageNo = 1 #当前的页码
pageMax = 100000 #最大页数
exitFlag = False
keywordsFilename = 'keywords.txt'
keywordList = []
#main
if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8') #系统输出编码置为utf8，解决输出时的乱码问题
    
    print '*******************************************'
    print '*          Patents Spider  v0101          *'
    print '*  Keywords need to be in "keywords.txt". *'
    print '*  Results will be in "datas/" folder.    *'
    print '*******************************************'
    
    readKeywordsFile(keywordsFilename)
    filedirectory = 'datas/'
    createFolder(filedirectory)
    writer = createWriter(filedirectory)
    
    m = test('特锐德')
    #print m
    analyzeWeb(m, writer)
    
    '''
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
    '''
    print('Exit main thread.')
#end main