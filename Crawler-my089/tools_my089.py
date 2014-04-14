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
filedirectory = u'D:\\datas\\pythondatas\\my089\\'

#For login
urlHost = u'http://www.my089.com'
urlLogin = u'https://member.my089.com/safe/login.aspx'
urlIndex = u'https://member.my089.com/safe/'
urlDefault = u'/Loan/default.aspx'
urlSucceed = u'/Loan/Succeed.aspx'

username = u'victor1991'
password = u'wmf123456'
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36', 'Host':'www.my089.com'}

usePattern = re.compile(u'((/Loan/)?Detail\.aspx\?sid=(\d|-)+)|(/Loan/Succeed.aspx)|(/ConsumerInfo1\.aspx\?uid=(\d|\w)+)')
loanPattern = re.compile(u'(/Loan/)?Detail\.aspx\?sid=(\d|-)+')
orderPattern = re.compile(u'http://www.my089.com/Loan/Detail\.aspx\?sid=((\d|-)+)')
consumerPattern = re.compile(u'http://www.my089.com/ConsumerInfo1\.aspx\?uid=((\d|\w)+)')
errorPattern = re.compile(u'/Error/default\.aspx')
needloginPattern = re.compile(u'/safe/login')
defaultPattern = re.compile(urlHost + '/Loan/default\.aspx(\?pid=1)?')
succeedPattern = re.compile(urlHost + '/Loan/Succeed\.aspx(\?pid=1)?')

TRY_LOGIN_TIMES = 5 #尝试登录次数
#宏常量定义
BORROW_TYPE = 1
BID_TYPE = 2
FRIEND_TYPE = 3
#用户页面说明
#个人信息 ConsumerInfo1.aspx?uid=
#信用评价 ConsumerInfo.aspx?uid=
#还款明细账单 4 #积分50分
#论坛帖子 2
#正在招标中的借款 ConsumerInfo3.aspx?uid=

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

    md5pwd = hashlib.md5(password).hexdigest();
    print 'md5 password = '+md5pwd
    #md5pwd = '73f7d9af739c494a455418da7a2efcce'
    data = {'txtUid':username, 'MD5Pwd':md5pwd, 'txtPwd1':'', 'SaveMinits':'10080', 'btnLogin':u'立即登录'}
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
#分析页面取得所有的url
def findAllUrl(url):
    mr_succeed = succeedPattern.match(url)
    mr_default = defaultPattern.match(url)
    mr_order = orderPattern.match(url)
    mr_consumer = consumerPattern.match(url)
    list_url = []

    #投资默认页面
    if mr_default:
        print 'Page default'
        content = readFromUrl(url)
        soup = BeautifulSoup(content)
        tag_pageCount = soup.find('span', {'class':'z_page'})
        pageCount = 1
        if tag_pageCount:
            pageCount = re.search('\d', tag_pageCount.string).group(0)
            #print pageCount
        for i in range(1, int(pageCount)+1):
            main_content = BeautifulSoup(readFromUrl(urlHost+urlDefault+'?pid='+str(i))).find('div', {'id':'man'})
            list_temp = findUrl(main_content.prettify())
            list_url.extend(list_temp)
            
    #投资成功页面        
    elif mr_succeed:
        print 'Page succeed'
        for i in range(1, 100):
            print('succeed loop:'+str(i))
            main_content = BeautifulSoup(readFromUrl(urlHost+urlSucceed+'?pid='+str(i))).find('div', {'id':'man'})
            list_temp = findUrl(main_content.prettify())
            list_url.extend(list_temp)
    #order页面
    elif mr_order:
        #logFile.write(url+'\n')
        sid = mr_order.group(1)
        uid = getUidFromLoan(url)
        content = readFromUrl(url)
        if content:
            list_temp = findUrl(content) #初始页面中的url
            list_url.extend(list_temp)
            #print list_url
            #print getDetailUrl(sid, uid, 8)
            list_temp = findUrl(readFromUrl(getDetailUrl(sid, uid, 8))) #待还记录中的url
            list_url.extend(list_temp)
    #end elif

    #consumer页面
    elif mr_consumer:
        uid = mr_consumer.group(1)
        consumer_content = readFromUrl(url)
        #print consumer_content
        list_temp = findUrl(consumer_content) #用户初始页面，借款列表第一页
        list_url.extend(list_temp)

        #使用“下一页”按钮遍历借款列表页
        content = consumer_content
        borrowPageCount = 0
        #soup = BeautifulSoup(content)
        while True:
            #print 'borrow Page:' + str(borrowPageCount)
            soup = BeautifulSoup(content)
            if not soup.find('table', {'id':'ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_dlBrrows'}): #查看不到借款信息
                break
            borrowPageCount += 1
            content = getNextPage(BORROW_TYPE, soup, url)
            if not content:
                break; #没有下一页
                
            borrow_content = BeautifulSoup(content).find('div', {'id':'ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_hdivBrrows'})
            list_temp = findUrl(borrow_content.prettify())
            list_url.extend(list_temp)

            #borrowPageCount += 1
        #end while
        #print('borrowPageCount = '+str(borrowPageCount))

        #使用“下一页”按钮遍历投标记录页
        content = consumer_content
        bidPageCount = 1
        while True:
            #print 'bid Page:' +str(bidPageCount)
            soup = BeautifulSoup(content)
            if not soup.find('div', {'id':'ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_hdivBids'}).find('table'): #查看不到投标信息
                break
            bidPageCount += 1
            content = getNextPage(BID_TYPE, soup, url)
            if not content:
                break; #没有下一页
                
            bid_content = BeautifulSoup(content).find('div', {'id':'ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_hdivBids'}) #只选取投标记录区域
            list_temp = findUrl(bid_content.prettify())
            #print('add '+str(len(list_temp)))
            list_url.extend(list_temp)

        #end while
        #print('bidPageCount = '+str(bidPageCount))

        #使用“下一页”按钮遍历好友列表
        content = consumer_content
        friendPageCount = 1
        while True:
            soup = BeautifulSoup(content)
            if not soup.find('table', {'id':'ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_dlFriends'}):#查看不到好友信息
                break
            friendPageCount += 1
            content = getNextPage(FRIEND_TYPE, soup, url)
            if not content:
                break; #没有下一页
                
            friend_content = BeautifulSoup(content).find('table', {'id':'ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_dlFriends'})
            list_temp = findUrl(friend_content.prettify())
            list_url.extend(list_temp)
        #end while
        #print('friendPageCount = '+str(friendPageCount))
                
        
    list_url = list(set(list_url)) #list去重
    return list_url
#--------------------------------------------------
#从consumer页面上读取下一页内容
def getNextPage(type, soup, url):
    viewState = soup.find('input', {'id':'__VIEWSTATE'})['value']
    eventValidation = soup.find('input', {'id':'__EVENTVALIDATION'})['value']

    eventString = {BORROW_TYPE:'ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder1$Pagination1$lbtnNext', BID_TYPE:'ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder1$Pagination2$lbtnNext', FRIEND_TYPE: 'ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder1$Pagination3$lbtnNext'}
    
    formdata = {'__EVENTTARGET':eventString[type], '__EVENTARGUMENT':'', '__VIEWSTATE':viewState, '__EVENTVALIDATION':eventValidation}
    result = responseFromUrl(url, formdata)
            
    if result:
        content = result.read()
        result.close()
        return content
    else:
        return None#没有下一页
#--------------------------------------------------
#从loan detail页面获取当前用户id
def getUidFromLoan(url):
    if orderPattern.match(url):
        webcontent = readFromUrl(url)
        if webcontent:
            soup = BeautifulSoup(webcontent)
    
            tag_uid = soup.find('span', text = re.compile(u'用 户 名：'))
            #print 'tag_uid='+str(tag_uid)
            href_uid = tag_uid.find_next_sibling('span').a['href']
            uid = re.search('/ConsumerInfo1\.aspx\?uid=((\d|\w)+)', href_uid).group(1)
            return uid
    return None
    
#--------------------------------------------------
#分析页面内链接
def findUrl(webcontent):
    list_url = []
    if(webcontent == None):
        print("[ERROR] webcontent is None in findUrl()")
        return list_url #返回空list
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
                href = href.replace('-', '') #去掉所有横杠
                list_url.append(href)
    return list_url
#end def findUrl

#--------------------------------------------------
#从url读取response
def responseFromUrl(url, formdata = None):
    response = None
    if formdata != None:
        formdata = urllib.urlencode(formdata)
    try:
        while True:
            req = urllib2.Request(url, formdata, headers = headers)
            response = urllib2.urlopen(req)
            curUrl = response.geturl()
            if errorPattern.search(curUrl): #进入错误页面
                response.close()
                return None
            elif needloginPattern.search(curUrl):
                print('NEED LOGIN!')
                login()
                continue
            break
    except (urllib2.URLError) as e:
        if hasattr(e, 'code'):
            print('ERROR:'+str(e.code)+' '+str(e.reason))
        print(str(e.reason))
        print('url = '+url)
            
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
#从/Loan/Detail.aspx 得到更细节的信息
#借款信息 1
#投标记录 2
#还款信用 3
#标的奖励 4
#账户详情 5
#资料审核 7
#待还记录 8
def getDetailUrl(sid, uid, doNumber):
    return urlHost + '/Loan/GetDetailItem.aspx\?sid='+str(sid)+'&uid='+str(uid)+'&do='+str(doNumber);

#--------------------------------------------------
def analyzeData(webcontent, sid, csvwriter):
    soup = BeautifulSoup(webcontent)
    
    tag_uid = soup.find('span', text = re.compile(u'用 户 名：'))
    #print 'tag_uid='+str(tag_uid)
    href_uid = tag_uid.find_next_sibling('span').a['href']
    uid = re.search('/ConsumerInfo1\.aspx\?uid=((\d|\w)+)', href_uid).group(1)

    #http://www.my089.com/Loan/GetDetailItem.aspx?sid=14032223504661291286300010184496&uid=E57D1C7DEAA59546&do=2&rnd=0.45415010140277445
    #投标记录 do=2
    #还款信用 do=3
    #标的奖励 4
    #账户详情 5
    #资料审核 7
    #待还记录 8
    m_toRepay = readFromUrl(getDetailUrl(8))
    print 'm_toRepay = '+m_toRepay


    return uid;

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
