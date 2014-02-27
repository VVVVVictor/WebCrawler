# -*- coding: utf-8 -*-

import urllib, urllib2, cookielib
import sys, string, time, os, re
import csv
from bs4 import BeautifulSoup
import socket

#For login
urlLogin = u'https://www.yooli.com/secure/newLogin.action'
urlIndex = u'http://www.yooli.com/'
nickName = u'victor1991'
password = u'wmf123456'
headers={'Referer':'https://www.yooli.com/secure/login/','User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36', 'Host':'www.yooli.com'}


def login():
	cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	urllib2.install_opener(opener)
	
	data = {'nickName':nickName, 'password':password, 'verifycode':'', 'chkboxautologin':'true'}
	postdata = urllib.urlencode(data)
	
	try:
		req = urllib2.Request(urlLogin, postdata, headers)
		result = urllib2.urlopen(req)
		result.close()
		
		req2 = urllib2.Request(urlIndex, headers = headers)
		result2 = urllib2.urlopen(req2)
		print result2.read()
		result2.close()
	except:
		print(u'[FAIL]Login failed. Please try again!')
		return False
	
	return True
	
#----------------------------
#main
if login():
	print('success')