#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = "Wang Miaofei"

import urllib, urllib2, cookielib
import sys, string, time, os, re, json
import csv
from bs4 import BeautifulSoup
import socket, ssl
from random import randint

configfileName = 'config'
filedirectory = u'D:/datas/pythondatas/renrendai/'

#For login
urlLogin = u'https://www.renrendai.com/j_spring_security_check'
urlIndex = u'http://www.renrendai.com/'
urlLenderRecordsPrefix = u'http://www.renrendai.com/lend/getborrowerandlenderinfo.action?id=lenderRecords&loanId='
urlRepayDetailPrefix = u'http://www.renrendai.com/lend/getborrowerandlenderinfo.action?id=repayDetail&loanId='
urlLenderInfoPrefix = u'http://www.renrendai.com/lend/getborrowerandlenderinfo.action?id=lenderInfo&loanId='
urlTransferLogPrefix = u'http://www.renrendai.com/transfer/transactionList.action?loanId='
urlUserPrefix = 'https://www.renrendai.com/account/myInfo.action?userId='
urlCommentPrefix = 'http://www.renrendai.com/lend/loanCommentList.action?loanId='
urlCollectionPrefix = 'http://www.renrendai.com/lend/dunDetail.action?loanId='

#for Financial Plan
urlFPLenderPrefix = 'http://www.renrendai.com/financeplan/getFinancePlanLenders.action?financePlanStr='
urlFPPerformancePrefix = 'http://www.renrendai.com/financeplan/listPlan!planResults.action?financePlanId='
username = u'15120000823'
password = u'wmf123456'

ipAddress = ['191.124.5.2', '178.98.24.45, 231.67.9.28']
host = 'www.renrendai.com'
userAgent = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36']
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36', 'Host':'www.renrendai.com'}

TRY_LOGIN_TIMES = 5 
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
    print('Logging in...')
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

    data = {'j_username':username, 'j_password':password, 'rememberme':'on', 'targetUrl':'http://www.renrendai.com', 'returnUrl':''}
    postdata = urllib.urlencode(data)
    for i in range(TRY_LOGIN_TIMES):
        try:
            req = urllib2.Request(urlLogin, postdata, getRandomHeaders())
            result = urllib2.urlopen(req)
            '''
            if urlIndex != result.geturl(): #通过返回url判断是否登录成功
                print result.geturl()
                print(u'[FAIL]Wrong USERNAME or PASSWORD. Please try again!')
                return False
            '''
            result.close()
            print('LOGIN SUCCESS')
            return True
        except:
            print(u'[FAIL]Login failed. Please try again!')
    #end for
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
#生成一个随机的headers
def getRandomHeaders():
    ipNumber = len(ipAddress)
    agentNumber = len(userAgent)
    headers = {'User-Agent': userAgent[randint(0, agentNumber-1)], 'Host': host, 'X-Forwarded-For': ipAddress[randint(0, ipNumber-1)]}
    return headers

#--------------------------------------------------
def getTime(format = None):
    if format:
        strtime = str(time.strftime(format, time.localtime(time.time())))
    else:
        strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    return strtime
#--------------------------------------------------
def cleanString(str):
    str = str.replace('\r\n', ' ')
    str = str.replace('\n', ' ')
    return str.strip()
#--------------------------------------------------
#从url读取页面内容
def readFromUrl(url, formdata = None):
    
    loopCount = 0
    while True:
        loopCount += 1
        if loopCount > 5:
            break
        try:
            response = responseFromUrl(url, formdata)
            if response:
                m = response.read()
                #response.close()
                return m
            else:
                print('response is None')
                return None
        except ssl.SSLError, e:
            print('[ERROR]ssl error in readFromUrl()!')
            if hasattr(e, 'code'):
                print e.code
            print e.errno
            login()
            continue
        except Exception, e:
            print('i do not know what is wrong. When readFromUrl()!')
            if hasattr(e, 'code'):
                print "Error Msg: "+e.code
            print e.errno
            continue
        
#end def readFromUrl
#--------------------------------------------------
#从url读取response
def responseFromUrl(url, formdata = None):
    response = None
    if formdata != None:
        formdata = urllib.urlencode(formdata)

    loopCount = 0
    #proxyNumber = len(proxyList)
    while True:
        loopCount += 1
        if loopCount > 5:
            print('Failed when trying responseFromUrl().')
            print('URL = '+url)
            break
        try:
            req = urllib2.Request(url, formdata, headers=getRandomHeaders())
            #proxyNo = randint(0, proxyNumber-1)
            #req.set_proxy(proxyList[proxyNo], 'http')
            response = urllib2.urlopen(req)
            curUrl = response.geturl()
            break
        except (urllib2.URLError) as e:
            if hasattr(e, 'code'):
                print('ERROR:'+str(e.code)+' '+str(e.reason))
                if(e.code == 404):
                    print('url = '+url)
                    return None
            else:
                print(str(e.reason))
            print('url = '+url)
        except httplib.IncompleteRead, e:
            print('[ERROR]IncompleteRead! '+url)
            continue
        except ssl.SSLError, e:
            print('[ERROR]ssl error!')
            continue
        except:
            print('some error: '+url)
            login()
            continue
            
        if(response == None):
            print('responseFromUrl get a None')
            time.sleep(1)
            login()
            continue
    #end while
    
    return response
#--------------------------------------------------
def analyzeData(webcontent, writers):
    soup = BeautifulSoup(webcontent)
    
    if soup.find('src', {'alt':'/exceptions/network-busy/img/404.png'}):
        return False #页面404
    
    currentDate = getTime('%Y-%m-%d')
    currentClock = getTime('%H:%M:%S')
    
    ### 分析script ###
    jsonString = soup.find(id = 'credit-info-data').get_text()
    if jsonString == None:
        print('Cannot get json')
        return True
    #jsonString = jsonString.replace('"[', '[').replace(']"', ']') #多余引号导致分析错误
    #print jsonString
    scriptData = json.loads(jsonString)
    
    ###本次借款基本信息###
    loanData = scriptData['data']['loan']
    loanId = loanData['loanId']
    tag_loanType = loanData['displayLoanType']
    if tag_loanType == 'SDRZ':
        loanType = '实'
    elif tag_loanType == 'XYRZ':
        loanType = '信'
    elif tag_loanType == 'JGDB':
        loanType = '保'
    else:
        loanType = tag_loanType
    tag_guarantor = loanData['utmSource']
    if tag_guarantor == 'debx-zdsd':
        guarantor = '证大速券'
    elif tag_guarantor == 'debx-yx':
        guarantor = '友众信业'
    elif tag_guarantor == 'debx-zaxy':
        guarantor = '中安信业'
    elif tag_guarantor == 'from-website':
        guarantor = ''
    else:
        guarantor = tag_guarantor
    title = loanData['title']
    borrowType = loanData['borrowType']
    amount = loanData['amount']
    interest = loanData['interest']
    months = loanData['months']
    statusType = loanData['status']
    userId = loanData['borrowerId']
    username = loanData['nickName']
    borrowerLevel = loanData['borrowerLevel']
    leftMonths = loanData['leftMonths'] #剩余期数（月）
    finishedRatio = loanData['finishedRatio'] #完成额度
    description = loanData['description']
    jobType = loanData['jobType']
    
    status = ''
    if statusType == 'IN_PROGRESS':
        status = '还款中'
    elif statusType == 'FIRST_READY':
        status = '已满标'
    elif statusType == 'FIRST_APPLY':
        status = '申请中'
    elif statusType == 'FAILED':
        status = '已流标'
    elif statusType == 'BAD_DEBT':
        status = '已垫付'
    elif statusType == 'CLOSED':
        status = '已还清'
    else:
        status = statusType
    buffer1 = [currentDate, currentClock, loanId, loanType, guarantor, title, amount, interest, months, status]
    #print(buffer1)

    #soup = soup.find('body') #只从body中提取数据，出现了莫名截断的问题 TODO
    #print soup
    
    guaranteeType = repayTyep = ''
    prepaymentRate = repayEachMonth = '0'
    #保障方式
    tag_guaranteeType = soup.find('span', text = u'保障方式')
    if tag_guaranteeType:
        guaranteeType = tag_guaranteeType.find_next_sibling('span').contents[0]
        #print guaranteeType
    #还款方式
    tag_repayType = soup.find('span', text=u'还款方式')
    if tag_repayType:
        repayType = tag_repayType.find_next_sibling('span').contents[0]
        #print repayType
    #提前还款费率
    tag_prepaymentRate = soup.find('span', text=u'提前还款费率')
    if tag_prepaymentRate:
        prepaymentRate = tag_prepaymentRate.find_next_sibling('span').find('em').string
        #print prepaymentRate
    #月还本息    
    tag_repayEachMonth = soup.find('span', text=u'月还本息（元）')
    if tag_repayEachMonth:
        repayEachMonth = tag_repayEachMonth.find_next_sibling('span').find('em').string
        repayEachMonth = repayEachMonth.replace(',', '')
        #print repayEachMonth
    #待还本息
    amountToRepay = 0
    tag_amountToRepay = soup.find('em', text=re.compile(u'待还本息\w*'))
    if tag_amountToRepay:
        amountToRepay = tag_amountToRepay.find_next_sibling('span').string.replace(',', '')
        amountToRepay = re.search(r'\d+', amountToRepay).group()
    #print amountToRepay
    #满标用时
    fullTime = ''
    tag_fullTime = soup.find('span', {'id':'fullTime'})
    if tag_fullTime:
        fullTime = tag_fullTime['data-time']
    buffer1.extend([guaranteeType, prepaymentRate, repayType, repayEachMonth, finishedRatio, fullTime])
    
    ###用户个人信息###
    tag_userinfo = soup.find('div', class_='ui-tab-content-basic')
    list_userinfo = tag_userinfo.find('ul').find_all('li')
    #print list_userinfo
    sex = list_userinfo[0].find('em', class_='mt5')['title']
    company = list_userinfo[1].find(class_='tab-list-value').string
    if company == '--': company = ''
    incomeRange = list_userinfo[2].find(class_='tab-list-value').string
    if incomeRange == '--': incomeRange = ''
    age = list_userinfo[3].find(class_='tab-list-value').string
    companyScale = list_userinfo[4].find(class_='tab-list-value').string
    if companyScale == '--': companyScale = ''
    house = list_userinfo[5].find(class_='icon-check-checked').next_sibling
    education = list_userinfo[6].find(class_='tab-list-value').string
    if education=='--': education=''
    position = list_userinfo[7].find(class_='tab-list-value').string
    if position == '--': position = ''
    houseLoan = list_userinfo[8].find(class_='icon-check-checked').next_sibling
    school = list_userinfo[9].find(id='university')['title']
    city = list_userinfo[10].find(class_='tab-list-value').string
    if city.find(u'请选择')>0 or city.find('--')>0: city = ''
    tag_car = list_userinfo[11].find(class_='icon-check-checked')
    if tag_car:
        car = tag_car.next_sibling
    else:
        car = list_userinfo[11].find('em')['title']
    marriage =list_userinfo[12].find(class_='tab-list-value').string
    workTime = list_userinfo[13].find(class_='tab-list-value').string
    if workTime=='--': workTime = ''
    carLoan = list_userinfo[14].find(class_='icon-check-checked').next_sibling
    
    userinfo = [userId, username, sex, age, education, school, marriage, company, companyScale, position, city, workTime, incomeRange, house, houseLoan, car, carLoan, jobType]
    buffer1.extend(userinfo)
    
    ###信用档案###
    tag_creditRecord = soup.find('div', class_='ui-tab-content-expediente')
    creditRank = tag_creditRecord.h4.span.get_text()
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
    creditRecord = [creditRank, loanTimes, loanSuccessTimes, payoffTimes, creditLine, loanTotalAmount, torepayAmount, overdueAmount, overdueTimes, seriousOverdueTimes]
    buffer1.extend(creditRecord)

    ###审核信息###
    list_renzheng = ['credit', 'identificationScanning', 'work', 'incomeDuty', 'house', 'car', 'marriage', 'graduation', 'fieldAudit', 'mobileReceipt', 'kaixin', 'residence', 'video']
    #"creditInfo":{"creditInfoId":490655,"user":495364,"identificationScanning":"VALID","mobile":"INVALID","graduation":"INVALID","credit":"OVERDUE","residence":"INVALID","marriage":"INVALID","child":"INVALID","album":"INVALID","work":"OVERDUE","renren":"INVALID","kaixin":"INVALID","house":"INVALID","car":"INVALID","identification":"VALID","detailInformation":"INVALID","borrowStudy":"VALID","mobileReceipt":"INVALID","incomeDuty":"OVERDUE","other":"INVALID","account":"INVALID","titles":"INVALID","fieldAudit":"INVALID","mobileAuth":"INVALID","video":"INVALID","version":1}
    creditInfo = scriptData['data']['creditInfo']
    list_creditInfo = {'credit':'0', 'identificationScanning':'0', 'work':'0', 'incomeDuty':'0', 'house':'0', 'car':'0', 'marriage':'0', 'graduation':'0', 'fieldAudit':'0', 'mobileReceipt':'0', 'kaixin':'0', 'residence':'0', 'video':'0'}
    #kaixin为微博，技术职称认证不详暂为fieldAudit
    for item in creditInfo.keys():
        if(creditInfo[item] == 'VALID'):
            list_creditInfo[item] = '1'
    ###审核通过时间###
    #"creditPassedTime":{"creditPassedTimeId":77028,"user":77078,"credit":"Dec 26, 2011 12:58:55 PM","work":"Dec 19, 2011 2:47:29 PM","incomeDuty":"Dec 22, 2011 1:34:36 PM","identificationScanning":"Dec 17, 2011 1:43:35 PM","marriage":"Dec 19, 2011 9:55:20 AM"}
    creditPassedTime = scriptData['data']['creditPassedTime']
    #信用报告，工作认证，收入认证，身份认证，婚姻认证
    list_passedTime = {'credit':'', 'identificationScanning':'', 'work':'', 'incomeDuty':'', 'house':'', 'car':'', 'marriage':'', 'graduation':'', 'fieldAudit':'', 'mobileReceipt':'', 'kaixin':'', 'residence':'', 'video':''}
    for item in creditPassedTime.keys():
        try:
            passedTime = time.strptime(creditPassedTime[item],'%b %d, %Y %I:%M:%S %p')
            list_passedTime[item] = time.strftime('%Y-%m-%d', passedTime)
        except:
            continue
    data_renzheng = []
    for i in range(0, len(list_renzheng)):
        itemName = list_renzheng[i]
        data_renzheng.append(list_creditInfo[itemName])
        data_renzheng.append(list_passedTime[itemName])
        #print list_renzheng[i]+': '+list_creditInfo[list_renzheng[i]]+' '+list_passedTime[list_renzheng[i]]
    buffer1.extend(data_renzheng)
    buffer1.append(description)
    
    writers[0].writerow(buffer1)
    
    basicInfo = [currentDate, currentClock]
    #投标记录-----------------------------------------
    analyzeLenderData(loanId, writers[1], basicInfo)
    
    #还款表现-----------------------------------------
    analyzeRepayData(loanId, writers[2], basicInfo)
    
    #催收信息-----------------------------------------
    analyzeCollectionData(loanId, writers[7], basicInfo)
    
    #债权信息-----------------------------------------
    analyzeLenderInfoData(loanId, writers[3], basicInfo)
    
    #债券转让记录-------------------------------------
    analyzeTransferData(loanId, writers[4], basicInfo)
    
    #用户信息---------------------------------------
    analyzeUserData(userId, writers[5], [loanTimes, loanSuccessTimes, payoffTimes, overdueTimes, overdueAmount, seriousOverdueTimes])
    
    #评论信息---------------------------------
    print('  Get Comments...')
    commentPage = 0
    while True:
        commentPage += 1
        if(commentPage > 1):
            commentsString = readFromUrl(urlCommentPrefix+str(loanId)+'&pageIndex='+str(commentPage))
            #print commentsString
            if(len(commentsString) == 0):
                break
        else:
            commentsString = soup.find('script', {'id':'comments-data'}).get_text()
        commentsJson = json.loads(commentsString)
        list_comments = commentsJson['data']['loanComments']
        for item in list_comments:
            m1 = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['commentTime'])
            if m1:
                commentDate = m1.group(1)
                commentClock = m1.group(2)
            else:
                commentFullTime = time.strptime(item['commentTime'],'%b %d, %Y %I:%M:%S %p')
                commentDate = time.strftime('%Y-%m-%d', commentFullTime)
                commentClock = time.strftime('%H:%M:%S', commentFullTime)
            comment = [currentDate, currentClock]
            comment.extend([item['toLoanId'], item['byUserId'], item['displayName'], commentDate,commentClock, item['content']])
            if 'repliedComments' in item:
                if item['repliedComments'] != None:
                    reply = item['repliedComments'][0]
                    m2 = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', reply['commentTime'])
                    if m2:
                        replyDate = m2.group(1)
                        replyClock = m2.group(2)
                    else:
                        replyFullTime = time.strptime(reply['commentTime'],'%b %d, %Y %I:%M:%S %p')
                        replyDate = time.strftime('%Y-%m-%d', replyFullTime)
                        replyClock = time.strftime('%H:%M:%S', replyFullTime)
                    replyUserId = reply['byUserId']
                    replyContent = reply['content']
                    comment.extend([reply['byUserId'], reply['displayName'], replyDate, replyClock, reply['content']])
            
            writers[6].writerow(comment)
        if(len(list_comments) < 10):
            break
    
    return True
    
#---------------------------------------------
def analyzeLenderData(loanId, writer, attrs):
    ###js获得投标记录###
    print('  Get Lender Records...')
    lenderRecordsString = readFromUrl(urlLenderRecordsPrefix+str(loanId))
    lenderRecords = json.loads(lenderRecordsString)
    list_lenderRecords = lenderRecords['data']['lenderRecords']
    #print list_lenderInfo
    for item in list_lenderRecords:
        m = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['lendTime'])
        lendDate = m.group(1)
        lendClock = m.group(2)
        isFinancePlan = '0' #理财计划
        financePlanId = '' #理财计划期数
        if(item['lenderType'] == 'FINANCEPLAN_BID'):
            isFinancePlan = '1'
            financePlanId = item['financePlanId']
        
        buffer_lenderRecords = []
        buffer_lenderRecords.extend(attrs)
        buffer_lenderRecords.extend([item['loanId'], item['userId'], item['userNickName'], item['amount'], lendDate, lendClock, isFinancePlan, financePlanId])
        #print buffer_lenderRecords
        writer.writerow(buffer_lenderRecords)
#end def analyzeLenderData
#-------------------------------------------------
def analyzeRepayData(loanId, writer, attrs):
    print('  Get Repay Log...')
    repayDetailString = readFromUrl(urlRepayDetailPrefix+str(loanId))
    repayDetail = json.loads(repayDetailString)
    
    totalunRepaid = repayDetail['data']['unRepaid']
    totalRepaid = repayDetail['data']['repaid']
    list_repayDetail = repayDetail['data']['phases']
    for item in list_repayDetail:
        repayTime = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['repayTime']).group(1)
        if item['actualRepayTime']:
            actualRepayTime = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['actualRepayTime']).group(1)
        else:
            actualRepayTime = ''
        buffer_repayDetail = []
        buffer_repayDetail.extend(attrs)
        buffer_repayDetail.extend([loanId, repayTime, item['repayType'], item['unRepaidAmount'], item['unRepaidFee'], actualRepayTime])
        writer.writerow(buffer_repayDetail)
    
#end def analyzeRepayData
#-------------------------------------------------
def analyzeCollectionData(loanId, writer, attrs):
    print('  Get Collection Log...')
    collectionString = readFromUrl(urlCollectionPrefix+str(loanId));
    collectionInfo = json.loads(collectionString)
    list_collection = collectionInfo['data']['dunInfoList']
    for item in list_collection:
        time = ''
        if item['dunTime']:
            time = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['dunTime']).group(1)
        elif item['createTime']:
            time = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['createTime']).group(1)
        buffer_collection = []
        buffer_collection.extend(attrs)
        buffer_collection.extend([loanId, time, item['contact'], item['description']])
        writer.writerow(buffer_collection)
#end def analyzeCollectionData()
#---------------------------------------------------
def analyzeLenderInfoData(loanId, writer, attrs):
    ###js获得债权信息###
    print('  Get Lender Infomation...')
    lenderInfoString = readFromUrl(urlLenderInfoPrefix+str(loanId))
    lenderInfo = json.loads(lenderInfoString)
    list_lenderInfo = lenderInfo['data']['lenders']
    #print list_lenderInfo
    for item in list_lenderInfo:
        isFinancePlan = '0' #理财计划
        financePlanId = '' #理财计划期数
        #print item['financePlanId']
        if(item['financePlanId'] != None):
            isFinancePlan = '1'
            financePlanId = item['financePlanId']
        buffer_lenderInfo = []
        buffer_lenderInfo.extend(attrs)
        buffer_lenderInfo.extend([loanId, item['userId'], item['nickName'], item['leftAmount'], item['share'], isFinancePlan, financePlanId])
        writer.writerow(buffer_lenderInfo)
#end def analyzeLenderInfoData()

#---------------------------------------------------
def analyzeTransferData(loanId, writer, attrs):
###js获得债券转让记录###
    print('  Get Transfer Log...')
    transferLogString = readFromUrl(urlTransferLogPrefix+str(loanId))
    transferLog = json.loads(transferLogString)
    
    transferAccount = transferLog['data']['account']
    transferNoAccount = transferLog['data']['noAccount']
    list_transferLog = transferLog['data']['loanTransferLogList']
    for item in list_transferLog:
        m = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['createTime'])
        transferDate = m.group(1)
        transferClock = m.group(2)
        buffer_transferLog = []
        buffer_transferLog.extend(attrs)
        buffer_transferLog.extend([loanId, item['toUserId'], item['toNickName'], item['fromUserId'], item['fromNickName'], item['price'], item['share'], transferDate, transferClock])
        writer.writerow(buffer_transferLog)
#end def analyzeTransferData()
#-------------------------------------------------------
def analyzeUserData(userId, writer, attrs):
    print('  Get User Info...')
    content_user = readFromUrl(urlUserPrefix+str(userId))
    soup = BeautifulSoup(content_user)
    currentDate = getTime('%Y-%m-%d')
    currentClock = getTime('%H:%M:%S')
    #个人信息
    nickName = soup.find('span', {'id':'nick-name'}).string
    tag_registerDate = soup.find('div', class_='avatar-info')
    if tag_registerDate:
        registerDate = re.search('\d+-\d+-\d+', tag_registerDate.find('p').string).group(0)
    #理财统计
    ownInfo = soup.find('div', class_='avatar-invest')
    tag_ownBondsCount = ownInfo.dl.find('dd')
    ownBondsCount = tag_ownBondsCount.find('em').string
    tag_ownFinancePlansCount = tag_ownBondsCount.find_next('dd')
    ownFinancePlansCount = tag_ownFinancePlansCount.find('em').string
    
    
    buffer_user = [currentDate, currentClock, userId, nickName, registerDate, ownBondsCount, ownFinancePlansCount]
    buffer_user.extend(attrs)
    writer.writerow(buffer_user)
#end analyzeUserData()

#------------------------------------------------------
def analyzeFPData(webcontent, planId, writers):
    soup = BeautifulSoup(webcontent)
    currentDate = getTime('%Y-%m-%d')
    currentClock = getTime('%H:%M:%S')
    tag_basic = soup.find('div', class_='basic-box')
    if tag_basic == None:
        return False
    list_basicInfo = tag_basic.ul.find_all('li', class_='fn-clear')
    
    planAmount = list_basicInfo[0].find('span', class_='num').em.get_text()
    expectedRate = list_basicInfo[0].find('span', {'id':'expected-rate'})['data-value']
    planProducts = list_basicInfo[1].find('span', {'id':'plan-basic-products'})['data-products']
    guaranteeMode = list_basicInfo[1].find('span', class_='last').get_text()
    status = list_basicInfo[2].find('span', class_='basic-value').get_text()
    fullTime = list_basicInfo[2].find('span', class_='last').get_text()
    lockPeriod = list_basicInfo[3].find('em', class_='value').get_text()
    lockDate = list_basicInfo[3].find('span', class_='last').get_text()
    #print list_basicInfo[4]
    buyInRate = list_basicInfo[5].find('div', {'id':'buy-in-rate'})['data-br']
    interestRate = list_basicInfo[5].find('div', {'id':'interest-rate'})['data-ir']
    quitRate = list_basicInfo[5].find('div', {'id':'quit-rate'})['data-qr']
    
    leftAmount = soup.find('em', {'id':'max-amount-1'})['data-amount']
    joinAmountLimit = soup.find('em', {'id':'max-amount-2'})['data-amount']
    
    buffer_FP = [currentDate, currentClock, planId, planAmount, expectedRate, planProducts, guaranteeMode, status, fullTime, lockPeriod, lockDate, buyInRate, interestRate, quitRate, leftAmount, joinAmountLimit]
    #print buffer_FP
    
    #分析加入记录
    joinLenderCount = analyzeFPLender(planId, writers[1])
    
    #分析理财计划表现
    performance = analyzePlan(planId)
    
    buffer_FP.append(joinLenderCount)
    buffer_FP.extend(performance)
    writers[0].writerow(buffer_FP)
    return True
#end def analyzeFPData()
#--------------------------------------------------------
#加入记录, 返回总人数
def analyzeFPLender(planId, writer):
    print('  Get Lender Info...')
    content_lender = readFromUrl(urlFPLenderPrefix+str(planId))
    lenderInfo = json.loads(content_lender)
    
    list_lenders = lenderInfo['data']['jsonList']
    #print len(list_lenders)
    for item in list_lenders:
        m = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['createTime'])
        aDate = m.group(1)
        aClock = m.group(2)
        buffer_lender = [planId]
        buffer_lender.extend([item['nickName'], item['userId'], item['amount'], aDate, aClock])
        writer.writerow(buffer_lender)
    return len(list_lenders)
#end def analyzeFPLender()
#----------------------------------------------------
#
def analyzePlan(planId):
    print('  Get Performace...')
    content_plan = readFromUrl(urlFPPerformancePrefix+str(planId))
    planInfo = json.loads(content_plan)
    item = planInfo['data']['financePlanVos'][0]
    #print item
    buffer_performance = []
    buffer_performance.extend([item['bidCount'], item['averageBidInterest'], item['amount'], item['fundsUseRate'], item['earnInterest'], item['borrowCount']])
    #writer.writerow(buffer_performance)
    return buffer_performance
#end def analyzePlan()
