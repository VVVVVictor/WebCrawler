#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = "Wang Miaofei"

import urllib, urllib2, cookielib, httplib
import sys, string, time, os, re, json
import csv
from bs4 import BeautifulSoup
import socket
from random import randint

#常量参数
LOST_PAGE_LIMIT = int(30)
LIST_LENGTH = int(6)
GAP_TIME = int(1)#连续抓取时的等待时间
SLEEP_TIME = int(20) #抓取最新页面的等待时间
CLOSE_WAIT_TIME = int(100) #爬虫被服务器强行关闭后的等待时间
ENABLE_PROXY = True #是否使用代理

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

#代理相关
proxyfileName = 'proxylist'
proxyList = ['111.206.81.248:80']

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
    proxy_handler = urllib2.ProxyHandler({"http": '111.206.81.248:80'})
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), proxy_handler)
    #opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    #opener.addheaders = headers
    urllib2.install_opener(opener)
    
    data = {'UserName':username, 'Password':password, 'Continue':'/default'}
    postdata = urllib.urlencode(data)
    
    try:
        req = urllib2.Request(urlAuth, postdata, headers = getRandomHeaders())
        #req.set_proxy('111.206.81.248:80', 'http')
        result = urllib2.urlopen(req)
        result.close()
        #for index, cookie in enumerate(cj):
        #    print '[',index,']',cookie
            
        req2 = urllib2.Request(urlAccount, headers = getRandomHeaders())
        #req2.set_proxy('111.206.81.248:80', 'http')
        result2 = opener.open(req2)
        result2.close()
        return True
    except (urllib2.URLError) as e:
        if hasattr(e, 'code'):
            print('ERROR:'+str(e.code)+' '+str(e.reason))
        else:
            print(str(e.reason))
    except socket.error as e:
        print('[ERROR] Socket error: '+str(e.errno))
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
    return filedirectory
#--------------------------------------------------
def getProxyList(proxy = None):
    global proxyList
    if proxy == None:
        proxy = proxyfileName
    try:
        proxyfile = open(os.getcwd()+'/'+proxy, 'r')
        proxyList = proxyfile.readlines()
    except:
        print('No proxy file!')
    return proxyList
#--------------------------------------------------
def setProxy(proxyList):
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

#--------------------------------------------------
#生成随机的proxy
def getRandomProxy():
    proxyNumber = len(proxyList)
    proxy = {'http':proxyList[randint(0, proxyNumber-1)]}
    print proxy
    return proxy

#--------------------------------------------------
#从url读取response
def responseFromUrl(url, formdata = None):
    response = None
    if formdata != None:
        formdata = urllib.urlencode(formdata)

    loopCount = 0
    proxyNumber = len(proxyList)
    while True:
        loopCount += 1
        if loopCount > 5:
            print('Failed when trying responseFromUrl().')
            print('URL = '+url)
            break
        try:
            req = urllib2.Request(url, formdata, headers=getRandomHeaders())
            proxyNo = randint(0, proxyNumber-1)
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
            print('[ERROR]IncompleteRead! '+userurl)
            continue
            
        if(response == None):
            print('responseFromUrl get a None')
            time.sleep(1)
            login()
            continue
    #end while
    
    return response

#--------------------------------------------------
#解析用户个人信息，抓取其中各项数据，存入logfile中
def analyzeUserData_ppdai(userID, usercontent, writers):
    soup = BeautifulSoup(usercontent)
    #sheet3 = excelbook.get_sheet(2)
    
    buffer3 = []
    ##抓取时间（0）
    nowtime = time.localtime(time.time())
    getdate = str(time.strftime('%Y/%m/%d', nowtime))
    buffer3.append(getdate)
    gettime = str(time.strftime('%H:%M:%S', nowtime))
    buffer3.append(gettime)
    #借款ID
    buffer3.append(userID)
    #print userID
    
    #借入信用
    tag_credit = soup.find('span', text=u'借入信用：')
    #print(tag_credit.parent)
    tag_credit = tag_credit.find_next_sibling(text=re.compile(u'(\s|\n)*\d+ 分(\s|\n)*'))
    #print(tag_credit)
    borrowCredit = re.search(r"\d+", repr(tag_credit))
    if borrowCredit:
        borrowCredit = borrowCredit.group()
    else:
        borrowCredit = 0
    buffer3.append(borrowCredit)

    #借出信用
    tag_credit = soup.find('span', text=u'借出信用：')
    #print(tag_credit.parent)
    tag_credit = tag_credit.find_next_sibling(text=re.compile(u'(\s|\n)*\d+ 分(\s|\n)*'))
    #print(tag_credit)
    lendCredit = re.search(r"\d+", repr(tag_credit))
    if lendCredit:
        lendCredit = lendCredit.group()
    else:
        lendCredit = 0
    buffer3.append(lendCredit)
    
    #性别 #年龄 #目前身份
    tag_person = soup.find('li', {'class':'user_li'})
    tag_sexAndAge = tag_person.find_all('span')
    sex = tag_sexAndAge[0].string.strip()
    age = tag_sexAndAge[1].string.strip()
    #年龄分档：1(20-25)  2(26-31)  3(32-38)  4(>39)
    if re.search('20', age):
        ageGrade = 1
    elif re.search('26', age):
        ageGrade = 2
    elif re.search('32', age):
        ageGrade = 3
    elif re.search('39', age):
        ageGrade = 4
    else:
        ageGrade = 0
    
    tag_profession = tag_person.find('p', text=re.compile(u'(\s|\n)*目前身份：.*'))
    #print(tag_profession)
    m = re.split(u'：', tag_profession.string.strip())
    profession = m[1].strip()
    
    buffer3.append(sex)
    buffer3.append(ageGrade)
    buffer3.append(profession)
    
    #注册时间
    #TODO: cannot get registertime
    #tag_registerTime = soup.find(text = re.compile(u'\.*注册时间：\.*'))
    tag_registerTime = soup.find('li', class_='reg_login_li')
    #tag_registerTime = soup.find('li', {'class': 'user_li'}).find_next_sibling('li')
    #print tag_registerTime
    registerTime = 'None'
    if tag_registerTime:
        m = re.split(u'：', tag_registerTime.p.string)
        if len(m) > 1:
            registerTime = m[1]
    buffer3.append(registerTime)
    
    
    #投资回报统计
    tag_lenderStat = soup.find('ul', {'class':'LenderStat'})
    lendTimes = badLoan = loanRate = 0
    #默认更新时间为抓取数据当天
    updateTime = time.strftime(u'%Y年%m月%d日', time.localtime(time.time()))
    updateTime = updateTime.decode('utf-8')
    #print(updateTime)
    if tag_lenderStat:
        tag_list = tag_lenderStat.find_all('li')
        #投标次数
        tag_lendTimes = tag_lenderStat.find(text=re.compile(u'\s*共投标.*'))
        if tag_lendTimes:
            lendTimes = tag_lendTimes.parent.find('span').string.strip()
        #print(lendTimes)
        #坏帐计提/借出总金额
        tag_badLoan = tag_lenderStat.find(text=re.compile(u'坏帐计提.*'))#吐槽：网站上的错别字：“帐”“账”
        if tag_badLoan:
            badLoan = tag_badLoan.parent.find('span').string.strip()
        #加权投标利率
        tag_loanRate = tag_lenderStat.find(text=re.compile(u'加权投标利率.*'))
        if tag_loanRate:
            loanRate = tag_loanRate.parent.find('span').string.strip()
        #最后更新时间
        tag_updateTime = tag_lenderStat.find(text=re.compile(u'.*最后更新时间.*'))
        if tag_updateTime:
            m = re.search(u'\d+年\d+月\d+日', tag_updateTime.strip())
            if m:
                updateTime = m.group()
    
    buffer3.append(lendTimes)
    buffer3.append(badLoan)
    buffer3.append(loanRate)
    buffer3.append(updateTime)
    
    
    #借入等级记录 #缺省得分都为0
    identityScore = videoScore = educationScore = mobileScore = bankScore = 0
    fullpayTimes = fullpayScore = overdueTimes = infoScore = communityScore = 0
    #身份认证
    tag_identity = soup.find(href='/cert/identitycert')
    if tag_identity:
        identityScore = tag_identity.parent.find_previous_sibling('td').find(text=re.compile(u'\d+'))
    #print(identityScore)
    #视频认证
    tag_video = soup.find(href='/cert/videousercert')
    if tag_video:
        videoScore = tag_video.parent.find_previous_sibling('td').find(text=re.compile(u'\d+'))
    #学历认证
    tag_education = soup.find(href='/cert/educationcert')
    if tag_education:
        educationScore = tag_education.parent.find_previous_sibling('td').find(text=re.compile(u'\d+'))
    #手机认证
    tag_mobile = soup.find(href='/cert/mobile')
    if tag_mobile:
        mobileScore = tag_mobile.parent.find_previous_sibling('td').find(text=re.compile(u'\d+'))
    #网上银行充值认证
    tag_bank = soup.find(href='/inpour')
    if tag_bank:
        bankScore = tag_bank.parent.find_previous_sibling('td').find(text=re.compile(u'\d+'))
    #全款还清次数 #全款还清得分
    tag_fullpay = soup.find(text = re.compile(u'(\s|\n)*全额还清：.*'))
    if tag_fullpay:
        fullpayTimes = tag_fullpay.parent.find('span').string.strip()
        fullpayScore = tag_fullpay.parent.find_previous_sibling('td').find(text=re.compile(u'\d+'))
    #逾期且还款次数
    tag_overdue = soup.find(text = re.compile(u'(\s|\n)*逾期且还款'))
    if tag_overdue:
        overdueTimes = tag_overdue.parent.find('span').string.strip()
    #资料得分
    tag_infoScore = soup.find('p', text = re.compile(u'资料得分：\d+ 分'))
    if tag_infoScore:
        m = re.search(u'\d+', tag_infoScore.string.strip())
        infoScore = m.group()
    #社区得分
    tag_community = soup.find('p', text = re.compile(u'社区得分：\d+ 分'))
    if tag_community:
        m = re.search(u'\d+', tag_community.string.strip())
        communityScore = m.group()
    
    buffer3.append(identityScore)
    buffer3.append(videoScore)
    buffer3.append(educationScore)
    buffer3.append(mobileScore)
    buffer3.append(bankScore)
    buffer3.append(fullpayTimes)
    buffer3.append(fullpayScore)
    buffer3.append(overdueTimes)
    buffer3.append(infoScore)
    buffer3.append(communityScore)
    
    #借出等级记录
    if soup.find('li', {'id':'li5'}) is None:
        identityScore = videoScore = educationScore = mobileScore = 0
    #身份认证 #视频认证 #学历认证 #手机认证
    #等于借入等级记录中的分数
    loanTimes = fullInterestTimes = interestTimes = overdueTimes = 0
    #投标成功次数
    tag_loanTimes = soup.find(text = re.compile(u'(\s|\n)*投标成功\(借款成功放款\)：(.|\n)*'))
    if tag_loanTimes:
        loanTimes = re.search(u'\d+', tag_loanTimes).group()
        #print('loanTimes = ' + loanTimes)
        #loanTimes = tag_loanTimes.parent.find_previous_sibling('td').find(text=re.compile(u'(\s|\n)*\d+(\s|\n)*'))
    #收到完整本息数
    tag_fullInterest = soup.find(text = re.compile(u'(\s|\n)*收到完整本息：(.|\n)*'))
    if tag_fullInterest:
        fullInterestTimes = re.search(u'\d+', tag_fullInterest).group()
        #print('fullInterestTimes = ' + fullInterestTimes)
    #收到本息次数
    tag_Interest = soup.find(text = re.compile(u'(\s|\n)*收到本息：(.|\n)*'))
    if tag_Interest:
        interestTimes = re.search(u'\d+', tag_Interest).group()
        #print('interestTimes = ' + interestTimes)
    #逾期笔数
    tag_overdue = soup.find(text = re.compile(u'(\s|\n)*逾期\(90—无限期\)：(.|\n)*'))
    if tag_overdue:
        overdueTimes = re.match(u'(.|\n)*：(\d+) 笔(.|\n)*', tag_overdue).group(2)
        #print('overTimes = '+overdueTimes)
    
    buffer3.append(identityScore)
    buffer3.append(videoScore)
    buffer3.append(educationScore)
    buffer3.append(mobileScore)
    buffer3.append(loanTimes)
    buffer3.append(fullInterestTimes)
    buffer3.append(interestTimes)
    buffer3.append(overdueTimes)
    
    #写入excel表3中
    writers[2].writerow(buffer3)
    '''
    col = 0
    for item in buffer3:
        sheet3.write(rows_sheet[2], col, item)
        col += 1
    rows_sheet[2] += 1
    '''
    ##————————————sheet3 finish————————————————————
    
    ##————————————sheet4 begin————————————————————
    #sheet4 = excelbook.get_sheet(3)
    ##借款列表
    tag_borrowListArea = soup.find('div', {'id':'div1'})
    
    if tag_borrowListArea:
        #计算页数
        tag_page = tag_borrowListArea.find('div', {'class':'fen_ye_nav'})
        pageNumber = 1
        if tag_page:
            tag_pageNumber = tag_page.find(text=re.compile(u'共\d+页'))
            pageNumber = re.search(u'\d+', tag_pageNumber).group()
        
        for page in range(1, int(pageNumber)+1):
            #分页获取借款列表
            pageurl = (ppdai_user_url+userID+'?page='+str(page)).encode('utf-8')
            pageurl = urllib2.quote(pageurl, safe=':?/=') #也需要用quote转义
            req_userPage = urllib2.Request(pageurl, None, headers = getRandomHeaders())
            while True:
                try:
                    #response_userPage = responseFromUrl(pageurl)
                    #req_userPage.set_proxy(proxyList[0], 'http')
                    response_userPage = urllib2.urlopen(req_userPage)
                    m_user = response_userPage.read()
                    response_userPage.close()
                    break
                except (urllib2.URLError) as e:
                    print('[ERROR] When get user\'s loan list page!')
                    if hasattr(e, 'code'):
                        print(str(e.code)+': '+str(e.reason))
                    else:
                        print(str(e.reason))
                    time.sleep(CLOSE_WAIT_TIME)
                    continue
                except socket.error as e:
                    print('[ERROR] Socket error: '+str(e.errno))
                    if e.errno == 10054: #被服务器端强行关闭
                        print('[ERROR] Socket was closed by the server.\n Trying to reconnect...')
                    #等待一定时间后重新连接
                    time.sleep(CLOSE_WAIT_TIME)
                    login()
                    continue
                except httplib.IncompleteRead, e:
                    print('[ERROR]IncompleteRead! '+userurl)
                    continue
            #end while
            soup_user = BeautifulSoup(m_user)
            
            tag_borrowListArea = soup_user.find('div', {'id':'div1'})
            if tag_borrowListArea:
                if tag_borrowListArea.find(text=re.compile(u'(\s|\n)*暂时还没有任何借款(\s|\n)*')) is None:
                    tag_borrowList = tag_borrowListArea.find_all('li')
                    for borrowItem in tag_borrowList:
                        buffer4 = []
                        ##抓取时间（0）
                        nowtime = time.localtime(time.time())
                        getdate = str(time.strftime('%Y/%m/%d', nowtime))
                        buffer4.append(getdate)
                        gettime = str(time.strftime('%H:%M:%S', nowtime))
                        buffer4.append(gettime)
                        #借款ID
                        buffer4.append(userID)
                        #订单号和标题
                        tag_a = borrowItem.find('a')
                        orderID = re.search(u'\d+', tag_a['href']).group()
                        title = tag_a.string.strip()
                        
                        tag_tr1 = borrowItem.find('tr') #表格第一行，包括金额、利率、期限、状态
                        #借款金额
                        td_amount = tag_tr1.find('td')
                        amount = re.search(r'\d+(,\d+)?', td_amount.find('span').string)
                        if amount:
                            amount = amount.group().replace(',', '') #删除数字中的逗号
                        #年利率
                        td_rate = td_amount.find_next_sibling('td')
                        rate = re.search(u'\d+', td_rate.string.strip()).group()
                        #借款期限
                        td_months = td_rate.find_next_sibling('td')
                        months = re.search(u'\d+', td_months.string.strip()).group()
                        #状态
                        td_state = td_months.find_next_sibling('td')
                        state = td_state.find('span').string.strip()
                        
                        tag_tr2 = tag_tr1.find_next_sibling('tr')#表格第二行，包括信用等级、进度、投标数、时间等
                        #信用等级
                        td_rank = tag_tr2.find('td')
                        rank = td_rank.find('i')['class'][0]
                        #借款进度
                        td_progress = td_rank.find_next_sibling('td')
                        progress = td_progress.find('div', {'class':'progress2'}).string.strip()
                        progress = re.search(u'\d+(\.\d+)?', progress).group()
                        #已完成投标数
                        td_investNumber = td_progress.find_next_sibling('td')
                        investNumber = re.search(u'\d+', td_investNumber.string.strip()).group()
                        #时间
                        td_time = td_investNumber.find_next_sibling('td')
                        finishtime = re.search(u'\d+/\d+/\d+', td_time.string.strip()).group()
                        
                        buffer4.append(orderID)
                        buffer4.append(title)
                        buffer4.append(amount)
                        buffer4.append(rate)
                        buffer4.append(months)
                        buffer4.append(state)
                        buffer4.append(rank)
                        buffer4.append(progress)
                        buffer4.append(investNumber)
                        buffer4.append(finishtime)
                        
                        #写入excel表4中
                        writers[3].writerow(buffer4)
                        '''
                        col = 0
                        for item in buffer4:
                            sheet4.write(rows_sheet[3], col, item)
                            col += 1
                        rows_sheet[3] += 1
                        '''
        #end for
    #end if tag_borrowListArea
    ##————————————sheet4 finish————————————————————
    
    ##————————————sheet5 begin————————————————————
    #投标列表
    #sheet5 = excelbook.get_sheet(4)
    tag_bidListArea = soup.find('div', {'id':'div2'})
    if tag_bidListArea:
        tr_title = tag_bidListArea.find('tr', {'class':'th_tit'})#标题行
        if tr_title:
            bidList = tr_title.find_next_siblings('tr')
            for bidItem in bidList:
                buffer5 = []
                ##抓取时间（0）
                nowtime = time.localtime(time.time())
                getdate = str(time.strftime('%Y/%m/%d', nowtime))
                buffer5.append(getdate)
                gettime = str(time.strftime('%H:%M:%S', nowtime))
                buffer5.append(gettime)
                #ID
                buffer5.append(userID)
                
                #订单号 #标题
                td_title = bidItem.find('td')
                a_title = td_title.find('a')
                orderID = re.search(u'\d+', a_title['href']).group()
                title = a_title.string.strip()
                #年利率
                td_rate = td_title.find_next_sibling('td')
                rate = re.search(u'\d+', td_rate.string.strip()).group()
                #有效金额
                td_valid = td_rate.find_next_sibling('td')
                validAmount = re.search(u'\d+', td_valid.string.replace(',', '')).group()
                #状态
                td_state = td_valid.find_next_sibling('td')
                state = td_state.find('span')['class'][0]
                #print('state='+state)
                if state == u'status2'.encode('utf-8'):#成功
                    state = 1
                else: #失败
                    state = 0
                #投标时间
                td_time = td_state.find_next_sibling('td')
                datetime = td_time.find('time').string.strip()
                m = re.search(u'(\d+/\d+/\d+) (\d+:\d+:\d+)', datetime)
                day = m.group(1)
                second = m.group(2)
                
                buffer5.append(orderID)
                buffer5.append(title)
                buffer5.append(rate)
                buffer5.append(validAmount)
                buffer5.append(state)
                buffer5.append(day)
                buffer5.append(second)
                
                #写入excel表4中
                writers[4].writerow(buffer5)
                '''
                col = 0
                for item in buffer5:
                    sheet5.write(rows_sheet[4], col, item)
                    col += 1
                rows_sheet[4] += 1
                '''
    
    ##————————————sheet5 finish————————————————————
#--------------------------------------------------
#解析网页内容webcontent，抓取其中各项数据，存入logfile中
def analyzeData_ppdai(orderID, webcontent, writers):
    soup = BeautifulSoup(webcontent)
    #print soup.__class__
    #print(soup.original_encoding)
    #soup.prettify()
    #print(soup)
    
    ##————————————sheet1 begin————————————————————
    buffer1 = []
    ##抓取时间（0）
    nowtime = time.localtime(time.time())
    getdate = str(time.strftime('%Y/%m/%d', nowtime))
    buffer1.append(getdate)
    gettime = str(time.strftime('%H:%M:%S', nowtime))
    buffer1.append(gettime)
    
    ##订单号（1）
    buffer1.append(orderID)
    
    
    ##订单类型（2）:安（应收款安全标）/非（非体现标）/赔（审错就赔付标）/保（个人担保标）/农（助农计划）
    an = fei = pei = bao = nong = 0
    tag_an = soup.find('i', {'class':'an'})
    if tag_an:  an = 1
    tag_fei = soup.find('i', {'class':'fei'})
    if tag_fei: fei = 1
    tag_pei = soup.find('i', {'class':'pei'})
    if tag_pei: pei = 1
    tag_bao = soup.find('i', {'class':'bao'})
    if tag_bao: bao = 1
    tag_nong = soup.find('i', {'class':'nong'})
    if tag_nong: nong = 1
    
    buffer1.append(an)
    buffer1.append(fei)
    buffer1.append(pei)
    buffer1.append(bao)
    buffer1.append(nong)
    
    #标题(3)
    tag_title = soup.find('td', {'class':'list_tit'})
    title = tag_title.find('h1').string
    #print(title)
    #logfile.write(title.encode('gbk')+',')
    buffer1.append(title)
    
    ##金额（4）
    tag_amount = soup.find('span', {'id':'TotalAmount'})
    amount = re.search(r'\d+(,\d+)?', tag_amount.string)
    if amount:
        amount = amount.group().replace(',', '') #删除数字中的逗号
        #logfile.write(amount+',')
        buffer1.append(amount)
    else:
        #logfile.write('NA,')
        buffer1.append('')

    ##年利率（5）
    tag_interestRate = soup.find('label', text=re.compile(u'年利率：'))
    #print(tag_interestRate)
    interestRate = tag_interestRate.find_next_sibling('span').string
    interestRate = re.search(r'\d+', interestRate).group()
    #print(interestRate)
    buffer1.append(interestRate)

    ##期限（6）
    #tag_timeLimit = soup.find(text=re.compile(u'\w*限：'))
    #ATTENTION!!!!!
    tag_timeLimit = soup.find('label', text=re.compile(u'期(\u00A0)*限：'))
    #print(tag_timeLimit.string.encode('utf-8'))
    timeLimit = tag_timeLimit.find_next_sibling('span').string
    timeLimit_months = re.search(r'\d+', timeLimit)
    if timeLimit_months:
        #logfile.write(timeLimit_months.group()+',')
        buffer1.append(timeLimit_months.group())
    else:
        #logfile.write('NA,')
        buffer1.append('')
    
    #print(buffer1)
    
    ##还款方式（7）
    p = re.compile(u'.*(，每月还款|月还息|一次还本付息).*')
    tag_refund = soup.find(text = p)
    tag_refund = tag_refund.strip()
    #print(tag_refund)
    p = re.compile(u'：')
    m = p.split(tag_refund)
    buffer1.append(m[0])
    
    
    ##每月还款金额（8）
    if len(m) > 1:
        temp = m[1].replace(',', '')
        refund = re.search(r'\d+', temp)
        if(refund):
            refund = refund.group()
        else:
            refund = ''
    else:
        refund = ''
    buffer1.append(refund)
    
    ##进度(9)
    tag_progress = soup.find('div', {'id':'progress'})
    progress = re.search(r'\d+(\.\d+)?', tag_progress.string).group()
    buffer1.append(progress)
    
    ##借款状态（10）
    tag_state = soup.find(['a','span'], text=re.compile(u'\s*(借款成功|借款审批中|正在预审|投标已结束)\s*'))
    if tag_state:
        state = tag_state.string.strip()
    else:
        state = ''
    buffer1.append(state)
        
    #print(tag_success)
    ##剩余时间、结束时间（11）
    tag_leftTime = soup.find('span', {'id':'leftTime'})
    leftTime = tag_leftTime.string.strip()
    matchFinishTime =re.search(u'结束时间：(\d+/\d+/\d+)', leftTime)
    if matchFinishTime:
        finishTime = matchFinishTime.group(1)
        #print finishTime
        leftTime = ''
    else:
        finishTime = ''
    buffer1.append(leftTime)
    buffer1.append(finishTime)
        
    ##总投标数、浏览量（12）
    tag_investNumber = soup.find(text=re.compile(u'总投标数：(\d+)(\s|\n)*\| 浏览量：(\d+)'))
    m = re.search(u'总投标数：(\d+)(\s|\n)*\| 浏览量：(\d+)', tag_investNumber)
    investNumber = m.group(1)
    viewNumber = m.group(3)
    buffer1.append(investNumber)
    buffer1.append(viewNumber)
    
    #借款id(13)
    tag_UserName = soup.find('div', {'class':'user_face_name'})
    userName = tag_UserName.a.string
    #logfile.write(userName+',')
    buffer1.append(userName)
    #print(str(userName.string)+'\n')

    #借入信用等级（14）
    tag_borrowRank = soup.find('i', {'title':'信用等级'})
    borrowRank = tag_borrowRank['class']
    buffer1.append(borrowRank[0])
    
    #借入信用分数（15）
    tag_borrowScore = tag_borrowRank.next_sibling #'   （28）分   '
    #print(tag_borrowScore)
    borrowScore = re.search(u'\d+', tag_borrowScore)
    if borrowScore:
        borrowScore = borrowScore.group()
    else:
        borrowScore = 0
    buffer1.append(borrowScore)
    
    #借出信用分数（16）
    tag_lendScore = soup.find('p', text=re.compile(u'(\s|\n)*借出信用：\.*'))
    lendScore = re.search(r'\d+', tag_lendScore.string).group()
    buffer1.append(lendScore)
    
    #成功次数（17）
    tag_timesOfSuccessAndFail = soup.find('h3', text=re.compile(u'\.*次成功，\d+ 次流标\.*'))
    #print(tag_timesOfSuccessAndFail)
    m = re.findall(r'\d+', tag_timesOfSuccessAndFail.string.strip())
    timesOfSuccess = m[0]
    buffer1.append(timesOfSuccess)
    
    #流标次数（18）
    timesOfFail = m[1]
    buffer1.append(timesOfFail)
    
    #身份认证（19）
    tag_hukou = soup.find('i', {'class':'hukou'})
    if tag_hukou:
        hukouIdentify = 1
    else:
        hukouIdentify = 0
    buffer1.append(hukouIdentify)
    #视频认证（20）
    tag_video = soup.find('i', {'class':'video'})
    if tag_video:
        videoIdentify = 1
    else:
        videoIdentify = 0
    buffer1.append(videoIdentify)
    #学历认证（21）
    tag_record = soup.find('i', {'class':'record'})
    if tag_record:
        recordIdentify = 1
    else:
        recordIdentify = 0
    buffer1.append(recordIdentify)
    
    #手机认证（22）
    tag_phone = soup.find('i', {'class':'phone'})
    if tag_phone:
        phoneIdentify = 1
    else:
        phoneIdentify = 0
    buffer1.append(phoneIdentify)
    
    ##借款目的（23）
    ##性别（24）
    ##年龄（25）
    ##婚姻状况（26）
    ##文化程度（27）
    ##住宅状况（28）
    ##是否购车（29）
    tag_table = soup.find('th', text=re.compile(u'(\s|\n)*借款目的(\s|\n)*'))
    if tag_table:
        tag_table = tag_table.parent.find_next_sibling('tr').find_all('td')
        #print(len(tag_table))
        purpose = tag_table[0].string.strip()
        sex = tag_table[1].string.strip()
        age = tag_table[2].string.strip()
        marriage = tag_table[3].string.strip()
        degree = tag_table[4].string.strip()
        house = tag_table[5].string.strip()
        car = tag_table[6].string.strip()
    else:
        purpose = sex = age = marriage = degree = house = car = ''
    buffer1.append(purpose)
    buffer1.append(sex)
    buffer1.append(age)
    buffer1.append(marriage)
    buffer1.append(degree)
    buffer1.append(house)
    buffer1.append(car)
    
    #户口认证、学历认证、网站认证
    hukouPlace = schoolName = eduBgd = eduType = ''
    tag_hukouPlace = soup.find('span', {'class':'hukou'})
    if tag_hukouPlace:
        hukouPlace = re.search(u'户口所在地：(.*)', tag_hukouPlace.string).group(1)
        
    tag_school = soup.find('span', {'class':'record'})
    if tag_school:
        eduRecord = re.search(u'毕业学校：(.*)，学历：(.*)，学习形式：(.*)）', tag_school.string)
        if eduRecord:
            schoolName = eduRecord.group(1)
            eduBgd = eduRecord.group(2)
            eduType = eduRecord.group(3)
    
    buffer1.append(hukouPlace)
    buffer1.append(schoolName)
    buffer1.append(eduBgd)
    buffer1.append(eduType)
    
    tag_siteAuth = soup.find('h4', text=u'网站认证：')
    rank_taobao = taobao = ''
    if tag_siteAuth:
        siteAuth = 1
        list_taobao = tag_siteAuth.find_next_siblings('span', {'class':'taobao'})#可能有多条
        if len(list_taobao) > 0:
            taobao = 1
            guanCount = zuanCount = 0
            for item_taobao in list_taobao:
                guanCount += len(item_taobao.find_all('img', {'src':'http://static.ppdai.com/skin/images/sell_guan.gif'}))
                zuanCount += len(item_taobao.find_all('img', {'src':'http://static.ppdai.com/skin/images/sell_zhuan.gif'})) #写网站的人z/zh不分
            rank_taobao = guanCount*10+zuanCount
            m_tmall = re.search(u'天猫商城', unicode(list_taobao))
            if m_tmall:
                rank_taobao = u'天猫商城'
        else:
            taobao = 0
    else:
        siteAuth = 0
    buffer1.append(siteAuth)
    buffer1.append(taobao)
    buffer1.append(str(rank_taobao))
    #print(tag_table)
    #tag_basicInfo = tag_table.find_next_sibling('tr')
    #print(tag_basicInfo)
    
    ##关于我（30）
    tag_aboutme = soup.find('h3', text=re.compile(u'(\s|\n)*关于我(\s|\n)*'))
    #print(tag_aboutme.next_sibling.next_sibling)
    if tag_aboutme:
        aboutme = tag_aboutme.find_next_sibling('p').string
        if aboutme:
            aboutme = aboutme.strip()
            aboutme = aboutme.replace(u'\u000D\u000A', '') #删除换行
    else:
        aboutme = ''
    ##我想要使用这笔款项做什么（31）
    tag_wanttodo = soup.find('h3', text=re.compile(u'(\s|\n)*我想要使用这笔款项做什么(\s|\n)*'))
    if tag_wanttodo:
        wanttodo = tag_wanttodo.find_next_sibling('p').string
        if wanttodo:
            wanttodo = wanttodo.strip()
            wanttodo = wanttodo.replace(u'\u000D\u000A', '') #删除换行
    else:
        wanttodo = ''
    ##我的还款能力说明（32）
    tag_refundAbility = soup.find('h3', text=re.compile(u'(\s|\n)*我的还款能力说明(\s|\n)*'))
    if tag_refundAbility:
        refundAbility = tag_refundAbility.find_next_sibling('p').string
        if refundAbility:
            refundAbility = refundAbility.strip()
            refundAbility = refundAbility.replace(u'\u000D\u000A', '') #删除换行
    else:
        refundAbility = ''
    
    buffer1.append(aboutme)
    buffer1.append(wanttodo)
    buffer1.append(refundAbility)
    
    #将数据写入表1中
    writers[0].writerow(buffer1)
    '''
    sheet1 = excelbook.get_sheet(0)
    col = 0
    #row = excelbook.sheet_by_index(0).nrows
    buffer11 = []
    for item in buffer1:
        sheet1.write(rows_sheet[0], col, item)
        col += 1
        #buffer11.append(item.decode('gbk'))
    rows_sheet[0] += 1 #行数加1
    '''
    ##————————————sheet1 finish————————————————————
    
    ##————————————sheet2  begin————————————————————
    #sheet2 = excelbook.get_sheet(1)
    tag_investList = soup.find('th', text=re.compile(u'(\s|\n)*投标人(\s|\n)*'))
    if tag_investList:
        '''
        lastItem = tag_investList.parent
        count = 0;
        while True:
            count += 1
            investItem = lastItem.find_next_sibling('tr')
            lastItem = investItem
            #print(count)
        '''
        investList = tag_investList.parent.find_next_siblings('tr')
        #print("length: "+str(len(investList)));
        #print investList
        for investItem in investList:
            investInfo = investItem.find_all('td')
            
            if(len(investInfo)<4):
                break;
            #投标ID
            invest_id = investInfo[0].find('a').string.strip()
            #当前利率
            invest_rate = investInfo[1].string.strip()
            invest_rate = re.search(u'\d+', invest_rate).group()
            #投标金额
            invest_amount = investInfo[2].string.strip()
            invest_amount = re.search(r'\d+(,\d+)?', invest_amount)
            invest_amount = invest_amount.group().replace(',', '') #删除数字中的逗号
            #投标时间
            invest_time = investInfo[3].string.strip()
            m = re.search(u'(\d+/\d+/\d+) (\d+:\d+:\d+)', invest_time)
            invest_day = m.group(1)
            invest_second = m.group(2)
            
            buffer2 = []
            ##抓取时间（0）
            nowtime = time.localtime(time.time())
            getdate = str(time.strftime('%Y/%m/%d', nowtime))
            buffer2.append(getdate)
            gettime = str(time.strftime('%H:%M:%S', nowtime))
            buffer2.append(gettime)
            buffer2.append(orderID) #订单号
            buffer2.append(invest_id)
            buffer2.append(invest_rate)
            buffer2.append(invest_amount)
            buffer2.append(invest_day)
            buffer2.append(invest_second)
            
            writers[1].writerow(buffer2)
            '''
            col = 0
            for item in buffer2:
                sheet2.write(rows_sheet[1], col, item)
                col += 1
            rows_sheet[1] += 1 
            '''
            
            
    ##————————————sheet2 finish————————————————————
    
    
    ##————————————sheet3-5 begin————————————————————
    '''分析借款人账号信息'''
    userurl = (ppdai_user_url+userName).encode('utf-8')
    userurl = urllib2.quote(userurl, safe=':?/=')#使用urllib.quote将中文转义成html
    req_user = urllib2.Request(userurl, None, getRandomHeaders()) 
    
    while True:
        try:
            #response_user = responseFromUrl(userurl)
            #req_user.set_proxy(proxyList[0], 'http')
            response_user = urllib2.urlopen(req_user)
            if response_user == None:
                break;
            m_user = response_user.read()
            response_user.close()
            #print m_user
            analyzeUserData_ppdai(userName, m_user, writers)
            #保存用户网页
            strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
            uName = filedirectory + userFolder + 'user_'  + userName +'_'+strtime+ '.html'
            uName = re.sub(re.compile(r'\*|\?|"|<|>|\|'), '_', uName) #替换部分导致文件名错误的字符
            f = open(uName, 'wb')
            f.write(m_user)
            f.close()
            break
        except (urllib2.URLError) as e:
            print('[ERROR] When user page!')
            if hasattr(e, 'code') and e.code == 404:
                print('[ERROR] User account has been canceled!') #用户账户已注销
                break;
            if hasattr(e, 'code'):
                print(str(e.code)+': '+str(e.reason))
            else:
                print(str(e.reason))
            time.sleep(CLOSE_WAIT_TIME)
            continue
        except socket.error as e:
            print('[ERROR] Socket error: '+str(e.errno))
            if e.errno == 10054: #被服务器端强行关闭
                print('[ERROR] Socket was closed by the server.\n Trying to reconnect...')
            #等待一定时间后重新连接
            time.sleep(CLOSE_WAIT_TIME)
            login()
            continue
        except httplib.IncompleteRead, e:
            print('[ERROR]IncompleteRead! '+userurl)
            continue
    #end while

#enddef analyzeData_ppdai
