#!/usr/bin/env python
# encoding: utf-8
# @software: PyCharm
# @time: 2019/5/23 15:07
# @author: Paulson●Wier
# @file: wenshu_js.py
# @desc:


import requests
import json
import execjs

url = "http://wenshu.court.gov.cn/List/ListContent"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
    "Cookie": "td_cookie=2755526039; td_cookie=2753170589; wzws_cid=a4620e173b15bbc5b35f9f7c83f4c911b9ce99a8502092c0d9f3d7e62f4f8e1d3382e3e142a2141912fcc7cb75730cd663ce4c46045163e4fdd63ffde61f2446; vjkl5=0af3992295ff78e31901d91809ab73d77cb0f58e; "
}
data = {
    "Param": "案件类型:刑事案件",
    "Index": 1,
    "Page": 10,
    "Order": "法院层级",
    "Direction": "asc",
    "vl5x": "1936ae6b8307718503920d5e",  # 可变参数，重点关注
    "number": "wens",
    "guid": "454981be-74fb-e807cac0-912c1411dd5c",  # 可变参数，重点关注
}

# res = requests.post(url, headers=headers, data=data)
# print(res.text)
