#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = "Wang Miaofei"

import urllib, urllib2, cookielib
import sys, string, time, os, re, json
import csv
from bs4 import BeautifulSoup
import socket
import hashlib

configfileName = 'config'
filedirectory = u'D:\\datas\\pythondatas\\kickstarter\\'

#For login
urlHost = u'https://www.kickstarter.com'
urlLogin = u'https://www.kickstarter.com/user_sessions'
urlIndex = u'https://www.kickstarter.com/'
urlCategory = u'https://www.kickstarter.com/discover/advanced?'

#for excel

username = u'victor1991@126.com'
password = u'wmf123456'
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36', 'Host':'www.kickstarter.com'}

TRY_LOGIN_TIMES = 5 #尝试登录次数

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
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

    #md5pwd = hashlib.md5(password).hexdigest();
    #print 'md5 password = '+md5pwd
    #md5pwd = '73f7d9af739c494a455418da7a2efcce'
    data = {'utf8':'%E2%9C%93', 'user_session[email]':username, 'user_session[password]':password, 'commit':'Log me in!', 'user_session[remember_me]':'0', 'user_session[remember_me]':'1'};
    postdata = urllib.urlencode(data)
    for i in range(TRY_LOGIN_TIMES):
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
            print("LOGIN SUCCESS!")
            return True #登录成功
        except:
            print(u'[FAIL]Login failed. Retrying...')
            #return False
    #end for
    print(u'[FAIL]login failed after retrying')
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
#从url读取response
def responseFromUrl(url, formdata = None):
    response = None
    if formdata != None:
        formdata = urllib.urlencode(formdata)

    loopCount = 0
    while True:
        loopCount += 1
        if loopCount > 5:
            print('Failed when trying responseFromUrl().')
            print('URL = '+url)
            break
        try:
            req = urllib2.Request(url, formdata, headers = headers)
            response = urllib2.urlopen(req)
            curUrl = response.geturl()
            break
        except (urllib2.URLError) as e:
            if hasattr(e, 'code'):
                print('ERROR:'+str(e.code)+' '+str(e.reason))
            print(str(e.reason))
            print('url = '+url)
            
        if(response == None):
            print('responseFromUrl get a None')
            time.sleep(1)
            login()
            continue
    #end while
    
    return response

#--------------------------------------------------
#从url读取页面内容
def readFromUrl(url, formdata = None):
    response = responseFromUrl(url, formdata)
    if response:
        m = response.read()
        response.close()
        return m
    else:
        return None
#end def readFromUrl

#--------------------------------------------------
def getTime(format = None):
    if format:
        strtime = str(time.strftime(format, time.localtime(time.time())))
    else:
        strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    return strtime

#--------------------------------------------------
def analyzeData(url, writers):
    webcontent = readFromUrl(url)
    soup = BeautifulSoup(webcontent)
    buffer1 = []
    #******************************
    #页面上栏部分
    currentDate = getTime('%Y-%m-%d')
    currentClock = getTime('%H:%M:%S')

    category = title = updates = backers = comments = location = ''

    tag_category = soup.find('li', class_='category')
    if tag_category:
        category = tag_category.a.get_text()
        category = category.strip()
        #print category
    tag_title = soup.find('meta', {'property':'og:title'})
    if tag_title:
        title = tag_title['content']
        title = title.replace(';', '.')
    tag_updates = soup.find('span', {'id':'updates_count'})
    if tag_updates:
        updates = tag_updates['data-updates-count']
    tag_backers = soup.find('meta', {'property':'twitter:text:backers'})
    if tag_backers:
        backers = tag_backers['content']
    tag_comments = soup.find('span', {'id':'comments_count'})
    if tag_comments:
        comments = tag_comments['data-comments-count']
    tag_location = soup.find('meta', {'property':'twitter:text:location'})
    if tag_location:
        location = tag_location['content']
    attrs1 = [url, currentDate, currentClock, category, title, updates, backers, comments, location]
    #******************************
    #页面左侧部分
    video = desLength = desPics = riskLength = FAQQ = FAQA = '0'
    tag_video = soup.find('div', {'id':'video-section'})
    if tag_video and tag_video['data-has-video']=='true':
        video = '1'
    tag_description = soup.find('div', {'class':'full-description'})
    if tag_description:
        desLength = str(len(tag_description.get_text()))
        desPics = str(len(tag_description.find_all('img')))
    tag_risk = soup.find('div', {'id':'risks'})
    if tag_risk:
        #print tag_risk.get_text()
        riskLength = str(len(tag_risk.get_text()))
    tag_FAQ = soup.find('div', {'id':'project-faqs'})
    if tag_FAQ:
        FAQQ = str(len(tag_FAQ.find_all('div', {'class':'faq-question'})))
        FAQA = str(len(tag_FAQ.find_all('div', {'class':'faq-answer'})))
    attrs2 = [video, desLength, desPics, riskLength, FAQQ, FAQA]

    #******************************
    #页面右栏上方
    moneyUnit = backers = pledgedAmount = goal = daysToGo = '0'
    tag_pledged = soup.find('div', {'id':'pledged'})
    if tag_pledged:
        goal = tag_pledged['data-goal']
        pledgedAmount = tag_pledged['data-pledged']
        tag_amount = tag_pledged.find('data')
        if tag_amount:
            moneyUnit = tag_amount['data-currency']
    tag_backers = soup.find('meta', {'property':'twitter:text:backers'})
    if tag_backers:
        backers = tag_backers['content']
    tag_days = soup.find('meta', {'property':'twitter:text:time'})
    if tag_days:
        daysToGo = tag_days['content']
    attrs3 = [moneyUnit, backers, pledgedAmount, goal, daysToGo]
    #******************************
    #页面右栏最下端
    beginDate = endDate = spanDays = ''
    tag_period = soup.find('div', {'id':'meta'})
    if tag_period:
        time1 = tag_period.find('time')
        beginDate = re.match('(\d+-\d+-\d+)T.*', time1['datetime']).group(1)
        time2 = time1.find_next_sibling('time')
        endDate = re.match('(\d+-\d+-\d+)T.*', time2['datetime']).group(1)
    tag_duration = soup.find('span', {'id':'project_duration_data'})
    if tag_duration:
        spanDays = re.match('(\d+).\d?', tag_duration['data-duration']).group(1)
    attrs4 = [beginDate, endDate, spanDays]
    #******************************
    #页面右栏中部
    creatorName = creatorAdd = ''
    FB_friends = 'NA'
    tag_creator = soup.find('meta', {'property':'twitter:text:artist'})
    if tag_creator:
        creatorName = tag_creator['content']
    creatorAdd = location #TODO: is there any difference?
    tag_creatorFB = soup.find('li', {'class':'facebook-connected'})
    if tag_creatorFB:
        FB_friends = re.match('(\s|\n)*(\d+).*', tag_creatorFB.find('span', class_='number').string).group(2)
    attrs5 = [creatorName, creatorAdd, str(FB_friends)]
    
    #******************************
    #about creator
    creatorID = lastLoginDate = joinedDate = ''
    bioLength = NBacked = NCreated = '0'
    bioContent = readFromUrl(url+'/creator_bio.js')
    soup_bio = BeautifulSoup(bioContent)
    tag_lastLogin = soup_bio.find('time', class_='js-adjust')
    if tag_lastLogin:
        lastLoginDate = re.match('(\d+-\d+-\d+)T.*', tag_lastLogin['datetime']).group(1)

    tag_creatorUrl = soup.find('meta', {'property':'kickstarter:creator'})
    if tag_creatorUrl:
        creatorUrl = tag_creatorUrl['content']
        #print creatorUrl
        creatorID = re.match('https://www\.kickstarter\.com/profile/(\w+)', creatorUrl).group(1)
        creatorContent = readFromUrl(creatorUrl)
        soup2 = BeautifulSoup(creatorContent)
        tag_joined = soup2.find('meta', {'property':'kickstarter:joined'})
        if tag_joined:
            joinedDate = re.match('(\d+-\d+-\d+) .*', tag_joined['content']).group(1)
        tag_bio = soup2.find('meta', {'property':'og:description'})
        if tag_bio:
            bioLength = str(len(tag_bio['content']))
        tag_NBacked = soup2.find('a', {'id':'list_title'})
        if tag_NBacked:
            NBacked = re.search('\d+', tag_NBacked.get_text()).group(0)
            tag_NCreated = tag_NBacked.parent.find_next_sibling('li')
            #print tag_NCreated
            if tag_NCreated:
                NCreated = re.search('\d+', tag_NCreated.get_text()).group(0)
        attrs6 = [str(creatorID), bioLength, lastLoginDate, joinedDate, str(NBacked), str(NCreated)]
    
    #******************************
    buffer1.extend(attrs1)
    buffer1.extend(attrs2)
    buffer1.extend(attrs3)
    buffer1.extend(attrs4)
    buffer1.extend(attrs5)
    buffer1.extend(attrs6)

    #******************************
    #Reward
    tag_reward = soup.find('ul', {'id':'what-you-get'})
    if tag_reward:
        reward_list = tag_reward.find_all('li', class_='NS-projects-reward')
        for reward_item in reward_list:
            RAmt = RBkr = RDes = RDel = ''
            tag_RAmt = reward_item.find('span', class_='money')
            if tag_RAmt:
                RAmt = re.match('\D(\d+(\.\d+)?)', tag_RAmt.string).group(1)
            tag_RBkr = reward_item.find('span', class_='num-backers')
            if tag_RBkr:
                RBkr = re.search('\d+', tag_RBkr.string).group(0)
            tag_RDes = reward_item.find('div', class_='desc')
            if tag_RDes:
                RDes = tag_RDes.p.string
            tag_RDel = reward_item.find('time')
            if tag_RDel:
                RDel = tag_RDel.string
            attrs7 = [RAmt, RBkr, RDes, RDel]
            buffer1.extend(attrs7)

    writers[0].writerow(buffer1)
    #-------------------------------------
    buffer2 = [currentDate, currentClock, category, title, creatorID]
    writers[1].writerow(buffer2)
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
