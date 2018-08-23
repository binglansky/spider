# -*-coding:utf8-*-
# author : Corleone
# time: 2018.08.23
import requests
import json,sys,time
import Queue
import threading
import logging
from pymongo import MongoClient

class baihe():
    def __init__(self):
        # 日志
        logger = logging.getLogger("AppName")
        formatter = logging.Formatter('%(asctime)s %(levelname)-5s: %(message)s')
        file_handler = logging.FileHandler("baihe.log")
        file_handler.setFormatter(formatter)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.formatter = formatter
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
            'Referer': 'http://search.baihe.com/',
            'Origin': 'http://search.baihe.com',
            'Content-Type': 'application/x-www-form-urlencoded',
	    'Cookie': 'Your baihe cookie '
        }
        conn = MongoClient('192.168.51.160', 27017)
        db = conn.test
        baihe = db.baihe
        self.baihe = baihe

        self.headers = headers
        self.logger = logger
        # ID队列
        self.all_id = Queue.Queue()
        # 页面队列
        self.all_page = Queue.Queue()

    def getuserid(self, all_page, x, city):
        while True:
            page = all_page.get()
            self.logger.info("Thread-%s start get %s" %(x,page))
            url = "http://search.baihe.com/Search/getUserID"
            params = 'minAge=18&maxAge=30&minHeight=150&maxHeight=180&education=1-8&loveType=&marriage=&income=1-12&nationality=&occupation=&children=&bloodType=&constellation=&religion=&online=&isPayUser=&isCreditedByAuth=&hasPhoto=1&housing=&car=&homeDistrict=&sorterField=1&page=%s&city=%s' % (page, city)
            try:
                res = requests.post(url,data=params,headers=self.headers)
            except requests.exceptions.ConnectionError:
                time.sleep(30)
                res = requests.post(url, data=params, headers=self.headers)
            try:
                result = json.loads(res.text)
            except ValueError:
                all_page.task_done()
                continue
            for id in result['data']:
                self.all_id.put(id)
            all_page.task_done()

    def getinfo(self,all_id):
        while True:
            id = all_id.get()
            url = "http://search.baihe.com/search/getUserList?userIDs=" + str(id)
            try:
                res = requests.get(url,headers=self.headers)
            except requests.exceptions.ConnectionError:
                time.sleep(30)
                try:
                    res = requests.get(url, headers=self.headers)
                except requests.exceptions.ConnectionError:
                    all_id.task_done()
                    continue

            try:
                result = json.loads(res.text)
            except ValueError:
                all_id.task_done()
                continue
            try:
                self.logger.info(str(result['data'][0]['userID']) + " " + result['data'][0]['nickname'] + " " + str(result['data'][0]['age']) + " " + result['data'][0]['cityChn'] + " " + result['data'][0]['educationChn'] + " " + str(result['data'][0]['height']) + " " + result['data'][0]['incomeChn'] + " " + result['data'][0]['marriageChn'] + " " + str(result['data'][0]['photoList']))
            except IndexError:
                all_id.task_done()
                continue

            self.baihe.insert(result)

            all_id.task_done()

    def main(self):
        allcity = [ 8611, 8612, 8613, 8614, 8615, 8621, 8622, 8623, 8631, 8632, 8633, 8634, 8635, 8636, 8637, 8641, 8642, 8643, 8644, 8645, 8646, 8650, 8651, 8652, 8653,8654, 8661, 8662, 8663, 8664, 8665, 8671, 8681, 8682]
        for city in allcity:
            self.logger.info(u"开始捕捉%s地区妹子" %city)
            threads = 5
            # 所有页面
            for page in range(1, 70):
                self.all_page.put(page)
            # 多线程获取ID
            for x in range(threads):
                t = threading.Thread(target=self.getuserid, args=(self.all_page, x,city))
                t.setDaemon(True)
                t.start()

            self.all_page.join()
            # 多线程获取信息
            self.logger.info(u"一共捕获到%s个妹子" % self.all_id.qsize())
            self.logger.info(u"下面开始获取妹子详细信息")
            for y in range(threads):
                t = threading.Thread(target=self.getinfo, args=(self.all_id, ))
                t.setDaemon(True)
                t.start()

            self.all_id.join()
            self.logger.info(u"%s地区妹子捕捉完毕！" % city)

if __name__ == '__main__':
    robot = baihe()
    robot.main()




