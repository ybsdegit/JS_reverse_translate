#!/usr/bin/env python
# encoding: utf-8
# @software: PyCharm
# @time: 2019/5/23 19:30
# @author: Paulson●Wier
# @file: 参考.py
# @desc:

import json
import re
from pprint import pprint
import js2py
import requests
import time
from bs4 import BeautifulSoup


# 请求首页，获得第一个wzws_cid
resp = requests.get(
    url="http://wenshu.court.gov.cn/",
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
    },
    # proxies=proxies
)
print(resp.cookies)
wzws_cid = requests.utils.dict_from_cookiejar(resp.cookies)["wzws_cid"]
# print("wzws_cid:",wzws_cid)

# 抓取响应中的js代码
raw_func = re.findall(r'<script type="text/javascript">(.*)</script>',resp.text,re.DOTALL)[0]
# print(raw_func)

sub_text = '''aaa=p;return "'zifuchuan'"'''
courl_func = re.sub('return p',sub_text,raw_func)   # 把原文中的return p 替换
# print(courl_func)

context = js2py.EvalJs()
context.execute('var aaa') # 定义个变量获取函数的返回值
context.execute(courl_func) # 执行替换好的函数
unpacked_cofunc = context.aaa  # 拿到函数
# print(context.aaa)

code = re.findall(r'(.*)function HXXTTKKLLPPP5',context.aaa)[0]
# print(code)

context.execute(code)

js = '''
var cookieString = "";
var wzwstemplate_result = KTKY2RBD9NHPBCIHV9ZMEQQDARSLVFDU(template.toString());
console.log(cookieString)
var confirm = QWERTASDFGXYSF();
var wzwschallenge_result = KTKY2RBD9NHPBCIHV9ZMEQQDARSLVFDU(confirm.toString());
console.log(cookieString)
console.log(dynamicurl)
'''
context.execute(js)

new_cookies = {
    "wzws_cid":wzws_cid,
    "wzwstemplate":context.wzwstemplate_result,
    "wzwschallenge":context.wzwschallenge_result
}
# print("new_cookies:",new_cookies)

new_url = "http://wenshu.court.gov.cn" + context.dynamicurl
# print("new_url:",new_url)
resp = requests.get(
    url=new_url,
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        "Referer":"http://wenshu.court.gov.cn/"
    },
    cookies=new_cookies,
    allow_redirects=False,
    # proxies=proxies
)

wzws_cid = requests.utils.dict_from_cookiejar(resp.cookies)["wzws_cid"] #获得了新的cid
# print("wzws_cid 计算后的:",wzws_cid)

# 带着新的cid请求首页
session = requests.session()

resp = session.get(
    url="http://wenshu.court.gov.cn/",
    cookies = {
        "wzws_cid":wzws_cid
    },
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        "Referer":"http://wenshu.court.gov.cn/"
    },
    # proxies=proxies
)

# resp = session.post(
#     url="http://wenshu.court.gov.cn/Index/GetAllCountRefresh?refresh=",     # 获得首页标题
#     headers={
#         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
#         "Referer":"http://wenshu.court.gov.cn/",
#         "X-Requested-With":"XMLHttpRequest"
#     }
# )

# print(resp.text)
# print("*"*100)

time.sleep(0.1)

# 请求列表页setcookie
resp = requests.get(
    url="http://wenshu.court.gov.cn/List/List?sorttype=1&conditions=searchWord+1+AJLX++%E6%A1%88%E4%BB%B6%E7%B1%BB%E5%9E%8B:%E5%88%91%E4%BA%8B%E6%A1%88%E4%BB%B6",
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        "Referer":"http://wenshu.court.gov.cn/",
        "X-Requested-With":"XMLHttpRequest"
    },
    cookies={
        "wzws_cid": wzws_cid
    },
    # proxies=proxies

)
# 从cookie中获取生成加密参数需要的值
vjkl5 = requests.utils.dict_from_cookiejar(resp.cookies)["vjkl5"]
# print("vjkl5:",vjkl5)

# 生成加密字符串vl5x和guid
with open('第一个.js','r') as f:
    js_content = f.read()
with open('md5.js','r') as f:
    js_md5 = f.read()
with open('sha1.js','r') as f:
    js_sha1 = f.read()
with open('base64.js','r') as f:
    js_base64 = f.read()
with open('guid文件.js','r') as f:
    js_guid = f.read()

context = js2py.EvalJs()
context.execute(js_md5)
context.execute(js_sha1)
context.execute(js_base64)
context.vjkl5 = vjkl5
context.execute(js_content)
context.execute(js_guid)
# print('vl5x:',context.result)
# print('guid:',context.guid)

# 整理参数向列表页发送post请求
data = {
    "Param":"案件类型:刑事案件",
    "Index":"1",
    "Page":"10",
    "Order":"法院层级",
    "Direction":"asc",
    "vl5x":context.result,
    "number":"wens",
    "guid":context.guid
}
# print("data:",data)

resp = requests.post(
    url="http://wenshu.court.gov.cn/List/ListContent",
    data=data,
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        "Referer":"http://wenshu.court.gov.cn/List/List?sorttype=1&conditions=searchWord+1+AJLX++%E6%A1%88%E4%BB%B6%E7%B1%BB%E5%9E%8B:%E5%88%91%E4%BA%8B%E6%A1%88%E4%BB%B6",
        "X-Requested-With":"XMLHttpRequest"
    },
    cookies={
        "wzws_cid": wzws_cid,
        "vjkl5":vjkl5
    },
    # proxies=proxies
)

# 保存获取的列表数据
with open('list_data.txt','wb') as f:
    f.write(resp.content)

# 处理一下数据
context.data = resp.text
context.execute('datalist = eval(data)')

with open('Base_64.js','r',encoding='utf-8') as f:
    context.execute(f.read())
with open('rawdeflate.js','r',encoding='utf-8') as f:
    context.execute(f.read())

with open('pako.js','r',encoding='utf-8') as f:
    context.execute(f.read())

datalist = json.loads(context.datalist)
# print(datalist)
for row in datalist:
    # pprint(row)
    pass

# RunEval = datalist[0]["RunEval"]
# doc_id =''
# for item in datalist[2:]:
#     # print(item)
#     doc_id += item["文书ID"]
# # print(doc_id)
#
# data = {
#     'runEval': RunEval,
#     'docIds': doc_id
# }
#
# print(data)
#
# resp = requests.post(
#     url = 'http://wenku.jwzlai.com/common/decode/docId',
#     headers={
#             "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
#         },
#     data = data
#
# )
#
# print(resp.text)

# 破解情页
detail_url1 = 'http://wenshu.court.gov.cn/WZWSREL2NvbnRlbnQvY29udGVudD9Eb2NJRD0xM2Q0YzAxYS0wNzM0LTRlYzEtYmJhYy02NThmOGJiOGVjNjImS2V5V29yZD0='

resp = requests.get(
    url=detail_url1,
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    },
    cookies=new_cookies,
    allow_redirects=False,
    # proxies=proxies
)

# print(resp.cookies)
# print(resp.headers)
wzws_cid3 = requests.utils.dict_from_cookiejar(resp.cookies)["wzws_cid"]
location = resp.headers['Location']

print(wzws_cid3)
print(location)

DocID = re.search(r'/content/content\?DocID=(.*?)&KeyWord=',location).group(1)
print(DocID)

detail_url2 = 'http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID='+DocID
resp = requests.get(
    url=detail_url2,
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        "Referer": "http://wenshu.court.gov.cn/content/content?DocID={}&KeyWord=".format(DocID)
    },

    cookies={
        "wzws_cid": wzws_cid3
    },
    # proxies=proxies
)
# print(resp.text)

bbb = re.search(r'(.*)var jsonData',resp.text,re.DOTALL).group(1)

content_dict = re.search(r'JSON.stringify\((.*?\).*?)\)',bbb,re.DOTALL).group(1)
content_dict = json.loads(content_dict)
pprint(content_dict)

content_html = re.search(r'jsonHtmlData = (.*)\;',bbb,re.DOTALL).group(1)
content_html = json.loads(content_html)
html_raw = re.search(r'"Html":"(.*?)"',content_html,re.DOTALL).group(1)


soup = BeautifulSoup(html_raw,'lxml')
txt_list = soup.select('div')
for txt in txt_list:
    print(txt.get_text())
