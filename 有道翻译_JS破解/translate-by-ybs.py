#!/usr/bin/env python
# encoding: utf-8
# @software: PyCharm
# @time: 2019/5/21 15:38
# @author: Paulson●Wier
# @file: translate-by-ybs.py
# @desc:
import random

import requests
import time
import hashlib


def md5_b(key):
    m = hashlib.md5()
    m.update(key.encode('utf-8'))
    return m.hexdigest()


def sign_b(key, salt):
    sign = 'fanyideskweb' + key + str(salt) + '@6f#X3=cCuncYssPsuRUE'
    return md5_b(sign)


def translate(key):
    url = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
    salt = str(int(time.time()*1000) + random.randint(0, 10))
    data = {
        "i": key,
        "from": "AUTO",
        "to": "AUTO",
        "smartresult": "dict",
        "client": "fanyideskweb",
        "ts": salt[:-1],
        "salt": salt,
        "sign": sign_b(key, salt),
        "bv": md5_b("5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"),
        "doctype": "json",
        "version": "2.1",
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_REALTIME',
        # 'typoResult': 'false'
    }

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        "Content-Length": "272",
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'OUTFOX_SEARCH_USER_ID=-995880639@10.168.8.64; JSESSIONID=aaa4S2JviOjAFe8LvizRw; '
                  'OUTFOX_SEARCH_USER_ID_NCOO=2146618943.795375; ___rl__test__cookies=1558425516486',
        'Host': 'fanyi.youdao.com',
        'Origin': 'http://fanyi.youdao.com',
        'Referer': 'http://fanyi.youdao.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                      ' (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    res = requests.post(url, data=data, headers=headers).json()
    # print(res)

    result = res['translateResult'][0][0]
    result_tgt = result['tgt']
    result_src = result['src']

    print(f"""‘{result_src}’\n‘{result_tgt}’""")

    try:
        print('\n其它翻译:\n'+''.join(res['smartResult']['entries']))
    except KeyError:
        pass


if __name__ == '__main__':
    # 1. 正常执行代码
    # translate("你可真是个小机灵鬼！")

    # 2. 命令行传入参数执行代码，不适合用于打包成exe执行
    # from sys import argv
    # print(len(argv))
    #
    # if len(argv) == 2:
    #     t_text = argv[1]
    #     translate(t_text)
    # elif len(argv) > 2:
    #     t_text = argv[1:]
    #     translate(' '.join(t_text))
    # else:
    #     print('请使用以下方式执行代码：\n python youdao_fanyi xxx')

    # 3. input 输入参数，打包后可以再黑框中输入参数
    while True:
        t_text = input("\n请输入待翻译的文本(from ybs):\n")
        translate(t_text)


