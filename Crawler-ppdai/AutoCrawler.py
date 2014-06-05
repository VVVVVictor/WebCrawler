# -*- coding: utf-8 -*-

import urllib, urllib2, cookielib
import sys, string, time, os, re
import csv
from bs4 import BeautifulSoup
import socket, errno
from tools_ppdai import *
#import xlrd, xlwt, xlutils
#from xlutils.copy import copy
#import shutil

headers={'Referer':'http://www.ppdai.com/default.htm','User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)', 'Host':'www.ppdai.com'}

#全局变量
rows_sheet = [2, 1, 2, 1, 1] #5个sheet当前最后一行
writers = [] #csv writers[0-4]

def getData_ppdai(url, filedirectory, begin_page, end_page=MAX_PAGE):
    global rows_sheet
    global writers

    print(u'\nSTART to get webpages from: '+str(begin_page))
    starttime = time.clock()
    lostPageCount = int(0) #记录连续404的页面个数，若该数值大于LOST_PAGE_LIMIT，则认为已录完数据
    fileCount = 0

    '''创建log文件'''
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    #resultExcel = copy(xlrd.open_workbook(filedirectory+'template.xls'))
    
    files = []
    writers = [] #清空原有csv writers
    
    #logfile = open(filedirectory+logfileName, 'wb')
    for i in range(1,6):
        name_sheet = filedirectory+datafilePrefix+str(i)+'.csv'
        #判断文件是否存在，以决定是否加标题行
        flag_newfile = True
        if os.path.isfile(name_sheet):
            flag_newfile = False
            
        file_sheet = open(name_sheet, 'ab')
        files.append(file_sheet)
        file_sheet.write('\xEF\xBB\xBF') #防止windows下excel打开显示乱码
        
        writer_sheet = csv.writer(file_sheet)
        writers.append(writer_sheet)
        if flag_newfile:
            writer_sheet.writerow(titles[i-1])
    #endfor
    
    lastpage = begin_page - 1 #记录抓取的最后一个有效页面
    
    
    for i in range(begin_page, end_page+1):
        lastlastpage = lastpage #用于判断lastpage是否更新
        req = urllib2.Request(url+str(i), None, getRandomHeaders())
        try:
            #response = responseFromUrl(url+str(i))
            req.
            response = urllib2.urlopen(req)
            #部分页面会重定向到/default.html，（如400001），以此来判定
            r = re.search(str(i), response.geturl())
            if not r:
                print('页面重定向')
                continue
            
            m = response.read()
            lastpage = i
        except (urllib2.URLError) as e:
            if hasattr(e, 'code') and e.code == 404:
                lostPageCount = lostPageCount + 1
                if(lostPageCount > LOST_PAGE_LIMIT):
                    print('YOU HAVE GOT THE LASTEST PAGE!')
                    break
                else:
                    continue #only a few pages are lost
            elif hasattr(e, 'code') and e.code == 403:
                login()
                i = lastpage
                continue
            else:
                if hasattr(e, 'code'):
                    print(str(e.code)+': '+str(e.reason))
                else:
                    print(str(e.reason))
                i = lastpage
                continue
        except socket.error as e:
            print('[ERROR] Socket error: '+str(e.errno))
            if e.errno == 10054: #被服务器端强行关闭
                print('[ERROR] Socket was closed by the server.\n Trying to reconnect...')
            #将最新页面写入log文件中
            logfile = open(filedirectory+logfileName, 'wb')
            logfile.write('LatestPage = '+str(lastpage))
            logfile.close()
            #等待一定时间后重新连接
            time.sleep(CLOSE_WAIT_TIME)
            login()
            i = lastpage #重新获取最新页面
            continue
            
        #end try&except
        response.close()
        lostPageCount = 0
        
        '''writing files'''
        strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
        sName = filedirectory + dataFolder + 'order_'  + str(i).zfill(LIST_LENGTH) +'_'+strtime+ '.html'
        print('Downloading ' + str(i) + ' web page...')
        
        #保存网页文件
        f = open(sName, 'wb')
        f.write(m)
        f.close()

        '''使用BeautifulSoup分析网页'''
        analyzeData_ppdai(i, m, writers)
        
        fileCount = fileCount + 1
        
        #将最新页面写入log文件中
        if lastpage != lastlastpage:
            logfile = open(filedirectory+logfileName, 'wb')
            logfile.write('LatestPage = '+str(lastpage))
            logfile.close()
        
        time.sleep(GAP_TIME)
    #endfor

    #resultExcel.save(filedirectory+'result_'+str(begin_page)+'_'+str(end_page)+'.'+strtime+'.xls')
    
    #logfile.close()
    
    for i in range(5):
        files[i].close()
        
    endtime = time.clock()
    print(u"[file number]:"+str(fileCount))
    print(u'[execute time]:'+str(endtime - starttime))
    return

#--------------------------------------------------
def getLatestPage():
    try:
        logfile = open(filedirectory+logfileName, 'r')
        line = logfile.readline()
        
        pattern = re.compile(u'\s*(LatestPage)\s*=\s*(\d+)\s*')
        m = pattern.match(line)
        latestPage = 651850 #default
        if m:
            latestPage =  m.group(2)
        logfile.close()
    except:
        latestPage = 460000
        #创建log文件
        logfile = open(filedirectory+logfileName, 'wb')
        logfile.write('LatestPage = '+str(latestPage))
        logfile.close()
        
    return latestPage

#--------------------------------------------------
#main
reload(sys)
sys.setdefaultencoding('utf-8') #系统输出编码置为utf8，解决输出时的乱码问题

filedirectory = getConfig()

createFolder(filedirectory)
createFolder(filedirectory+dataFolder)
createFolder(filedirectory+userFolder)
getProxy()

print('[Data Path] '+filedirectory)
if login():
    #setProxy()
    tempCount = 0
    while True:
        latestpage = int(getLatestPage())
        getData_ppdai(ppdaiurl, filedirectory, latestpage+1,)
        time.sleep(SLEEP_TIME)
        '''
        tempCount += 1
        if(tempCount > 400):
            break
        '''
