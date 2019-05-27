#!/usr/bin/env python
# encoding: utf-8
# @software: PyCharm
# @time: 2019/5/27 15:38
# @author: Paulson●Wier
# @file: new_wenshu.py
# @desc:
import re
import time

import execjs
import js2py
import requests
from 文书网.my_logger import logger

class NewWenshu(object):
    '''裁判文书网'''
    def __init__(self, page, case_type):
        self.case_type = case_type
        self.page = page
        self.log = logger()
        self.headers = {
            "Host": "wenshu.court.gov.cn",
            "Origin": "http://wenshu.court.gov.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
            "Referer": "http://wenshu.court.gov.cn/",
            # "Referer":"http://wenshu.court.gov.cn/List/List?sorttype=1&conditions=searchWord+1+AJLX++%E6%A1%88%E4%BB%B6%E7%B1%BB%E5%9E%8B:%E5%88%91%E4%BA%8B%E6%A1%88%E4%BB%B6",
            "X-Requested-With": "XMLHttpRequest"
        }


    def home_1(self):
        """
        首页第一次
        :return:
        """
        url = 'http://wenshu.court.gov.cn/'
        s = requests.Session()
        resp = s.get(
            url=url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",

            },
            # proxies=self.proxies,
            allow_redirects=False,
            timeout=20
        )
        html_js = resp.text

        try:
            dynamicurl = re.search('dynamicurl="(.*?)"', html_js).group(1)
            wzwsquestion = re.search('wzwsquestion="(.*?)"', html_js).group(1)
            wzwsfactor = re.search('wzwsfactor="(.*?)"', html_js).group(1)
            wzwsmethod = re.search('wzwsmethod="(.*?)"', html_js).group(1)
            wzwsparams = re.search('wzwsparams="(.*?)"', html_js).group(1)
        except:
            return None

        para_part = '''
                var dynamicurl="{}";var wzwsquestion="{}";var wzwsfactor="{}";var wzwsmethod="{}";var wzwsparams="{}";
                '''.format(dynamicurl, wzwsquestion, wzwsfactor, wzwsmethod, wzwsparams)

        with open('home_1.js', 'r', re.DOTALL) as f:
            js_code = f.read()
        js_code = para_part + js_code

        ctx = execjs.compile(js_code)
        wzwschallenge = ctx.call("wzwschallenge")

        next_url = 'http://wenshu.court.gov.cn' + dynamicurl + '?' + 'wzwschallenge=' + wzwschallenge
        print('next_url',next_url)
        wzws_cid = requests.utils.dict_from_cookiejar(resp.cookies).get("wzws_cid")
        return next_url, wzws_cid

    def home_2(self):
        """
        首页第二次
        :return:
        """
        box = self.home_1()
        if not box:
            return None
        next_url, wzws_cid = box
        print('next_url, wzws_cid \n',next_url, wzws_cid )

        url = next_url
        s = requests.Session()
        resp = s.get(
            url=url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
            },
            # proxies=self.proxies,
            allow_redirects=False,
            timeout=20,
            cookies={
                "wzws_cid": wzws_cid
            }
        )
        next_wzws_cid = requests.utils.dict_from_cookiejar(resp.cookies).get("wzws_cid")
        return next_wzws_cid

    def list_1(self):
        """
        列表页第一次
        :return:
        """
        box = self.home_2()
        if not box:
            return None
        next_wzws_cid = box

        url = "http://wenshu.court.gov.cn/List/List"
        s = requests.Session()
        resp = s.get(
            url=url,
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "Referer": "http://wenshu.court.gov.cn/",
                "DNT": "1",
                "Host": "wenshu.court.gov.cn",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
            },
            cookies={
                "wzws_cid": next_wzws_cid
            },
            # proxies=self.proxies,
            allow_redirects=False,
            timeout=20
        )

        vjkl5 = requests.utils.dict_from_cookiejar(resp.cookies).get("vjkl5")
        return vjkl5, next_wzws_cid

    def list_2(self):
        """
        列表页第二次
        :return:
        """
        box = self.list_1()
        if not box:
            return None
        vjkl5, next_wzws_cid = box
        print('vjkl5, next_wzws_cid\n',vjkl5, next_wzws_cid)
        box = self.get_vl5x_and_guid(vjkl5)

        if not box:
            return None
        vl5x, guid = box
        print('vl5x, guid\n',vl5x, guid)
        url = "http://wenshu.court.gov.cn/List/ListContent"

        data = {
            "Param": f"{self.case_type}",
            "Index": self.page,
            "Page": 10,
            "Order": "法院层级",
            "Direction": "asc",
            "vl5x": vl5x,  # 可变参数，重点关注
            "number": "wens",
            "guid": guid,  # 可变参数，重点关注
        }
        print(data)
        s = requests.Session()
        resp = s.post(
            url=url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
                "Referer": "http://wenshu.court.gov.cn/",
                "X-Requested-With": "XMLHttpRequest",
            },
            cookies={
                "wzws_cid": next_wzws_cid,
                "vjkl5": vjkl5
            },
            # proxies=self.proxies,
            allow_redirects=False,
            timeout=20,
            data=data
        )

        return resp.text


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




class StartSpider(object):
    """
    用来启动爬虫
    """

    def __init__(self):
        self.log = logger()

    def run(self, keyword):
        page = 1
        real_page_num = 1

        page_try_count = 0
        keyword_try_count = 0
        total_data_count = 200
        first_flag = 1

        while page <= 20:
            # 每个搜索条件只给20页，再多请求会给重复的或假数据

            if page > real_page_num:
                # 如果页数小于20页,请求完真实页数后停止
                break

            if page_try_count > 5:
                self.log.warning('开始出现连续异常！-- 等待2s')
                time.sleep(2)

            start_time = time.time()
            try:
                # self.log.info('第{}页，{}'.format(page, keyword))
                print('第{}页，{}'.format(page, keyword))
                obj = NewWenshu(page, keyword)
                data = obj.list_2()
                print('result:\n',data)
                page += 1

            except:
                raise

                pass



if __name__ == '__main__':
    start = StartSpider()
    start.run('案件类型:刑事案件')