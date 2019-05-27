import re
import time
import pymongo
import requests
import execjs
import threadpool
from wenshu_task.docid import getkey, decode_docid
from wenshu_task.my_logger import logger
from wenshu_task.redis_ip_pool import RedisPara
from wenshu_task.wenshu_method import ParseJs, ParseDetail, Para
from wenshu_task.wenshu_setting import ExceptionCollections, ThreadNum, MongoSetting

'''
文书网爬虫：http://wenshu.court.gov.cn/
'''

class NewWenshu(object):
    '''裁判文书网'''
    def __init__(self,page,case_type,get_ua, get_pr):
        self.ua = get_ua
        self.proxies = {'http': 'http://{}'.format(get_pr)}
        self.page = page
        self.case_type = case_type
        self.item = {}
        self.log = logger()
        self.data_count = 200
        self.order = "法院层级"
        self.direction = "asc"

    # 首页第一次
    def home_1(self):
        url = 'http://wenshu.court.gov.cn/'
        resp = requests.get(
            url=url,
            headers={
                "User-Agent": self.ua,
            },
            proxies=self.proxies,
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
        '''.format(dynamicurl,wzwsquestion,wzwsfactor,wzwsmethod,wzwsparams)

        with open('home_1.js','r',re.DOTALL) as f:
            js_code = f.read()
        js_code = para_part + js_code

        ctx = execjs.compile(js_code)
        wzwschallenge = ctx.call("wzwschallenge")

        next_url = 'http://wenshu.court.gov.cn' + dynamicurl + '?' + 'wzwschallenge=' + wzwschallenge
        wzws_cid = requests.utils.dict_from_cookiejar(resp.cookies).get("wzws_cid")
        return next_url,wzws_cid

    # 首页第二次
    def home_2(self):
        box = self.home_1()
        if not box:
            return None
        next_url, wzws_cid = box

        url = next_url
        resp = requests.get(
            url=url,
            headers={
                "User-Agent": self.ua,
            },
            proxies=self.proxies,
            allow_redirects=False,
            timeout=20,
            cookies ={
                "wzws_cid": wzws_cid
            }
        )
        next_wzws_cid = requests.utils.dict_from_cookiejar(resp.cookies).get("wzws_cid")
        return next_wzws_cid

    # 列表页第一次
    def list_1(self):
        box = self.home_2()
        if not box:
            return None
        next_wzws_cid = box

        url = "http://wenshu.court.gov.cn/List/List"
        resp = requests.get(
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

                "User-Agent": self.ua,
            },
            cookies={
                "wzws_cid": next_wzws_cid
            },
            proxies=self.proxies,
            allow_redirects=False,
            timeout=20
        )

        vjkl5 = requests.utils.dict_from_cookiejar(resp.cookies).get("vjkl5")
        return vjkl5, next_wzws_cid

    # 列表页第二次
    def list_2(self):
        box = self.list_1()
        if not box:
            return None
        vjkl5, next_wzws_cid = box

        parser = ParseJs()
        box = parser.get_key_para(vjkl5)
        if not box:
            return None
        vl5x, guid = box



        url = "http://wenshu.court.gov.cn/List/ListContent"
        data = {
            "Param": "{}".format(self.case_type),  # 搜索关键字
            "Index": "{}".format(self.page),  # 这里是页数
            "Page": "10",  # 这个不变
            "Order": "{}".format(self.order),    # 排序关键词
            "Direction": "{}",     # 排序方向
            "number": "wens",
            "vl5x": vl5x,
            "guid": guid
        }

        resp = requests.post(
            url=url,
            headers={
                "User-Agent": self.ua,
                "Referer": "http://wenshu.court.gov.cn/",
                "X-Requested-With": "XMLHttpRequest",
            },
            cookies={
                "wzws_cid": next_wzws_cid,
                "vjkl5": vjkl5
            },
            proxies=self.proxies,
            allow_redirects=False,
            timeout=20,
            data=data
        )
        return resp.text

    # 列表页解析
    def list_3(self):
        text = self.list_2()
        if not text:
            return None
        context = ParseDetail(text)
        datalist = context.parse_list_data()

        if not datalist:
            self.log.warning('没有获取列表数据')
            return None

        RunEval = datalist[0]['RunEval']
        key = getkey(RunEval)

        # 获取当前关键词数据总量
        if key:     # 判断一下key,如果是脏数据,不用来计算页数
            self.data_count = datalist[0]['Count']

        for case in datalist[1:]:
            parse_obj = ParseDetail(case)
            title, court, pdate, writ, reason, Docid = parse_obj.parse_items()

            docid = decode_docid(Docid, key)

            if not docid:
                self.log.warning('没有获取正确的docid')
                return None

            # 如果 docid 能在数据库中找到，不重复请求
            if self.search_data(docid):
                continue

            self.set_defult_data()
            self.item['title'] = title
            self.item['court'] = court
            self.item['pdate'] = pdate
            self.item['writ'] = writ
            self.item['reason'] = reason
            self.item['sid'] = docid
            self.item['src'] = 'http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID=' + docid
            self.item['category'] = self.case_type

            next_wzws_cid, detail_js = self.detail_1(docid)

            html_js = detail_js
            dynamicurl = re.search('dynamicurl="(.*?)"', html_js).group(1)
            wzwsquestion = re.search('wzwsquestion="(.*?)"', html_js).group(1)
            wzwsfactor = re.search('wzwsfactor="(.*?)"', html_js).group(1)
            wzwsmethod = re.search('wzwsmethod="(.*?)"', html_js).group(1)
            wzwsparams = re.search('wzwsparams="(.*?)"', html_js).group(1)

            para_part = '''
                   var dynamicurl="{}";var wzwsquestion="{}";var wzwsfactor="{}";var wzwsmethod="{}";var wzwsparams="{}";
                   '''.format(dynamicurl, wzwsquestion, wzwsfactor, wzwsmethod, wzwsparams)

            with open('home_1.js', 'r', re.DOTALL) as f:
                js_code = f.read()
            js_code = para_part + js_code

            ctx = execjs.compile(js_code)
            wzwschallenge = ctx.call("wzwschallenge")

            next_url = 'http://wenshu.court.gov.cn' + dynamicurl + '?' + 'wzwschallenge=' + wzwschallenge

            next_wzws_cid = self.detail_2(next_url,next_wzws_cid)

            detail_html = self.detail_3(next_wzws_cid,docid)
            if detail_html:
                context = ParseDetail(detail_html)
                html_raw = context.parse_detail()

                self.item['content'] = html_raw

                # 保存数据
                self.save_data(docid)

                time.sleep(0.2)
            else:
                self.log.warning('没有获取到值')

        return 'success'

    # 详情页第一次
    def detail_1(self, docid):
        url = 'http://wenshu.court.gov.cn/content/content?DocID={}&KeyWord='.format(docid)
        resp = requests.get(
            url=url,
            headers={
                "User-Agent": self.ua,
            },
            proxies=self.proxies,
            allow_redirects=False,
            timeout=20,
        )
        next_wzws_cid = requests.utils.dict_from_cookiejar(resp.cookies).get('wzws_cid')
        return next_wzws_cid,resp.text

    # 详情页第二次
    def detail_2(self,next_url, wzws_cid):
        url = next_url
        resp = requests.get(
            url=url,
            headers={
                "User-Agent": self.ua,
            },
            proxies=self.proxies,
            allow_redirects=False,
            timeout=20,
            cookies ={
                "wzws_cid": wzws_cid
            }
        )
        next_wzws_cid = requests.utils.dict_from_cookiejar(resp.cookies).get("wzws_cid")
        return next_wzws_cid

    # 详情页第三次
    def detail_3(self,next_wzws_cid,docid):
        url = 'http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID=' + docid

        resp = requests.get(
            url=url,
            headers={
                "User-Agent": self.ua,
                "X-Requested-With": "XMLHttpRequest",
            },
            proxies=self.proxies,
            allow_redirects=False,
            timeout=20,
            cookies={
                "wzws_cid": next_wzws_cid
            }
        )
        # 可能给返回这个 window.location.href='/Html_Pages/VisitRemind20180914.html?DocID=cb564602-23aa-46e3-abe3-841f59727e0f'
        if len(resp.text) < 150:
            self.log.warning('返回值异常')
            return None

        if "您的访问频次超出正常访问范围，为保障网站稳定运行，请输入验证码后继续查看" in resp.text:
            self.log.warning('需要验证码')
            return None

        return resp.text

    # 保存数据
    def save_data(self,docid):
        # 保存成功不显示，失败会打印异常
        pipline = WenshuPipeline(docid)
        succ_flag = pipline.save_item(self.item)
        if not succ_flag:
            # 如果sid已存在，会保存失败
            self.log.info('未保存成功，page--{},case_type--{},useragent--{}, proxies--{}'.format(self.page,self.case_type,self.ua, self.proxies))

    # 查询sid
    def search_data(self,sid):
        pipline = WenshuPipeline(sid)
        exist_flag = pipline.collection.find({"sid":sid}).count()
        return exist_flag

    # 设置默认item数据
    def set_defult_data(self):
        self.item['content'] = ''
        self.item['sid'] = ''
        self.item['src'] = ''
        self.item['category'] = ''
        self.item['title'] = ''
        self.item['court'] = ''
        self.item['pdate'] = ''
        self.item['writ'] = ''
        self.item['reason'] = ''
        self.item['sync'] = 0

class WenshuPipeline(object):
    """
    文书保存到数据库
    """
    def __init__(self,docid):
        '''
        数据库初始化配置
        '''
        self.client = pymongo.MongoClient(MongoSetting)
        self.db = self.client.spider
        data_base_num = self.generate_database_num(docid)
        collection_name = 'judicial_documents_' + str(data_base_num)
        command_str = 'self.db.{}'.format(collection_name)
        self.collection = eval(command_str)

    @staticmethod
    def str_wash(data):
        """
        传入用过字典，把里面值是字符串的清洗一下。返回字典
        :param data:
        :return:
        """
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = v.strip()
        return data

    def save_item(self, item):
        '''
        保存数据，如果sid相同不重复插入
        :param item:
        :return:
        '''
        sid = item['sid']
        dup_flage = self.collection.find_one({"sid": sid}, {"sid": 1})
        if not dup_flage:
            result = self.collection.insert_one(self.str_wash(dict(item)))
            self.client.close()
            return result

    def generate_database_num(self, docid):
        '''
        生成数据库编号
        参数 docid
        返回0-99的数字
        '''
        raw_docid = docid.replace('-', '')
        num_docide = int(raw_docid, 16)
        database_num = num_docide % 100

        return database_num

class GetKeywordList(object):
    '''
    获取所有关键词,除去已请求过的
    '''
    def __init__(self):
        self.client = pymongo.MongoClient(MongoSetting)
        self.db = self.client.spider

    def get_data(self):
        raw_data_list = []
        collection = self.db.wenshu_court1
        all_keyword_cursor = collection.find({'id': {'$gt': -1}})
        for keyword in all_keyword_cursor:
            name = keyword.get('name')
            type = keyword.get('type')
            raw_data_list.append(type + ':' + name)

        used_keyword_cursor = self.get_used_keyword()
        for ukeyword in used_keyword_cursor:
            uname = ukeyword.get('keyword')
            if uname in raw_data_list:
                raw_data_list.remove(uname)

        return raw_data_list

    def get_used_keyword(self):
        collection = self.db.wenshu_used_keyword
        used_keyword = collection.find()
        return used_keyword

class StartSpider(object):
    '''用来启动爬虫'''
    def __init__(self):
        self.get_ua = ''
        self.get_pr = ''
        self.log = logger()

    @staticmethod
    def set_used_keyword(keyword):
        '''
        记录用过的关键词
        :param keyword:
        :return:
        '''
        client = pymongo.MongoClient(MongoSetting)
        db = client.spider
        collection = db.wenshu_used_keyword

        dup_flage = collection.find_one({"keyword": keyword})
        if not dup_flage:
            # 如果不重复的话,保存
            result = collection.insert_one({"keyword": keyword})
            client.close()
            return result

    @staticmethod
    def set_failed_keyword(keyword):
        '''
        记录失败的关键词
        :param keyword:
        :return:
        '''
        client = pymongo.MongoClient(MongoSetting)
        db = client.spider
        collection = db.wenshu_failed_keyword

        dup_flage = collection.find_one({"keyword": keyword})
        if not dup_flage:
            # 如果不重复的话,保存
            result = collection.insert_one({"keyword": keyword})
            client.close()
            return result

    def run(self, keyword):
        '''
        运行爬虫
        :param keyword:
        :return:
        '''
        page = 1
        page_try_count = 0
        keyword_try_count = 0
        total_data_count = 200
        first_flag = 1
        real_page_num = 20

        while page <= 20:
            # 每个搜索条件只给20页，再多请求会给重复的或假数据

            if page > real_page_num:
                # 如果页数小于20页,请求完真实页数后停止
                break

            if page_try_count > 5:
                # 触发连续异常

                self.log.warning('开始出现连续异常！-- 等待2s')
                time.sleep(2)

                # 进行2秒等待后,把page_try_count清零,keyword_try_count加一
                page_try_count = 0
                keyword_try_count += 1

                # 如果一个关键词触发的连续异常次数大于等于20,放弃请求该关键词,保存到失败的关键词表
                if keyword_try_count >= 20:
                    self.set_failed_keyword(keyword)
                    self.log.warning('关键词"{}"请求失败,已保存失败关键词'.format(keyword))
                    return

            # 获取代理
            r = RedisPara()
            get_pr = r.get_random_ip()

            if not get_pr:
                self.log.error('代理ip为空')
                time.sleep(2)
                continue

            # 获取UA
            p = Para()
            get_ua = p.get_user_agent()

            self.log.info('当前参数：keyword-{},ua-{},prox-{},'.format(keyword, get_ua, get_pr))

            start_time = time.time()
            try:
                self.log.info('第{}页，{}'.format(page, keyword))
                obj = NewWenshu(page, keyword, get_ua, get_pr)
                sucess_flag = obj.list_3()
                total_data_count = int(obj.data_count)     # 获取该关键词下的数据总量
                if sucess_flag:
                    page += 1
                    page_try_count = 0
                else:
                    # 没有报错，但是没有给数据
                    raise requests.exceptions.ProxyError

            except ExceptionCollections as e:
                # 捕获指定异常
                page_try_count += 1
                self.log.error('连接失败,异常为:{}'.format(e))
            else:
                # 如果10条数据成功保存，执行这里
                self.log.info(' ---------------- 第{}页,{},采集完毕，用时{}秒 ----------------'.format(page-1, keyword, (time.time() - start_time)))

            if first_flag and total_data_count < 200:
                # 如果不到20页,计算出真实页数
                real_page_num = total_data_count // 10
                remainder = total_data_count % 10
                if remainder:
                    real_page_num += 1
                first_flag = 0

        # 如果当前关键词采集完毕,保存关键词
        self.set_used_keyword(keyword)
        self.log.info(' -------------- 关键词 "{}" 下数据采集完毕--------------'.format(keyword))

    def muti_task(self):
        '''实现多任务'''

        # 获取关键字列表
        keyword_obj = GetKeywordList()
        keyword_list = keyword_obj.get_data()

        # 设置线程池参数
        thread_num = ThreadNum
        pool = threadpool.ThreadPool(thread_num)
        self.log.info('当前线程数：{}'.format(thread_num))
        requests = threadpool.makeRequests(self.run, keyword_list)
        [pool.putRequest(req) for req in requests]
        pool.wait()


spider = StartSpider()
spider.muti_task()



