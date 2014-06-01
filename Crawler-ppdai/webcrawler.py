# -*- coding: utf-8 -*-

import urllib, urllib2, cookielib
import sys, string, time, os, re
import csv
from bs4 import BeautifulSoup
import socket
from tools_ppdai import *
#import xlrd, xlwt, xlutils
#from xlutils.copy import copy
#import shutil

#全局变量
rows_sheet = [2, 1, 2, 1, 1] #5个sheet当前最后一行
writers = [] #csv writers[0-4]

def getData_ppdai(url, begin_page, end_page, filedirectory):
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
    for i in range(1,6):
        name_sheet = filedirectory+str(begin_page)+'-'+str(end_page)+'.'+strtime+'_sheet'+str(i)+'.csv'
        
        file_sheet = open(name_sheet, 'wb')
        files.append(file_sheet)
        file_sheet.write('\xEF\xBB\xBF') #防止windows下excel打开显示乱码
        
        writer_sheet = csv.writer(file_sheet)
        writers.append(writer_sheet)
        writer_sheet.writerow(titles[i-1])
    #end for
    
    lastpage = begin_page #记录抓取的最后一个有效页面
    
    for i in range(begin_page, end_page+1):
        req = urllib2.Request(url+str(i), None, headers =  getRandomHeaders())
        try:
            response = urllib2.urlopen(req)
            #部分页面会重定向到/default.html，（如400001），以此来判定
            r = re.search(str(i), response.geturl())
            if not r:
                print(str(i)+u': 页面重定向')
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
                print('[ERROR] When get order page!')
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
            #等待一定时间后重新连接
            time.sleep(CLOSE_WAIT_TIME)
            login()
            i = lastpage
            continue
        #end try&except
        response.close()
        lostPageCount = 0
        
        '''writing files'''
        strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
        sName = filedirectory + dataFolder + 'order_' + str(i).zfill(LIST_LENGTH) +'_'+strtime+ '.html'
        print('Downloading ' + str(i) + ' web page...')
        
        #保存网页文件
        f = open(sName, 'wb')
        f.write(m)
        f.close()
        

        '''使用BeautifulSoup分析网页'''
        analyzeData_ppdai(i, m, writers)
        
        fileCount = fileCount + 1
        time.sleep(GAP_TIME)
    #endfor

    #resultExcel.save(filedirectory+'result_'+str(begin_page)+'_'+str(end_page)+'.'+strtime+'.xls')
    
    for i in range(5):
        files[i].close()
        
    #logfile.close()
    endtime = time.clock()
    print(u"[file number]:"+str(fileCount))
    print(u'[execute time]:'+str(endtime - starttime))
    return

#--------------------------------------------------
#main
reload(sys)
sys.setdefaultencoding('utf-8') #系统输出编码置为utf8，解决输出时的乱码问题

while True:
    try:
        begin_page = int(input(u'start page:\n'))
        if begin_page < 100000:
            print(u'Your number has been modified to 100000, since this number should be no less than 100000. ')
            begin_page = 100000
        break
    except:
        print('Illegal number. Please input again:')
        continue
    
while True:
    try:
        end_page = int(input(u'end page:\n'))
        if end_page < begin_page:
            print(u'end_page should not less than begin_page. Please input again: ')
            continue
        break
    except:
        print('Illegal number. Please input again:')
        continue

filedirectory = getConfig()

createFolder(filedirectory)
createFolder(filedirectory+dataFolder)
createFolder(filedirectory+userFolder)

print('[Data Path] '+filedirectory)
if login():
    getData_ppdai(ppdaiurl, begin_page, end_page, filedirectory)
