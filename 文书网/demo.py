#!/usr/bin/env python
# encoding: utf-8
# @software: PyCharm
# @time: 2019/5/23 16:50
# @author: Paulson●Wier
# @file: demo.py
# @desc:
import execjs
import js2py

with open('vl5x.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

with open('md5.js', 'r', encoding='utf-8') as f:
    js_md5 = f.read()

with open('sha1.js', 'r', encoding='utf-8') as f:
    js_sha1 = f.read()

with open('Base64.js', 'r', encoding='utf-8') as f:
    js_base64 = f.read()

with open('guid.js','r', encoding='utf-8') as f:
    js_guid = f.read()


context = js2py.EvalJs()
context.execute(js_md5)
context.execute(js_sha1)
context.execute(js_base64)
context.execute(js_content)
context.execute(js_guid)
#
print('vl5x:', context.result)
print('guid:', context.guid)