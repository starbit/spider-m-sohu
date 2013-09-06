# -- coding: utf-8 --

# This spider is to crawl all the urls
# under http://m.sohu.com/
# Be free to ask any questions by sending email to
# 129.911@gmail.com
# @lulu

from scrapy.spider import BaseSpider
from scrapy import signals, linkextractor
from scrapy.xlib.pydispatch import dispatcher
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from hashlib import md5
from Queue import Queue
from datetime import datetime

import redis
import urllib2
import re
import threading


queue = Queue()  # For writing failed urls


class Consumer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.fobj = open('log', 'wb')  # To record failed urls

    def run(self):
        global queue
        
        while True:
            try:
                failed_url = queue.get()
                self.fobj.write(failed_url + '\n')
                self.fobj.flush()  # Manually flush buffer
            except:
                pass

    def __del__(self):
        self.fobj.close()


class SohuSpider(BaseSpider):
    name = "sohu"  # So you can run it simply by 'scrapy crawl sohu'
    allowed_domains = ["m.sohu.com"]  # Only follow pages under this

    start_urls = ['http://m.sohu.com/']  # Start crawling from this page
    
    success_httpstatus_list = [200, 301, 302]  # You can change the list

    def __init__(self):
        # Initial a redis client and start a thread for queue
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        c = Consumer()
        c.start()

    def parse(self, response):
        global queue
        
        # Check response status
        status = response.status
        if status not in self.success_httpstatus_list:
            item = "%s %s %s" % (datetime.now(), status, response.url)
            queue.put(item)  # Put it into failed url queue

        if isinstance(response, HtmlResponse):
            
            # Check for duplication, add new ones
            dest = self.generate_md5(response.body)
            if self.r.setnx(dest, ''):
                yield
            
            # Extract urls
            hxs = HtmlXPathSelector(response)
            urls = hxs.select('//a/@href').extract()
            
            # Send request for each url
            for url in urls:
                # Call another method to filter and normalize urls
                url = self.handle_url(response, url)
                if url:
                    yield Request(url)
                else:
                    yield

    def handle_url(self, response, url):
        global queue
        
        if not url:
            return False
        
        # Filter those with auto_display which cause refresh and parsing error
        elif 'auto_display' in url:
            return False
        else:
            # Change relative url to absolute url and normalize it
            url = urljoin_rfc(get_base_url(response), url).split('#')[0].strip()
            # A regular expression pattern to filter pages outside domain
            pattern  = re.compile(r'^http:\/\/\w*\.?m\.sohu\.com')
            match = pattern.match(url)
            if not match:
                return False

            # If the url is a resource, read status code instead of download
            if url.split('.')[-1] in linkextractor.IGNORED_EXTENSIONS:
                # IGNORED_EXTENSIONS contains formats like jpg, jpeg etc.
                try:
                    res = urllib2.urlopen(url)
                    res.close()
                
                except urllib2.HTTPError, error:  # HTTPError may be a 404 error
                    code = error.getcode()
                    if code not in self.success_httpstatus_list:
                        item = "%s %s %s" % (datetime.now(), code, url)
                        queue.put(item)
                except urllib2.URLError:  # URLError may be a dns error
                    pass
                except:
                    pass

                return False
                    
            
            # Check for duplication, add new ones
            dest = self.generate_md5(url)
            if self.r.setnx(dest, ''):
                return False
            else:
                return url
                    
    def generate_md5(self, item):
        # Generate md5 of url or html body, easy to store and check
        m = md5()
        m.update(item)
        dest = m.hexdigest()
        return dest

    def handle_spider_closed(spider, reason):
        # Do some stuff when spider closed
        global queue
        
        queue.put(0)  # Put an untrue item to close queue
        del(spider.r)  # Close redis client

    # Connect handle_spider_close method to the closed signal
    dispatcher.connect(handle_spider_closed, signals.spider_closed)
