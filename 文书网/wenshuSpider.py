#!/usr/bin/env python
# encoding: utf-8
# @software: PyCharm
# @time: 2019/5/27 10:12
# @author: Paulson●Wier
# @file: wenshuSpider.py
# @desc:
import js2py
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import warnings
warnings.filterwarnings('ignore')


class WenshuSpider(object):

    def __init__(self):
        self.url_res = "http://wenshu.court.gov.cn/List/ListContent"
        self.url = 'http://wenshu.court.gov.cn/'
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        self.headers={
            "Host": "wenshu.court.gov.cn",
            "Origin": "http://wenshu.court.gov.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
            "Referer": "http://wenshu.court.gov.cn/",
            # "Referer":"http://wenshu.court.gov.cn/List/List?sorttype=1&conditions=searchWord+1+AJLX++%E6%A1%88%E4%BB%B6%E7%B1%BB%E5%9E%8B:%E5%88%91%E4%BA%8B%E6%A1%88%E4%BB%B6",
            "X-Requested-With":"XMLHttpRequest"
        }
        self.data = {
            "Param": "案件类型:刑事案件",
            "Index": 1,
            "Page": 10,
            "Order": "法院层级",
            "Direction": "asc",
            "vl5x": "",  # 可变参数，重点关注
            "number": "wens",
            "guid": "",  # 可变参数，重点关注
        }
        self.cookie = dict()

    def get_cookie(self):
        self.driver.get(self.url)
        self.driver.get("http://wenshu.court.gov.cn/List/List")
        self.driver.get(
            'http://wenshu.court.gov.cn/List/List?sorttype=1&conditions=searchWord'
            '+1+AJLX++%E6%A1%88%E4%BB%B6%E7%B1%BB%E5%9E%8B:%E5%88%91%E4%BA%8B%E6%A1%88%E4%BB%B6')
        self.driver.get(
            'http://wenshu.court.gov.cn/List/List?sorttype=1&conditions=searchWord'
            '+1+AJLX++%E6%A1%88%E4%BB%B6%E7%B1%BB%E5%9E%8B:%E5%88%91%E4%BA%8B%E6%A1%88%E4%BB%B6')
        cookies = self.driver.get_cookies()
        wzws_cid = self.driver.get_cookie('wzws_cid')['value']
        vjkl5 = self.driver.get_cookie('vjkl5')['value']
        # cookie_dict = dict()
        for cookie in cookies:
            self.cookie[cookie['name']] = cookie['value']
        return wzws_cid, vjkl5

    def get_vl5x_and_guid(self, vjkl5):
        """
        读取js文件并执行
        :return: vl5x, guid
        """
        with open('vl5x.js', 'r', encoding='utf-8') as f:
            js_content = f.read()
        with open('md5.js', 'r', encoding='utf-8') as f:
            js_md5 = f.read()
        with open('sha1.js', 'r', encoding='utf-8') as f:
            js_sha1 = f.read()
        with open('Base64.js', 'r', encoding='utf-8') as f:
            js_base64 = f.read()
        with open('guid.js', 'r', encoding='utf-8') as f:
            js_guid = f.read()

        context = js2py.EvalJs()
        context.execute(js_md5)
        context.execute(js_sha1)
        context.execute(js_base64)
        context.vjkl5 = vjkl5
        context.execute(js_content)
        context.execute(js_guid)

        return context.result, context.guid

    def get_wenshu_list_page(self):
        s = requests.Session()
        resp = s.post(url=self.url_res, headers=self.headers, data=self.data, cookies=self.cookie, allow_redirects=False,
            timeout=20)
        print(resp.text)

    def run(self):
        wzws_cid, vjkl5 = self.get_cookie()
        print(vjkl5)
        vl5x, guid = self.get_vl5x_and_guid(vjkl5)
        print(vl5x, guid)

        self.cookie['wzws_cid'] = wzws_cid
        self.cookie['vjkl5'] = vjkl5

        self.data['vl5x'] = vl5x
        self.data['guid'] = guid

        print(self.data)
        print(self.cookie)
        self.get_wenshu_list_page()



if __name__ == '__main__':
    w = WenshuSpider()
    w.run()

