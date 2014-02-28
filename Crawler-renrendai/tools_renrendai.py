#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

import urllib, urllib2, cookielib
import sys, string, time, os, re
import csv
from bs4 import BeautifulSoup
import socket

configfileName = 'config'
filedirectory = u'D:\\datas\\pythondatas\\renrendai\\'

#For login
urlLogin = u'https://www.renrendai.com/j_spring_security_check'
urlIndex = u'http://www.renrendai.com/'
username = u'15120000823'
password = u'wmf123456'
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36', 'Host':'www.renrendai.com'}

#--------------------------------------------------
#读取配置文件
def getConfig():
    global filedirectory, username, password
    try:
        configfile = open(os.getcwd()+'\\'+configfileName, 'r')
        #line = configfile.readline()
        pattern = re.compile(u'\s*(\w+)\s*=\s*(\S+)\s*')
        for line in configfile:
            #print line
            m = pattern.match(line)
            if m:
                if m.group(1) == u'filedirectory':
                    filedirectory =  m.group(2)+'\\'
                    '''
                    tempchar = filedirectory[len(filedirectory)-1]
                    if tempchar != u'\\' and tempchar != u'/':
                        print('temp')
                        filedirectory = filedirectory + '\\'
                        '''
                elif m.group(1) == u'username':
                    username = m.group(2)
                elif m.group(1) == u'password':
                    password = m.group(2)
                #print filedirectory
        configfile.close()
    except:
        configfile = open(os.getcwd()+'\\'+configfileName, 'wb')
        configfile.write('filedirectory = '+filedirectory+'\n')
        configfile.write('username = '+username+'\n')
        configfile.write('password = '+password+'\n')
        configfile.close()
        print('Create new config file!')
    
    print('[CONFIG]')
    print('filedirectory = '+filedirectory)
    print('username = '+username)
    print('password = '+password)
    return filedirectory
#end def getConfig()
    
#--------------------------------------------------
#登录函数
def login():
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

    data = {'j_username':username, 'j_password':password, 'rememberme':'on', 'targetUrl':'http://www.renrendai.com', 'returnUrl':''}
    postdata = urllib.urlencode(data)

    try:
        req = urllib2.Request(urlLogin, postdata, headers)
        result = urllib2.urlopen(req)
        if urlIndex != result.geturl(): #通过返回url判断是否登录成功
            print(u'[FAIL]Wrong USERNAME or PASSWORD. Please try again!')
            return False
        result.close()
    except:
        print(u'[FAIL]Login failed. Please try again!')
        return False
    return True
#end def login()

#--------------------------------------------------
#查看文件夹是否存在：若不存在，则创建
def createFolder(filedirectory):
    if os.path.isdir(filedirectory):
        pass
    else:
        os.makedirs(filedirectory) #可以创建多级目录
    return

#--------------------------------------------------
def analyzeData(webcontent):
    soup = BeautifulSoup(webcontent)
    
    if soup.find('img', {'alt':'404'}):
        return False #页面404
        
        
    return True
    