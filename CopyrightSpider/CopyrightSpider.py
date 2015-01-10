# -*- coding: utf-8 -*-
#python3.4

import urllib.request, urllib.parse, urllib.error, http.cookiejar, http.client, threading
import time, os, re, importlib
import sys
import csv
from bs4 import BeautifulSoup
import socket
from random import randint

requestUrlPrefix = 'http://www.ccopyright.com.cn/cpcc/RRegisterAction.do?'

# for headers
ipAddress = ['191.124.5.2', '178.98.24.45, 231.67.9.28']
host = 'epub.sipo.gov.cn'
userAgent = [
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36']
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36',
    'Host': 'epub.sipo.gov.cn'}

#全局变量
gWriter = ''

title = ['关键词', '登记号', '分类号', '软件全称', '软件简称', '版本号', '著作权人（国籍）', '首次发表日期', '登记日期']

#-------------------------------------------------
class MyException(Exception):
    pass


#-------------------------------------------------
class DataFetcher(threading.Thread):
    def __init__(self, tId, writer):
        threading.Thread.__init__(self)
        self.tId = tId
        self.writer = writer

    def run(self):
        global kwNo, exitFlag
        while not exitFlag:
            kwLock.acquire()
            if (kwNo >= kwMax):
                #print('if')
                exitFlag = True
                break
            curKeyword = keywordList[kwNo]
            kwNo += 1
            kwLock.release()

            print(("Thread " + str(self.tId) + " get keyword:" + curKeyword))
            getDataByKw(curKeyword, writer)


#end class DataFetcher
#--------------------------------------------------
def getDataByKw(keyword, writer):
    pageNow = 1
    while True:
        #newkw = keyword.decode('gbk').encode('utf-8') #important
        if PY3:
            newkw = keyword.encode('gbk')
        else:
            newkw = keyword
        data = {'method': 'list', 'no': 'fck', 'sql_name': '', 'sql_regnum': '', 'sql_author': newkw,
                'curPage': str(pageNow), 'count': '100', 'sortOrder': '', 'sortLabel': ''}
        postData = urllib.parse.urlencode(data)
        requestUrl = requestUrlPrefix + postData
        #print(("requestUrl=" + requestUrl))
        #requestUrl = requestUrlPrefix+"method=list&no=fck&sql_name=&sql_regnum=&sql_author="+%C0%D6%CA%D3%CD%F8+"&curPage="+str(pageNow)+"&count=80&sortOrder=&sortLabel="
        req = urllib.request.Request(requestUrl, headers=getRandomHeaders())
        try:
            response = urllib.request.urlopen(req, timeout=10)
            m = response.read()
            #print "read m finish"
            #print(m.decode('gbk'))
        except socket.timeout as e:
            print("Socket timeout. Reconnect...")
            continue
        except urllib.error.URLError as e:
            print('URLError timeout. Reconnect...')
            continue
        except http.client.BadStatusLine as e:
            print('BadStatusLine. Reconnect...')
            continue
        else:
            if analyzeWeb(m, writer, [keyword]):
                print('    page: '+str(pageNow))
                pageNow += 1
                time.sleep(2)
                #break
            else:
                break
        #end while


#end def getDataByKw()
#--------------------------------------------------
def analyzeWeb(webcontent, writer, pre):
    soup = BeautifulSoup(webcontent.decode('gbk'))
    form = soup.find('form', {'name':'generalForm'})
    table_data = form.find_all('table')[1]
    list_tr = table_data.find_all('tr')
    if(len(list_tr) <= 2): return False
    line = 0
    for tr in list_tr:
        line += 1
        if(line < 3): continue
        td_list = tr.find_all('td')
        buffer = []
        buffer.extend(pre)
        registerNumber = td_list[0].get_text()
        classNumber = td_list[1].get_text()
        fullName = removeLF(td_list[2].get_text())
        shortName = td_list[3].get_text()
        version = td_list[4].get_text()
        author = td_list[5].get_text()
        publishDate = td_list[6].get_text()
        registerDate = td_list[7].get_text()
        buffer.extend([registerNumber, classNumber, fullName, shortName, version, author, publishDate, registerDate])
        writer.writerow(buffer)
    return True


#end def analyzeWeb
#--------------------------------------------------
#查看文件夹是否存在：若不存在，则创建
def createFolder(filedirectory):
    if os.path.isdir(filedirectory):
        pass
    else:
        os.makedirs(filedirectory)  #可以创建多级目录
    return


#end def createFolder
#----------------------------------------------
def createWriter(filedirectory, prefix=''):
    global PY3
    writers = []  #csv writer list
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    name_sheet = filedirectory + 'patent_' + strtime + '.csv'
    flag_newfile = True
    if (os.path.isfile(name_sheet)):
        flag_newfile = False
    if PY3:
        file_sheet = open(name_sheet, 'w', newline='')
    else:
        file_sheet = open(name_sheet, 'wb')
        file_sheet.write('\xEF\xBB\xBF')

    writer = csv.writer(file_sheet)
    if (flag_newfile):
        writer.writerow(title)

    return writer


#end def createWriters
#--------------------------------------------------
#生成一个随机的headers
def getRandomHeaders():
    ipNumber = len(ipAddress)
    agentNumber = len(userAgent)
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Cache-Control': 'no-cache', 'Content-Type': 'application/x-www-form-urlencoded',
               'User-Agent': userAgent[randint(0, agentNumber - 1)], 'Host': host,
               'X-Forwarded-For': ipAddress[randint(0, ipNumber - 1)], 'Pragma': 'no-cache'}
    return headers


#--------------------------------------------------
def readKeywordFile(filename):
    keywordList = []
    lineCount = 0
    try:
        configfile = open(filename, 'r')
        for line in configfile:
            keywordList.append(line.strip())
            lineCount += 1
        configfile.close()
    except:
        print('open keywords file ERROR!')

    print(('Keywords number:' + str(lineCount)))
    return keywordList


#end def readKeywordsFile
#--------------------------------------------------
def removeSpace(str):
    str = str.decode('utf-8', 'ignore').encode('utf-8')
    str = str.replace(' ', '')  #normal space
    str = str.replace('\r\n', '')
    str = str.replace('\n', '')
    str = str.replace('\xa0', '')  #remove &nbsp;
    str = str.replace('\u2002', '')  #remove &ensp;
    #print "removeSpace:"+str
    return str.strip()
#--------------------------------------------------
def removeLF(str):
    str = str.replace('\r\n', '')
    str = str.replace('\n', '')
    return str.strip()
#--------------------------------------------------
def test():
    html_doc = """
    <html><head><title>The Dormouse's story</title></head>
    <body>
    <p class="title">something<b>The Dormouses story</b>other</p>
    """
    soup = BeautifulSoup(html_doc)
    print(soup.p.text)
    pLi = soup.find('p', text=re.compile('something'), recursive=False)
    print(pLi)

#--------------------------------------------------
#global variable
startDate = ''
endDate = ''
threadCount = 1
kwNo = 0  #当前的关键词
kwMax = 100000  #keyword的个数
exitFlag = False
keywordFilename = 'keywords.txt'
keywordList = []
resultDirectory = 'datas/'
PY3 = True
#main
if __name__ == '__main__':
    importlib.reload(sys)
    #sys.set
    #sys.setdefaultencoding('utf8')  #系统输出编码置为utf8，解决输出时的乱码问题
    if sys.version > '3':
        PY3 = True
    else:
        PY3 = False

    print('*******************************************')
    print('*         Copyright Spider  v0111         *')
    print('*  Keywords need to be in "keywords.txt". *')
    print('*  Results will be in "datas" folder.     *')
    print('*******************************************')

    startTime = time.clock()
    keywordList = readKeywordFile(keywordFilename)
    kwMax = len(keywordList)
    createFolder(resultDirectory)
    writer = createWriter(resultDirectory)

    kwLock = threading.Lock()
    threads = []
    for i in range(threadCount):
        thread = DataFetcher(i + 1, writer)
        threads.append(thread)
    for t in threads: t.start()

    while (kwNo < kwMax): pass
    exitFlag = True

    for t in threads: t.join()

    print('Exit main thread.')
    endTime = time.clock()
    print(('[Total execute time]:' + str(endTime - startTime) + 's'))
    os.system('pause')
    #end main