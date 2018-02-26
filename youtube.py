# -*-coding:utf-8-*-
# time: 2018.1.23
# author : Corleone
from bs4 import BeautifulSoup
import lxml
import Queue
import requests
import re,os,sys,random
import threading
import logging
import json,hashlib,urllib
from requests.exceptions import ConnectTimeout,ConnectionError,ReadTimeout,SSLError,MissingSchema,ChunkedEncodingError
import random

reload(sys)
sys.setdefaultencoding('gbk')

# 日志模块
logger = logging.getLogger("AppName")
formatter = logging.Formatter('%(asctime)s %(levelname)-5s: %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

q = Queue.Queue()   # url队列
page_q = Queue.Queue()  # 页面

def downlaod(q,x,path):
    urlhash = "https://weibomiaopai.com/"
    try:
        html = requests.get(urlhash).text
    except SSLError:
        logger.info(u"网络不稳定 正在重试")
        html = requests.get(urlhash).text
    reg = re.compile(r'var hash="(.*?)"', re.S)
    result = reg.findall(html)
    hash_v = result[0]
    while True:
        data = q.get()
        url, name = data[0], data[1].strip().replace("|", "")
        file = os.path.join(path, '%s' + ".mp4") % name
        api = "https://steakovercooked.com/api/video/?cached&hash=" + hash_v + "&video=" + url
        api2 = "https://helloacm.com/api/video/?cached&hash=" + hash_v + "&video=" + url
        try:
            res = requests.get(api)
            result = json.loads(res.text)
        except (ValueError,SSLError):
            try:
                res = requests.get(api2)
                result = json.loads(res.text)
            except (ValueError,SSLError):
                q.task_done()
                return False
        vurl = result['url']
        logger.info(u"正在下载：%s" %name)
        try:
            r = requests.get(vurl)
        except SSLError:
            r = requests.get(vurl)
        except MissingSchema:
            q.task_done()
            continue
        try:
            with open(file,'wb') as f:
                f.write(r.content)
        except IOError:
            name = u'好开心么么哒 %s' % random.randint(1,9999)
            file = os.path.join(path, '%s' + ".mp4") % name
            with open(file,'wb') as f:
                f.write(r.content)
        logger.info(u"下载完成：%s" %name)
        q.task_done()

def get_page(keyword,page_q):
    while True:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'
        }
        page = page_q.get()
        url = "https://www.youtube.com/results?sp=EgIIAg%253D%253D&search_query=" + keyword + "&page=" + str(page)
        try:
            html = requests.get(url, headers=headers).text
        except (ConnectTimeout,ConnectionError):
            print u"不能访问youtube 检查是否已翻墙"
            os._exit(0)
        reg = re.compile(r'"url":"/watch\?v=(.*?)","webPageType"', re.S)
        result = reg.findall(html)
        logger.info(u"第 %s 页" % page)
        for x in result:
            vurl = "https://www.youtube.com/watch?v=" + x
            try:
                res = requests.get(vurl).text
            except (ConnectionError,ChunkedEncodingError):
                logger.info(u"网络不稳定 正在重试")
                try:
                    res = requests.get(vurl).text
                except SSLError:
                    continue
            reg2 = re.compile(r"<title>(.*?)YouTube",re.S)
            name = reg2.findall(res)[0].replace("-","")
            if u'\u4e00' <= keyword <= u'\u9fff':
                q.put([vurl, name])
            else:
                # 调用金山词霸
                logger.info(u"正在翻译")
                url_js = "http://www.iciba.com/" + name
                html2 = requests.get(url_js).text
                soup = BeautifulSoup(html2, "lxml")
                try:
                    res2 = soup.select('.clearfix')[0].get_text()
                    title = res2.split("\n")[2]
                except IndexError:
                    title = u'好开心么么哒 %s' % random.randint(1, 9999)
                q.put([vurl, title])
        page_q.task_done()


def main():
    # 使用帮助
    keyword = raw_input(u"请输入关键字：").decode("gbk")
    threads = int(raw_input(u"请输入线程数量(建议1-10): "))
    # 判断目录
    path = 'D:\youtube\%s' % keyword
    if os.path.exists(path) == False:
        os.makedirs(path)
    # 解析网页
    logger.info(u"开始解析网页")
    for page in range(1,26):
        page_q.put(page)
    for y in range(threads):
        t = threading.Thread(target=get_page,args=(keyword,page_q))
        t.setDaemon(True)
        t.start()
    page_q.join()
    logger.info(u"共 %s 视频" % q.qsize())
    # 多线程下载
    logger.info(u"开始下载视频")
    for x in range(threads):
        t = threading.Thread(target=downlaod,args=(q,x,path))
        t.setDaemon(True)
        t.start()
    q.join()
    logger.info(u"全部视频下载完成！")

main()

