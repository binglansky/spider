# -*-coding:utf8-*-
import urllib2,urllib
from pymongo import MongoClient
import json
import threading
import logging,sys
import Queue


class reboot():
    def __init__(self):
        logger = logging.getLogger("AppName")
        formatter = logging.Formatter('%(asctime)s %(levelname)-5s: %(message)s')
        file_handler = logging.FileHandler("future.log")
        file_handler.setFormatter(formatter)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.formatter = formatter
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)
        self.logger = logger

        conn = MongoClient('127.0.0.1',27017)
        db = conn.test
        self.future = db.future
        self.count = []
        self.q = Queue.Queue()

        
    def insertdb(self,thread):
        while True:
            data = self.q.get()
            if not self.future.find_one({'id': data['id']}):
                self.future.insert(data)
                self.logger.info(u"已经插入数据" + data['id'])
            else:
                self.logger.info(u"已经存在" + data['id'])
        

    def main(self, thread):
        while True:
            self.logger.info(u"第%s次请求" %len(self.count))
            url = "http://paywhere.fast.im/index.php/home/Future/show_envelope"
            headers = {
                'User-Agent':'toFuture/40 CFNetwork/811.5.4 Darwin/16.6.0',
                'Host':'paywhere.fast.im'
                }
            formdata = {'imei':'d74521b6001e4510'}
            data = urllib.urlencode(formdata)
            try:
                request = urllib2.Request(url, data=data, headers = headers)
                html = urllib2.urlopen(request).read().replace('﻿', '')
            except urllib2.URLError:
                continue
            result = json.loads(html)
            for x in result['data']:
                self.q.put(x)
                   
            self.count.append(1)

if __name__ == '__main__':
    test = reboot()
    for x in range(10):
        t = threading.Thread(target=test.main, args=(x,))
        t.start()
    
    for y in range(10):
        t2 = threading.Thread(target=test.insertdb, args=(y,))
        t2.start()
    
    

