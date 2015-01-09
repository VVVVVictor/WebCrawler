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

title = ['登记号', '分类号', '软件全称', '软件简称', '版本号', '著作权人（国籍）', '首次发表日期', '登记日期']

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
                'curPage': str(pageNow), 'count': '80', 'sortOrder': '', 'sortLabel': ''}
        postData = urllib.parse.urlencode(data)
        requestUrl = requestUrlPrefix + postData
        print(("requestUrl=" + requestUrl))
        if requestUrl:
            break
        #requestUrl = requestUrlPrefix+"method=list&no=fck&sql_name=&sql_regnum=&sql_author="+%C0%D6%CA%D3%CD%F8+"&curPage="+str(pageNow)+"&count=80&sortOrder=&sortLabel="
        req = urllib.request.Request(requestUrl, headers=getRandomHeaders())
        try:
            response = urllib.request.urlopen(req, timeout=10)
            m = response.read()
            #print "read m finish"
            print(m)
        except socket.timeout as e:
            print("    Socket timeout. Reconnect...")
            continue
        except urllib.error.URLError as e:
            print('    URLError timeout. Reconnect...')
            continue
        except http.client.BadStatusLine as e:
            print('    BadStatusLine. Reconnect...')
            continue
        '''
        else:
            if analyzeWeb(m, writer, [keyword]):
                print('    page: '+str(pageNow))
                pageNow += 1
                time.sleep(2)
                #break
            else:
                break
        '''
        break
        #end while


#end def getDataByKw()
#--------------------------------------------------
def analyzeWeb(webcontent, writer, pre):
    soup = BeautifulSoup(webcontent)
    boxList = soup.find_all('div', class_='cp_box')
    if (len(boxList) == 0): return False
    for box in boxList:
        buffer = []
        buffer.extend(pre)
        #print(removeSpace(box.h1.get_text().strip()))
        m_title = re.match('\[(发明公布|发明授权|实用新型|外观设计|发明审定)\]\s*(\S+)', removeSpace(box.h1.get_text().strip()))
        title = m_title.group(2)
        type = m_title.group(1)
        liList = box.ul.find_all('li')

        publishId = publishDate = appId = appDate = applicant = inventor = address = ''
        boxUl = box.ul
        publishIdLi = boxUl.find('li', text=re.compile('(申请公布号|授权公告号|审定号)：'))
        if publishIdLi:
            publishId = re.match('(申请公布号|授权公告号|审定号)：(\w+)', publishIdLi.get_text()).group(2)
        publishDateLi = boxUl.find('li', text=re.compile('(申请公布日|授权公告日|审定公告日)：'))
        if publishDateLi:
            publishDate = re.match('(申请公布日|授权公告日|审定公告日)：(\S+)', publishDateLi.get_text().strip()).group(2)
        appIdLi = boxUl.find('li', text=re.compile('(申请号)：'))
        if appIdLi:
            appId = re.match('(申请号)：(\w+)', appIdLi.get_text()).group(2)
        appDateLi = boxUl.find('li', text=re.compile('(申请日)：'))
        if appDateLi:
            appDate = re.match('(申请日)：(\S+)', appDateLi.get_text().strip()).group(2)
        #applicantLi = boxUl.find('li', text=re.compile(u'(申请人|专利权人)：'))
        applicantLi = appDateLi.find_next_sibling('li', class_='wl228')
        if applicantLi:
            applicant = re.match('(申请人|专利权人)：(.+)', removeSpace(applicantLi.get_text())).group(2)
        #inventorLi = boxUl.find('li', text=re.compile(u'(发明人|设计人)：'))
        inventorLi = applicantLi.find_next_sibling('li', class_='wl228')
        if inventorLi:
            inventor = re.match('(发明人|设计人)：(.+)', removeSpace(inventorLi.get_text())).group(2)
        addressLi = boxUl.find('li', text=re.compile('(地址)：'))
        #print addressLi
        if addressLi:
            address = re.match('(地址)：(\S+)', addressLi.get_text()).group(2)

        #classLi = boxUl.find('li', text=re.compile(u'(分类号)：(.*)')) #可能是因为格式嵌套
        classLi = addressLi.find_next_sibling('li')
        #print classLi.text
        #classLi = boxUl.find('li', text=re.compile(u'(分类号)：(.*)'))
        [quanbu.extract() for quanbu in classLi('a')]
        collapsDiv = classLi.find('div', {'style': 'display:none;'})
        agency = agent = priority = pctDate = pctApp = pctPublish = compareFile = ''  #专利代理机构，代理人，优先权，PCT进入国家阶段日，PCT申请数据，PCT公布数据，对比文件
        classCodeHalf = ''  #分类号后半部分
        if collapsDiv:
            #collapsLiList = collapsDiv.find_all('li')
            agencyLi = collapsDiv.find('li', text=re.compile('专利代理机构：'))
            if agencyLi:
                agency = re.match('专利代理机构：(.+)', agencyLi.get_text()).group(1)
                agencyLi.extract()
            agentLi = collapsDiv.find('li', text=re.compile('代理人：'))
            if agentLi:
                agent = re.match('代理人：(.+)', agentLi.get_text()).group(1)
                agentLi.extract()
            priorityLi = collapsDiv.find('li', text=re.compile('优先权：'))
            if priorityLi:
                priority = re.match('(本国)?优先权：(.+)', priorityLi.get_text()).group(2)
                priorityLi.extract()
            pctDateLi = collapsDiv.find('li', text=re.compile('PCT进入国家阶段日：'))
            if pctDateLi:
                pctDate = re.match('PCT进入国家阶段日：(.+)', pctDateLi.get_text()).group(1)
                pctDateLi.extract()
            pctAppLi = collapsDiv.find('li', text=re.compile('PCT申请数据：'))
            if pctAppLi:
                pctApp = re.match('PCT申请数据：(.+)', pctAppLi.get_text()).group(1)
                pctAppLi.extract()
            pctPublishLi = collapsDiv.find('li', text=re.compile('PCT公布数据：'))
            if pctPublishLi:
                pctPublish = re.match('PCT公布数据：(.+)', pctPublishLi.get_text()).group(1)
                pctPublishLi.extract()
            compareFileLi = collapsDiv.find('li', text=re.compile('对比文件：'))
            if compareFileLi:
                compareFile = re.match('对比文件：(.+)', compareFileLi.get_text()).group(1)
                compareFileLi.extract()
            classCodeHalf = removeSpace(collapsDiv.get_text().strip())
            collapsDiv.extract()

        classCode = re.match('(分类号)：(.+)', removeSpace(classLi.get_text())).group(2)
        classCode += classCodeHalf
        #if len(classCode)>2 and classCode[len(classCode)-2:len(classCode)] == u'全部':
        #    classCode = classCode[0:len(classCode)-2]
        abstractTag = box.find('div', class_='cp_jsh')
        [quanbu.extract() for quanbu in abstractTag('a')]
        abstract = re.match('(摘要|简要说明)：\s*(\S*)',
                            removeSpace(box.find('div', class_='cp_jsh').get_text().strip())).group(2)
        #if len(abstract)>2 and abstract[len(abstract)-2:len(abstract)] == u'全部':
        #    abstract = abstract[0:len(abstract)-2]
        buffer.extend(
            [type, title, publishId, publishDate, appId, appDate, applicant, inventor, address, classCode, agency,
             agent, priority, pctDate, pctApp, pctPublish, compareFile, abstract])
        writer.writerow(buffer)
    #end for
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
    #sys.setdefaultencoding('utf8')  #系统输出编码置为utf8，解决输出时的乱码问题
    if sys.version > '3':
        PY3 = True
    else:
        PY3 = False

    print('*******************************************')
    print('*         Copyright Spider  v0109         *')
    print('*  Keywords need to be in "keywords.txt". *')
    print('*  Results will be in "datas" folder.     *')
    print('*******************************************')

    startTime = time.clock()
    keywordList = readKeywordFile(keywordFilename)
    kwMax = len(keywordList)
    createFolder(resultDirectory)
    writer = createWriter(resultDirectory)
    #test()
    '''
    m = test('特锐德')
    print m
    analyzeWeb(m, writer)
    '''

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