#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

import urllib, urllib2, cookielib
import sys, string, time, os, re
import csv
from bs4 import BeautifulSoup
import socket

from tools_renrendai import *

#----------------------------
#main
if login():
	print('success')
else:
    print('failed!')
print('oh?')
