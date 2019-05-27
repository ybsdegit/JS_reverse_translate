#!/usr/bin/env python
# encoding: utf-8
# @software: PyCharm
# @time: 2019/5/27 15:38
# @author: Paulson●Wier
# @file: new_wenshu.py
# @desc:
import base64
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

    # 计算生成第一次访问的连接
    def get_url_first(self, wzwsquestion, wzwsfactor, dynamicurl):
        try:
            nub_ = 0
            for question in wzwsquestion:
                nub_ += ord(question)
            nub_ *= int(wzwsfactor)
            nub_ = nub_ + 111111
            challenge = 'WZWS_CONFIRM_PREFIX_LABEL{}'.format(nub_)
            wzwschallenge = 'wzwschallenge={}'.format(str(base64.b64encode(challenge.encode('utf-8')), 'utf-8'))
            # print(wzwschallenge)
            result = '{}?{}'.format(dynamicurl, wzwschallenge)
            return result
        except:
            print('--Error:方法get_url_first--')
            # time.sleep(60)

    def get_vjkl5(self):
        timeout = 5
        while 1:
            # proxies = self.get_proxies()
            try:
                session = requests.session()
                url_1 = 'http://wenshu.court.gov.cn/List/List?sorttype=1&conditions=searchWord+1+AJLX++%E6%A1%88%E4%BB%B6%E7%B1%BB%E5%9E%8B:%E5%88%91%E4%BA%8B%E6%A1%88%E4%BB%B6'
                headers_1 = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
                    # "Referer": "http://wenshu.court.gov.cn/list/list/?sorttype=1&number=T9EYXNMW&guid=690587f5-b606-efd81bf9-71543b2db841&conditions=searchWord++CPRQ++%E8%A3%81%E5%88%A4%E6%97%A5%E6%9C%9F:2019-04-01%20TO%202019-04-01",
                    "Host": "wenshu.court.gov.cn",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "Origin": "http://wenshu.court.gov.cn",
                    # "X-Requested-With": "XMLHttpRequest",
                    # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",

                }
                response_1 = session.get(url=url_1,
                                         headers=headers_1,
                                         # proxies=proxies,
                                         timeout=timeout
                                         )
                html = response_1.text

                waws_cid = response_1.headers['Set-Cookie'].split(';')[0]

                dynamicurl = re.findall(r'dynamicurl="(.*?)";0', html, re.S)[0]
                wzwsquestion = re.findall(r'wzwsquestion="(.*?)";0', html, re.S)[0]
                wzwsfactor = re.findall(r'wzwsfactor="(.*?)";0', html, re.S)[0]

                result_1 = self.get_url_first(wzwsquestion, wzwsfactor, dynamicurl)
                url_2 = 'http://wenshu.court.gov.cn{}'.format(result_1)
                print(url_2)
                headers_1['Referer'] = url_1
                response_2 = session.get(url=url_2, headers=headers_1,
                                         # proxies=proxies,
                                         timeout=timeout)
                vjkl5 = response_2.headers['Set-Cookie'].split(';')[0]
                # print(response_2.text)
                # print('-------------------')
                # print(vjkl5)
                # print(waws_cid)
                # print('-------------------')
                if 'vjkl5' in vjkl5:
                    return vjkl5
                else:
                    print('--Error:获取vjl5x时出现问题，暂停10s--')
                    # time.sleep(1)

            except:
                print('--Error:get_vjkl5出现错误--')

    def list_2(self):
        """
        列表页第二次
        :return:
        """
        box = self.get_vjkl5()
        if not box:
            return None

        vjkl5 = box
        print('vjkl5, next_wzws_cid\n',vjkl5)

        box = self.get_vl5x_and_guid(vjkl5)

        if not box:
            return None
        vl5x, guid = box

        print('vl5x, guid\n',vl5x, guid)
        url = "http://wenshu.court.gov.cn/List/ListContent"

        headers_2 = {
                      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
                      "Referer": "http://wenshu.court.gov.cn/",
                      "X-Requested-With": "XMLHttpRequest",
                      "Cookie": vjkl5
                  }
        data = {
            "Param": f"{self.case_type}",
            "Index": self.page,
            "Page": 10,
            "Order": "法院层级",
            "Direction": "asc",
            "vl5x": vl5x,  # 可变参数，重点关注
            "number": "wens",
            "guid": guid  # 可变参数，重点关注
        }
        print(type(headers_2))
        print(data)
        s = requests.Session()
        resp = s.post(
            url=url,
            headers=headers_2,
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