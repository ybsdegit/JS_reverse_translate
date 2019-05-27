#!/usr/bin/env python
# encoding: utf-8
# @software: PyCharm
# @time: 2019/5/27 9:52
# @author: Paulson●Wier
# @file: demo_cookie.py
# @desc:
import warnings
warnings.filterwarnings('ignore')
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.get('http://wenshu.court.gov.cn/')
driver.get('http://wenshu.court.gov.cn/List/List?sorttype=1&conditions=searchWord+1+AJLX++%E6%A1%88%E4%BB%B6%E7%B1%BB%E5%9E%8B:%E5%88%91%E4%BA%8B%E6%A1%88%E4%BB%B6')
cookies = driver.get_cookies()
print(type(cookies))

cookie_dict = dict()
for cookie in cookies:
    cookie_dict[cookie['name']] = cookie['value']

print('coolie')
print(cookie_dict)
wzws_cid = driver.get_cookie('wzws_cid')['value']
vjkl5 = driver.get_cookie('vjkl5')['value']
print('wzws_cid:',wzws_cid)
print('vjkl5:',vjkl5)
