#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = "Wang Miaofei"

import urllib, urllib2, cookielib
import sys, string, time, os, re, json
import csv
from bs4 import BeautifulSoup
import socket

configfileName = 'config'
filedirectory = u'D:\\datas\\pythondatas\\my089\\'

#For login
urlLogin = u'https://member.my089.com/safe/login.aspx'
urlIndex = u'https://member.my089.com/safe/'
urlLenderRecordsPrefix = u'http://www.renrendai.com/lend/getborrowerandlenderinfo.action?id=lenderRecords&loanId='
urlRepayDetailPrefix = u'http://www.renrendai.com/lend/getborrowerandlenderinfo.action?id=repayDetail&loanId='
urlLenderInfoPrefix = u'http://www.renrendai.com/lend/getborrowerandlenderinfo.action?id=lenderInfo&loanId='
urlTransferLogPrefix = u'http://www.renrendai.com/transfer/transactionList.action?loanId='
username = u'victor1991'
password = u'73f7d9af739c494a455418da7a2efcce'
#password = u'wmf123456'
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36', 'Host':'www.my089.com'}

usePattern = re.compile(u'((/Loan/)?Detail\.aspx\?sid=(\d|-)+)|(/Loan/Succeed.aspx)|(/ConsumerInfo1\.aspx\?uid=(\d|\w)+)')

#--------------------------------------------------
#读取配置文件，返回目标文件夹地址
def getConfig():
    global filedirectory, username, password
    try:
        configfile = open(os.getcwd()+'/'+configfileName, 'r')
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
    
    createFolder(filedirectory)
    
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

    data = {'txtUid':username, 'MD5Pwd':password, 'txtPwd1':'', 'SaveMinits':'10080', 'btnLogin':u'立即登录'}
    postdata = urllib.urlencode(data)

    try:
        req = urllib2.Request(urlLogin, postdata, headers)
        result = urllib2.urlopen(req)
        if urlIndex != result.geturl(): #通过返回url判断是否登录成功
            print result.geturl()
            print(u'[FAIL]Wrong USERNAME or PASSWORD. Please try again!')
            return False
        result.close()

        req2 = urllib2.Request(urlIndex, headers=headers)
        result2 = urllib2.urlopen(req2)
        #print result2.read()
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
#分析页面内链接
def findUrl(webcontent):
    soup = BeautifulSoup(webcontent)
    list_a = soup.find_all('a')
    for item_a in list_a:
        #print item_a
        if item_a.has_attr('href'):#是否含有链接信息
            href = item_a['href']
            if usePattern.match(href):#是否有用
                if re.match('Detail.*', href):
                    href = '/Loan/'+href
                    #print href
                yield href
    
#end def findUrl

#--------------------------------------------------
#从url读取页面内容
def readFromUrl(url):
    try:
        req = urllib2.Request(url, headers = headers)
        response = urllib2.urlopen(req)
        m = response.read()
        response.close()
        return m
    except (urllib2.URLError) as e:
        if hasattr(e, 'code'):
            print('ERROR:'+str(e.code)+' '+str(e.reason))
            return None

#end def readFromUrl

#--------------------------------------------------
def analyzeData(webcontent, csvwriter):
    soup = BeautifulSoup(webcontent)
    
    tag_uid = soup.find('span', text = re.compile(u'用 户 名：'))
    print 'tag_uid='+str(tag_uid)
    href_uid = tag_uid.find_next_sibling('span').a['href']
    uid = re.search('/ConsumerInfo1\.aspx\?uid=((\d|\w)+)', href_uid).group(0)
    #print uid
    yield uid
    
    '''
    if soup.find('img', {'alt':'404'}):
        return False #页面404
    
    ### 分析script ###
    jsonString = soup.find(id = 'credit-info-data').string
    #jsonString = jsonString.replace('"[', '[').replace(']"', ']') #多余引号导致分析错误
    scriptData = json.loads(jsonString)
    
    ###本次借款基本信息###
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
    
    buffer1 = [loanId, title, userId, borrowType, amount, interest, months]
    print(buffer1)
    
    ###审核信息###
    creditInfo = scriptData['data']['creditInfo']
    
    ###审核通过时间###
    #"creditPassedTime":{"creditPassedTimeId":77028,"user":77078,"credit":"Dec 26, 2011 12:58:55 PM","work":"Dec 19, 2011 2:47:29 PM","incomeDuty":"Dec 22, 2011 1:34:36 PM","identificationScanning":"Dec 17, 2011 1:43:35 PM","marriage":"Dec 19, 2011 9:55:20 AM"}
    creditPassedTime = scriptData['data']['creditPassedTime']
    #信用报告，工作认证，收入认证，身份认证，婚姻认证
    list_passedTime = {'credit':'', 'work':'', 'incomeDuty':'', 'identificationScanning':'', 'marriage':''}
    for item in creditPassedTime.keys():
        list_passedTime[item] = creditPassedTime[item]
    print list_passedTime
    
    
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
    
    userinfo = [company, incomeRange, age, companyScale, house, education, position, houseLoan, school, city, car, marriage, workTime, carLoan]
    #print buffer_personal
    #csvwriter.writerow(buffer_personal)
    
    ###信用档案###
    tag_creditRecord = soup.find('div', class_='ui-tab-content-expediente') 
    list_creditRecord = tag_creditRecord.find('ul').find_all('li')
    loanTimes = list_creditRecord[0].find(class_='tab-list-value').string #申请借款（笔）
    creditLine = list_creditRecord[1].find(class_='tab-list-value').string #信用额度
    overdueAmount = list_creditRecord[2].find(class_='tab-list-value').string #逾期金额
    loanSuccessTimes = list_creditRecord[3].find(class_='tab-list-value').string #成功借款
    loanTotalAmount = list_creditRecord[4].find(class_='tab-list-value').string #借款总额
    overdueTimes = list_creditRecord[5].find(class_='tab-list-value').string #逾期次数
    payoffTimes = list_creditRecord[6].find(class_='tab-list-value').string #还清笔数
    torepayAmount = list_creditRecord[7].find(class_='tab-list-value').string #待还本息
    seriousOverdueTimes = list_creditRecord[8].find(class_='tab-list-value').string #严重逾期
    creditRecord = [loanTimes, loanSuccessTimes, payoffTimes, creditLine, loanTotalAmount, torepayAmount, overdueAmount, overdueTimes, seriousOverdueTimes]
    print(creditRecord)
    
    
    #-----------------------------------------------------
    ###js获得投标记录###
    req_lenderRecords = urllib2.Request(urlLenderRecordsPrefix+str(loanId), headers=headers)
    #while:
    print('[LENDER RECORDS]')
    try:
        response_lenderRecords = urllib2.urlopen(req_lenderRecords)
        lenderRecordsString = response_lenderRecords.read()
        lenderRecords = json.loads(lenderRecordsString)
        list_lenderRecords = lenderRecords['data']['lenderRecords']
        #print list_lenderInfo
        for item in list_lenderRecords:
            buffer_lenderRecords = [item['loanId'], item['userId'], item['userNickName'], item['amount'], item['lendTime']]
            print buffer_lenderRecords
    except (urllib2.URLError) as e:
        if hasattr(e, 'code'):
            print(str(e.code)+': '+str(e.reason))
        else:
            print(e.reason)
    except socket.error as e:
        print('ERROR] Socket error: '+str(e.errno))    
    
    #-----------------------------------------------------
    ###js获得还款表现###
    req_repayDetail = urllib2.Request(urlRepayDetailPrefix+str(loanId), headers=headers)
    try:
        response_repayDetail = urllib2.urlopen(req_repayDetail)
        repayDetailString = response_repayDetail.read()
        repayDetail = json.loads(repayDetailString)
        
        totalunRepaid = repayDetail['data']['unRepaid']
        totalRepaid = repayDetail['data']['repaid']
        list_repayDetail = repayDetail['data']['phases']
        for item in list_repayDetail:
            buffer_repayDetail = [item['repayTime'], item['status'], item['unRepaidAmount'], item['unRepaidFee'], item['actualRepayTime']]
            print buffer_repayDetail
        
    except (urllib2.URLError) as e:
        if hasattr(e, 'code'):
            print(str(e.code)+': '+str(e.reason))
        else:
            print(e.reason)
    except socket.error as e:
        print('ERROR] Socket error: '+str(e.errno))
        i = lastpage 
    #-----------------------------------------------------
    ###js获得债权信息###
    req_lenderInfo = urllib2.Request(urlLenderInfoPrefix+str(loanId), headers=headers)
    #while:
    try:
        response_lenderInfo = urllib2.urlopen(req_lenderInfo)
        lenderInfoString = response_lenderInfo.read()
        lenderInfo = json.loads(lenderInfoString)
        list_lenderInfo = lenderInfo['data']['lenders']
        #print list_lenderInfo
        for item in list_lenderInfo:
            buffer_lenderInfo = [loanId, item['userId'], item['nickName'], item['leftAmount'], item['lendTime'], item['share']]
            print buffer_lenderInfo
    except (urllib2.URLError) as e:
        if hasattr(e, 'code'):
            print(str(e.code)+': '+str(e.reason))
        else:
            print(e.reason)
    except socket.error as e:
        print('ERROR] Socket error: '+str(e.errno))
    
    #-----------------------------------------------------
    ###js获得债券转让记录###
    req_transferLog = urllib2.Request(urlTransferLogPrefix+str(loanId), headers=headers)
    try:
        response_transferLog = urllib2.urlopen(req_transferLog)
        transferLogString = response_transferLog.read()
        transferLog = json.loads(transferLogString)
        
        transferAccount = transferLog['data']['account']
        transferNoAccount = transferLog['data']['noAccount']
        list_transferLog = transferLog['data']['loanTransferLogList']
        print('[TRANSFER LOG]')
        for item in list_transferLog:
            buffer_transferLog = [item['fromNickName'], item['fromUserId'], item['toNickName'], item['toUserId'], item['price'], item['share'], item['createTime']]
            print buffer_transferLog
    except (urllib2.URLError) as e:
        if hasattr(e, 'code'):
            print(str(e.code)+': '+str(e.reason))
        else:
            print(e.reason)
    except socket.error as e:
        print('ERROR] Socket error: '+str(e.errno))
        i = lastpage 
    
    return True
    '''
