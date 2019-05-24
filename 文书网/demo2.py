#!/usr/bin/env python
# encoding: utf-8
# @software: PyCharm
# @time: 2019/5/24 17:18
# @author: Paulson●Wier
# @file: demo2.py
# @desc:
import re
import requests


# url = 'http://wenshu.court.gov.cn/List/List?sorttype=1&conditions=searchWord+1+AJLX++%E6%A1%88%E4%BB%B6%E7%B1%BB%E5%9E%8B:%E5%88%91%E4%BA%8B%E6%A1%88%E4%BB%B6'
url = 'http://wenshu.court.gov.cn/'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}
sy_s = requests.Session()
sy_response = sy_s.get(url, headers=headers)
print(sy_response.headers)

cookie_wzws_cid1 = str(sy_response.cookies)
print(cookie_wzws_cid1)
# print(r.text)

result = re.findall(r'^<Re.*Cookie (\w*)=(\w*)',cookie_wzws_cid1)
wzws_cid = result[0][0] + '=' + result[0][1]

print(wzws_cid)


# a9c892639771fa4071f3bf235612b861e59ddc1e7ebf4d1381a9d6226aeb0c0c 427807ea81dca9fe0d4b42bfc94ff15d6a53ce312a0a851c2c1aa5d2fa841f33e0d4b82d45e7a171b8281b292adf10bb92d5e22ba758db4ed61fb2d55105cea8
# 69485e709377aa1ea4a1958723976a91a3c0d620f3d75e07f46bdb75166e8bc8571a655e6ce0b72471da1742968e848670c780aab1177cc834cad040cf5d1d8d
# a9c892639771fa4071f3bf235612b861e59ddc1e7ebf4d1381a9d6226aeb0c0c 6683971cc433c1daa09f3404df833eeba5638ebb3a9b298cce9c9ddede49f006
# 405441167fe0cd71637b6dbabce8e2ae683abca74d41955d60e57e74d08ca699a59eb70adfbac5cc3f1ac304b34a9d2067a26f334ed3532151ba58b6d28b9782f73a1306ad030f21aa43d22d4c1639f7378af866c006e574884992702e7d4aa0

# a9c892639771fa4071f3bf235612b861e59ddc1e7ebf4d1381a9d6226aeb0c0c 427807ea81dca9fe0d4b42bfc94ff15d 332f62d95c1eab68f95b4437fb1b6a2f
# td_cookie=2860334187; td_cookie=2859516671; vjkl5=4f0995ffb7e94201d3188dddb82eae711b32cb4b;


# a9c892639771fa4071f3bf235612b861e59ddc1e7ebf4d1381a9d6226aeb0c0c 6683971cc433c1daa09f3404df833eebbad802a23453a2612d493fbd907e24ca
# vjkl5=4f0995ffb7e94201d3188dddb82eae711b32cb4b

# a9c892639771fa4071f3bf235612b861e59ddc1e7ebf4d1381a9d6226aeb0c0c 6683971cc433c1daa09f3404df833eebbad802a23453a2612d493fbd907e24ca
# a9c892639771fa4071f3bf235612b861e59ddc1e7ebf4d1381a9d6226aeb0c0c 427807ea81dca9fe0d4b42bfc94ff15d cdc434d766bae672c26543279d5ee82a7c1996b1dfaf9ad6cb56d5c47f6d6ed830962a8b75097bcd1a5be1a52e2518bd