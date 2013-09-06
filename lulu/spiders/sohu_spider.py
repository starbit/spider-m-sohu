# -- coding: utf-8 --

from scrapy.spider import BaseSpider
from scrapy import signals, linkextractor
from scrapy.xlib.pydispatch import dispatcher
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from hashlib import md5
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url
from Queue import Queue
from datetime import datetime
import redis, urllib2, re
import threading


queue = Queue()

class Consumer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.fobj = open('log', 'wb')

    def run(self):
        global queue
        while True:
            try:
                failed_url = queue.get()
                self.fobj.write(failed_url + '\n')
                self.fobj.flush()
            except:
                pass

    def __del__(self):
        self.fobj.close()


class SohuSpider(BaseSpider):
    name = "sohu"
    allowed_domains = ["m.sohu.com"]

    start_urls = [
    'http://m.sohu.com/',
    ]
    
    success_httpstatus_list = [200, 301, 302]# html response success codes

    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        c = Consumer()
        c.start()

    def parse(self, response):
        global queue
        if response.status  not in self.success_httpstatus_list:
            item = "%s %s %s" % (datetime.now(), response.status, response.url)
            queue.put(item)

            print item

        if isinstance(response, HtmlResponse):
            
            #generate md5 value of htmlbody, easy for both storing and checking
            m = md5()
            m.update(response.body)
            dest = m.hexdigest()
            
            #check for duplication, add new ones
            if self.r.setnx(dest, ''):
                yield

            hxs = HtmlXPathSelector(response)
            urls = hxs.select('//a/@href').extract()
                
            for url in urls:
                #call another method to filter and normalize urls
                url = self.handle_url(response, url)
                if url:
                    yield Request(url)
                else:
                    yield

    def handle_url(self, response, url):
        global queue
        if not url:
            return False
        elif 'auto_display' in url:#filter those with auto_display which cause refresh and parsing error
            return False
        else:
            pattern  = re.compile(r'^http:\/\/\w*\.?m\.sohu\.com')
            url = urljoin_rfc(get_base_url(response), url).split('#')[0].strip()
            match = pattern.match(url)
            if not match:
                return False
            if url.split('.')[-1] in linkextractor.IGNORED_EXTENSIONS:
                try:
                    res = urllib2.urlopen(url)#to save time, we just get html status instead of downloading the whole resource
                    res.close()
                
                except urllib2.HTTPError, error:
                    if error.getcode() not in self.success_httpstatus_list:
                        item = "%s %s %s" % (datetime.now(), error.getcode(), url)
                        queue.put(item)
                        print item

                return False
                    
            #generate md5 value of url, easy for both storing and checking
            m = md5()
            m.update(url)
            dest = m.hexdigest()
            
            #check for duplication, add new ones
            if self.r.setnx(dest, ''):
                return False
            else:
                return url


    def handle_spider_closed(spider, reason):
        global queue
        queue.put(0)
        del(spider.r)

    dispatcher.connect(handle_spider_closed, signals.spider_closed)

    def process_exception(self, response, exception ,spider):
        pass
