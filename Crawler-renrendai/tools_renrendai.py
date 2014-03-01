#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

import urllib, urllib2, cookielib
import sys, string, time, os, re, json
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
    
    ### 分析script ###
    jsonString = soup.find(id = 'credit-info-data').string
    #jsonString = jsonString.replace('"[', '[').replace(']"', ']') #多余引号导致分析错误
    scriptData = json.loads(jsonString)
    
    loanData = scriptData['data']['loan']
    loanId = loanData['loanId']
    title = loanData['title']
    borrowType = loanData['borrowType']
    amount = loanData['amount']
    interest = loanData['interest']
    months = loanData['months']
    
    userId = loanData['borrowerId']
    username = loanData['nickName']
    borrowerLevel = loanData['borrowerLevel']
    
    leftMonths = loanData['leftMonths'] #剩余期数（月）
    
    #soup = soup.find('body') #只从body中提取数据，出现了莫名截断的问题 TODO
    #print soup
    guaranteeType = repayTyep = ''
    prepaymentRate = repayEachMonth = '0'
    #保障方式
    tag_guaranteeType = soup.find('span', text = u'保障方式')
    if tag_guaranteeType:
        guaranteeType = tag_guaranteeType.find_next_sibling('span').contents[0]
        print guaranteeType
    #还款方式
    tag_repayType = soup.find('span', text=u'还款方式')
    if tag_repayType:
        repayType = tag_repayType.find_next_sibling('span').contents[0]
        print repayType
    #提前还款费率
    tag_prepaymentRate = soup.find('span', text=u'提前还款费率')
    if tag_prepaymentRate:
        prepaymentRate = tag_prepaymentRate.find_next_sibling('span').find('em').string
        print prepaymentRate
    #月还本息    
    tag_repayEachMonth = soup.find('span', text=u'月还本息（元）')
    if tag_repayEachMonth:
        repayEachMonth = tag_repayEachMonth.find_next_sibling('span').find('em').string
        repayEachMonth = repayEachMonth.replace(',', '')
        print repayEachMonth
    
    #待还本息
    amountToRepay = 0
    tag_amountToRepay = soup.find('em', text=re.compile(u'待还本息\w*'))
    if tag_amountToRepay:
        amountToRepay = tag_amountToRepay.find_next_sibling('span').string.replace(',', '')
        amountToRepay = re.search(r'\d+', amountToRepay).group()
    print amountToRepay
    
    ###用户个人信息###
    tag_userinfo = soup.find('div', class_='ui-tab-content-basic')
    list_userinfo = tag_userinfo.find('ul').find_all('li')
    #print list_userinfo
    company = list_userinfo[1].find(class_='tab-list-value').string
    incomeRange = list_userinfo[2].find(class_='tab-list-value').string
    age = list_userinfo[3].find(class_='tab-list-value').string
    companyScale = list_userinfo[4].find(class_='tab-list-value').string
    house = list_userinfo[5].find(class_='icon-check-checked').next_sibling
    education = list_userinfo[6].find(class_='tab-list-value').string
    position = list_userinfo[7].find(class_='tab-list-value').string
    houseLoan = list_userinfo[8].find(class_='icon-check-checked').next_sibling
    school = list_userinfo[9].find(id='university')['title']
    city = list_userinfo[10].find(class_='tab-list-value').string
    car = list_userinfo[11].find(class_='icon-check-checked').next_sibling
    marriage =list_userinfo[12].find(class_='tab-list-value').string
    workTime = list_userinfo[13].find(class_='tab-list-value').string
    carLoan = list_userinfo[14].find(class_='icon-check-checked').next_sibling
    
    
    buffer_personal = [company, incomeRange, age, companyScale, house, education, position, houseLoan, school, city, car, marriage, workTime, carLoan]
    print buffer_personal
    
    buffer1 = [loanId, title, userId, borrowType, amount, interest, months]
    print(buffer1)
        
    return True
    