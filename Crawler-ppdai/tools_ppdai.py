#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = "Wang Miaofei"

import urllib, urllib2, cookielib
import sys, string, time, os, re, json
import csv
from bs4 import BeautifulSoup
import socket
from random import randint

#常量参数
LOST_PAGE_LIMIT = int(10)
LIST_LENGTH = int(6)
GAP_TIME = int(1)#连续抓取时的等待时间
SLEEP_TIME = int(20) #抓取最新页面的等待时间
CLOSE_WAIT_TIME = int(100) #爬虫被服务器强行关闭后的等待时间
ENABLE_PROXY = True

MAX_PAGE = int(10000000)

ppdaiurl = u'http://www.ppdai.com/list/'
ppdai_user_url = u'http://www.ppdai.com/user/'

#记录相关
logfileName = 'log'
configfileName = 'config'
datafilePrefix = 'data_sheet'
filedirectory = u'D:\\datas\\pythondatas\\ppdailist\\'
dataFolder = u'pages/' #保存订单的文件夹名字
userFolder = u'users/' #保存用户的文件夹名字

#登录相关
urlAuth = u'http://www.ppdai.com/Json/SyncReply/Auth'
urlAccount = u'http://www.ppdai.com/account'
username = 'victor1991@126.com'
password = 'wmf123456'
domain = 'ppdai.com'
ipAddress = ['10.0.0.1', '191.234.5.2', '178.98.246.45, 231.67.9.23']
host = 'www.ppdai.com'
userAgent = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36']

attrList = u'借贷单号,标题,金额（元）,年利率,期限（月）,是否结束（1表示已结束）,借款人id,借入信用,借出信用'
titles = (('抓取时间','抓取时刻','订单号','安','非','赔','保','农','订单标题','金额(元）','年利率','期限（月）','还款方式','每月还款金额','进度','借款状态','剩余时间','结束时间','总投标数','浏览量','借款id','借入信用等级','借入信用分数','借出信用分数','成功次数','流标次数','身份认证','视频认证','学历认证','手机认证','借款目的','性别','年龄','婚姻状况','文化程度','住宅状况','是否购车','户口所在地','毕业学校','学历','学习形式','网站认证','淘宝网认证','卖家信用等级（皇冠数*10+钻石数*1）','关于我','我想要使用这笔款项做什么','我的还款能力说明'),
    ('抓取时间','抓取时刻','订单号','投标ID','当前利率（%）','投标金额','投标时间（天）','投标时间（时刻）'),
    ('抓取时间','抓取时刻','借款ID','借入信用','借出信用','性别','年龄分档（1(20-25)  2(26-31)  3(32-38)  4(>39)）','目前身份','注册时间','投标次数','坏帐计提/借出总金额','加权投标利率（反映风险偏好）','最后更新时间','身份认证','视频认证','学历认证','手机认证','网上银行充值认证','全款还清次数','全款还清得分','逾期且还款次数','资料得分','社区得分','身份认证','视频认证','学历认证','手机认证','投标成功次数','收到完整本息笔数','收到本息次数','逾期笔数'),
    ('抓取时间','抓取时刻','借款ID','订单号','订单标题','借款金额（元）','年利率（%）','借款期限（月）','状态','信用等级','借款进度','已完成投标数','时间'),
    ('抓取时间','抓取时刻','借款ID','订单号','标题','年利率（%）','有效金额','状态（1表示成功，0表示失败）','投标时间（天）','投标时间（时刻）')
    )
    
'''登录网页'''
def login():
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    #opener.addheaders = headers
    urllib2.install_opener(opener)
    
    data = {'UserName':username, 'Password':password, 'Continue':'/default'}
    postdata = urllib.urlencode(data)
    
    try:
        req = urllib2.Request(urlAuth, postdata, headers = getRandomHeaders())
        result = urllib2.urlopen(req)
        result.close()
        #for index, cookie in enumerate(cj):
        #    print '[',index,']',cookie
            
        req2 = urllib2.Request(urlAccount, headers = getRandomHeaders())
        result2 = opener.open(req2)
        result2.close()
        return True
    except:
        print(u'[FAIL]Login failed. Please try again!')
        return False
#end def login()

'''查看文件夹是否存在：若不存在，则创建'''
def createFolder(filedirectory):
    if os.path.isdir(filedirectory):
        pass
    else:
        os.makedirs(filedirectory) #可以创建多级目录
    return

#--------------------------------------------------
def getConfig():
    global filedirectory
    try:
        configfile = open(os.getcwd()+'/'+configfileName, 'r')
        #line = configfile.readline()
        pattern = re.compile(u'\s*(\w+)\s*=\s*(\S+)\s*')
        for line in configfile:
            #print line
            m = pattern.match(line)
            if m:
                if m.group(1) == u'filedirectory':
                    filedirectory =  m.group(2)+'/'
                elif m.group(1) == u'username':
                    username = m.group(2)
                elif m.group(1) == u'password':
                    password = m.group(2)
                #print filedirectory
        configfile.close()
    except:
        configfile = open(os.getcwd()+'/'+configfileName, 'wb')
        configfile.write('filedirectory = '+filedirectory+'\n')
        configfile.write('username = '+username+'\n')
        configfile.write('password = '+password+'\n')
        configfile.close()
        print('Create new config file!')
    
    print('[CONFIG]')
    print('filedirectory = '+filedirectory)
    print('username = '+username)
    print('password = '+password)
    return

#--------------------------------------------------
def setProxy():
    if ENABLE_PROXY:
        proxy_handler = urllib2.ProxyHandler({"http": '111.206.81.248:80'})
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)
#--------------------------------------------------
#生成一个随机的headers
def getRandomHeaders():
    ipNumber = len(ipAddress)
    agentNumber = len(userAgent)
    headers = {'User-Agent': userAgent[randint(0, agentNumber-1)], 'Host': host, 'X-Forwarded-For': ipAddress[randint(0, ipNumber-1)]}
    return headers