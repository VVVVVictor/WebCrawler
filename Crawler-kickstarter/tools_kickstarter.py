#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = "Wang Miaofei"

import urllib, urllib2, cookielib
import sys, string, time, os, re, json
import csv
from bs4 import BeautifulSoup
import socket
from random import randint

configfileName = 'config'
filedirectory = u'D:\\datas\\pythondatas\\kickstarter\\'
enable_proxy = True

#For login
urlHost = u'https://www.kickstarter.com'
urlLogin = u'https://www.kickstarter.com/user_sessions'
urlIndex = u'https://www.kickstarter.com/'
urlCategory = u'https://www.kickstarter.com/discover/advanced?'

#for excel

username = u'victor1991@126.com'
password = u'wmf123456'
#'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
ipAddress = ['191.234.5.2', '178.98.246.45, 231.67.9.23']
host = 'www.kickstarter.com'
userAgent = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36']
#headers=[{'User-Agent': userAgent[0], 'Host': 'www.kickstarter.com', 'X-Forwarded-For':ipAddress}, {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'User-Agent': userAgent[1], 'Host': 'www.kickstarter.com', 'X-Forwarded-For':ipAddress}, {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'User-Agent': userAgent[2], 'Host': 'www.kickstarter.com', 'X-Forwarded-For':ipAddress}]
HEADERS_NUMBER = 3

TRY_LOGIN_TIMES = 5 #尝试登录次数
CATEGORY_COUNT = 15

#--------------------------------------------------
#读取配置文件，返回目标文件夹地址
def getConfig():
    global filedirectory, username, password, threadCount
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
                elif m.group(1) == u'threadCount':
                    threadCount = m.group(2)
                #print filedirectory
        configfile.close()
    except:
        configfile = open(os.getcwd()+'/'+configfileName, 'wb')
        configfile.write('filedirectory = '+filedirectory+'\n')
        configfile.write('username = '+username+'\n')
        configfile.write('password = '+password+'\n')
        configfile.write('threadCount = '+threadCount+'\n')
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

    #md5pwd = hashlib.md5(password).hexdigest();
    #print 'md5 password = '+md5pwd
    #md5pwd = '73f7d9af739c494a455418da7a2efcce'
    data = {'utf8':'%E2%9C%93', 'user_session[email]':username, 'user_session[password]':password, 'commit':'Log me in!', 'user_session[remember_me]':'0', 'user_session[remember_me]':'1'};
    postdata = urllib.urlencode(data)
    for i in range(TRY_LOGIN_TIMES):
        try:
            #print headers[randint(0, HEADERS_NUMBER-1)]
            req = urllib2.Request(urlLogin, postdata, getRandomHeaders())
            result = urllib2.urlopen(req)
            if urlIndex != result.geturl(): #通过返回url判断是否登录成功
                print result.geturl()
                print(u'[FAIL]Wrong USERNAME or PASSWORD. Please try again!')
                return False
            result.close()
    
            req2 = urllib2.Request(urlIndex, headers=getRandomHeaders())
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
def responseFromUrl(url, formdata = None, headers = None):
    response = None
    #here in kickstarter are all HTTPS
    '''
    proxy_handler = urllib2.ProxyHandler({"http": '186.238.51.149:8080'})
    if enable_proxy:
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)
    '''
    if formdata != None:
        formdata = urllib.urlencode(formdata)
    if headers == None:
        headers = getRandomHeaders()
    loopCount = 0
    while True:
        loopCount += 1
        if loopCount > 5:
            print('\nFailed when trying responseFromUrl():')
            print('  URL = '+url+'\n')
            break
        try:
            req = urllib2.Request(url, formdata, headers)
            response = urllib2.urlopen(req)
            curUrl = response.geturl()
            break
        except (urllib2.URLError) as e:
            if hasattr(e, 'code'):
                print('ERROR:'+str(e.code)+' '+str(e.reason))
                if(e.code == 429):
                    time.sleep(2)
                    continue
            
        if(response == None):
            print('responseFromUrl get a None')
            time.sleep(1)
            login()
            continue
    #end while
    
    return response

#--------------------------------------------------
#生成一个随机的headers
def getRandomHeaders():
    ipNumber = len(ipAddress)
    agentNumber = len(userAgent)
    headers = {'User-Agent': userAgent[randint(0, agentNumber-1)], 'Host': host, 'X-Forwarded-For': ipAddress[randint(0, ipNumber-1)]}
    return headers
    
#--------------------------------------------------
#从url读取页面内容
def readFromUrl(url, formdata = None, headers = None):
    response = responseFromUrl(url, formdata, headers)
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
def getWordNumber(str):
    list_word = str.split()
    return len(list_word)
    
#--------------------------------------------------
def cleanString(str):
    str = str.replace('\r\n', ' ')
    str = str.replace('\n', ' ')
    return str.strip()
#--------------------------------------------------
def analyzeData(url, writers):
    webcontent = readFromUrl(url)
    #print webcontent
    soup = BeautifulSoup(webcontent)
    buffer1 = []
    #******************************
    #页面上栏部分
    currentDate = getTime('%Y-%m-%d')
    currentClock = getTime('%H:%M:%S')

    category = title = updates = backers = comments = location = ''
    updatesContent = commentsContent = ''

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
    desContent = riskContent = ''
    tag_video = soup.find('div', {'id':'video-section'})
    if tag_video and tag_video['data-has-video']=='true':
        video = '1'
    tag_description = soup.find('div', {'class':'full-description'})
    if tag_description:
        desContent = cleanString(tag_description.get_text())
        desLength = getWordNumber(desContent)
        desPics = str(len(tag_description.find_all('img')))
    tag_risk = soup.find('div', {'id':'risks'})
    if tag_risk:
        #print tag_risk.get_text()
        riskContent = cleanString(tag_risk.get_text())
        riskLength = getWordNumber(riskContent)
    tag_FAQ = soup.find('div', {'id':'project-faqs'})
    if tag_FAQ:
        FAQQ = str(len(tag_FAQ.find_all('div', {'class':'faq-question'})))
        FAQA = str(len(tag_FAQ.find_all('div', {'class':'faq-answer'})))
    attrs2 = [video, desLength, desPics, desContent, riskLength, riskContent, FAQQ, FAQA]

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
        creatorName = creatorName.replace(';', '.')
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
    attrs6 = []
    if tag_creatorUrl:
        creatorUrl = tag_creatorUrl['content']
        #print creatorUrl
        creatorID = re.match('https://www\.kickstarter\.com/profile/(\S+)', creatorUrl).group(1)
        creatorContent = readFromUrl(creatorUrl)
        soup2 = BeautifulSoup(creatorContent)
        tag_joined = soup2.find('meta', {'property':'kickstarter:joined'})
        if tag_joined:
            joinedDate = re.match('(\d+-\d+-\d+) .*', tag_joined['content']).group(1)
        tag_bio = soup2.find('meta', {'property':'og:description'})
        if tag_bio:
            bioLength = getWordNumber(tag_bio['content'])
        tag_NBacked = soup2.find('a', {'id':'list_title'})
        if tag_NBacked:
            NBacked = re.search('\d+', tag_NBacked.get_text()).group(0)
            tag_NCreated = tag_NBacked.parent.find_next_sibling('li')
            #print tag_NCreated
            if tag_NCreated:
                NCreated = re.search('\d+', tag_NCreated.get_text()).group(0)
        attrs6 = [str(creatorID), bioLength, lastLoginDate, joinedDate, str(NBacked), str(NCreated)]
        #to get number of projects of each category
        tag_circle = soup2.find('div', {'id':'small_circle'})
        if tag_circle:
            scriptPart = tag_circle.find_next('script').string
            scriptData = re.search('circle_data = (\[.*\]);', scriptPart).group(1)
            script = json.loads(scriptData)
            for item in script:
                #print item['projects_backed'],
                attrs6.append(item['projects_backed'])
        else:
            #for deleted user
            for i in range(CATEGORY_COUNT):
                attrs6.append('')
            #print '-'
        
    
    #******************************
    buffer1.extend(attrs1)
    buffer1.extend(attrs2)
    buffer1.extend(attrs3)
    buffer1.extend(attrs4)
    buffer1.extend(attrs5)
    buffer1.extend(attrs6)

    writers[0].writerow(buffer1)
    #-------------------------------------
    basicInfo = [currentDate, currentClock, category, title, creatorID]
    backersUrl = url+'/backers'
    analyzeBackersData(backersUrl, writers[1], basicInfo)

    tag_updatesNav = soup.find('a', {'id': 'updates_nav'})
    if tag_updatesNav:
        updatesUrl = tag_updatesNav['href']
        updatesUrl = urlHost + updatesUrl
        analyzeUpdatesData(updatesUrl, writers[2], basicInfo)

    tag_commentsNav = soup.find('a', {'id': 'comments_nav'})
    if tag_commentsNav:
        commentsUrl = tag_commentsNav['href']
        commentsUrl = urlHost + commentsUrl
        analyzeCommentsData(commentsUrl, writers[3], basicInfo)

    tempBuff = [url]
    tempBuff.extend(basicInfo)
    analyzeRewardData(soup, writers[4], tempBuff)
    
    analyzeFaqData(soup, writers[5], tempBuff)
#end analyzeData()
#-----------------------------------------------------
def analyzeBackersData(url, writer, attrs):
    backersContent = readFromUrl(url)
    soup_backers = BeautifulSoup(backersContent)
    tag_backerPage = soup_backers.find('li', class_='page')
    if tag_backerPage:
        backerList = tag_backerPage.find_all('div', class_='NS_backers__backing_row')
        for backerItem in backerList:
            buffer2 = [url+'/backers']
            buffer2.extend(attrs)
            tag_backer = backerItem.div
            backerName = tag_backer.h5.get_text().strip()
            #print backerName
            backerID = re.match('/profile/(\S+)', backerItem.a['href']).group(1)
            backerLocation = ''
            tag_backerLocation = tag_backer.find('p', class_='location')
            if tag_backerLocation:
                backerLocation = (tag_backerLocation.get_text()).strip()
            i_backingNumber = 1
            tag_backing = tag_backer.find('p', class_='backings')
            if tag_backing:
                backingNumber = re.search('\d+', tag_backing.get_text()).group(0)
                i_backingNumber = (int)(str(backingNumber))+1
            buffer2.extend([backerName, backerID, backerLocation, i_backingNumber])
            writer.writerow(buffer2)

#-----------------------------------------------------
def analyzeUpdatesData(url, writer, attrs):
    pageCount = 0
    while True:
        pageCount += 1
        updateContent = readFromUrl(url+'?page='+str(pageCount))
        soup_updates = BeautifulSoup(updateContent)
        tag_posts = soup_updates.find('div', class_='grid_11')
        list_posts = tag_posts.find_all('div', class_='post')
        if len(list_posts) == 0:
            break
        for post in list_posts:
            buffer3 = [url]
            buffer3.extend(attrs)
            date = title = content = ''
            likes = '0'
            tag_date = post.find('time')
            if tag_date:
                date = re.match('(\d+-\d+-\d+)T.*', tag_date['datetime']).group(1)
            tag_title = post.find('h3', class_='title')
            if tag_title:
                title = tag_title.a.string
            tag_likes = post.find('data', {'itemprop': 'Post[post_likes]'})
            if tag_likes:
                if tag_likes.string:
                    likes = re.match('(\d+) .*', tag_likes.string).group(1)
            tag_content = post.find('div', class_='body')
            if tag_content:
                content = cleanString(tag_content.get_text().strip())
            if post.find('div', {'id':'for-backers'}):
                content = 'FOR BACKERS ONLY!'
            buffer3.extend([title, date, likes, content])
            writer.writerow(buffer3)
#end analyzeUpdatesData()

#---------------------------------------------------
def analyzeCommentsData(url, writer, attrs):
    commentsContent = readFromUrl(url)
    soup_comments = BeautifulSoup(commentsContent)
    tag_comments = soup_comments.find('ol', class_='comments')
    if tag_comments:
        list_comments = tag_comments.find_all('li', class_='comment')
    else:
        return
    for comment in list_comments:
        buffer4 = [url]
        buffer4.extend(attrs)
        commentator = commentatorID = date = content = ''
        tag_commentator = comment.find('a', class_='author')
        if tag_commentator:
            commentator = tag_commentator.string
            commentatorID = re.match('/profile/(\S+)', tag_commentator['href']).group(1)
        tag_date = comment.find('data', {'data-format': 'distance_date'})
        if tag_date:
            date = re.search('(\d+-\d+-\d+)T', tag_date['data-value']).group(1)
        tag_content = comment.find_all('p')
        for p in tag_content:
            #print p
            if p.get_text():
                content += p.get_text()
        content = cleanString(content)
        buffer4.extend([commentator, commentatorID, date, content])
        writer.writerow(buffer4)
#end analyzeCommentData

#-----------------------------------------------------
def analyzeRewardData(soup, writer, attrs):
    #******************************
    #Reward
    tag_reward = soup.find('ul', {'id':'what-you-get'})
    if tag_reward:
        reward_list = tag_reward.find_all('li', class_='NS-projects-reward')
        for reward_item in reward_list:
            buffer5 = []
            buffer5.extend(attrs)
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
                RDes = cleanString(RDes)
            tag_RDel = reward_item.find('time')
            if tag_RDel:
                RDel = tag_RDel.string
            buffer5.extend([RAmt, RBkr, RDes, RDel])
            writer.writerow(buffer5)
#end analyzeRewardData()

#-----------------------------------------------------
def analyzeFaqData(soup, writer, attrs):
    tag_faq = soup.find('ul', class_='faqs')
    if tag_faq:
        faq_list = tag_faq.find_all('li', class_='faq')
        for faq in faq_list:
            buffer6 = []
            buffer6.extend(attrs)
            question = answer = updateDate = updateClock = ''
            tag_question = faq.find('span', class_='question')
            if tag_question:
                question = tag_question.get_text()
            tag_answer = faq.find('div', class_='faq-answer')
            if tag_answer:
                answer = tag_answer.get_text()
                answer = cleanString(answer)
            tag_time = faq.find('time', class_='js-adjust')
            if tag_time:
                updateDate = re.search('(\d+-\d+-\d+)T', tag_time['datetime']).group(1)
                updateClock = re.search('T(\d+:\d+:\d+)-', tag_time['datetime']).group(1)
            buffer6.extend([question, answer, updateDate, updateClock])
            writer.writerow(buffer6)
#end analyzeFaqData
