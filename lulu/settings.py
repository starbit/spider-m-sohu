# Scrapy settings for lulu project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'lulu'
LOG_LEVEL = 'INFO'

SPIDER_MODULES = ['lulu.spiders']
NEWSPIDER_MODULE = 'lulu.spiders'
'''
By default, Scrapy uses a LIFO queue for storing pending requests, which basically means that it crawls in DFO order. This order is more convenient in most cases. If you do want to crawl in true BFO order, you can do it by setting the following settings:
'''
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = 'scrapy.squeue.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeue.FifoMemoryQueue'

DOWNLOAD_DELAY = 0.01  # Determined by your network condition
CONCURRENT_REQUESTS = 256
CONCURRENT_REQUESTS_PER_DOMAIN = 256
DEPTH_LIMIT = 0
DOWNLOAD_TIMEOUT = 10  # Discard the request if it takes too long

DNSCACHE_ENABLED = True
COOKIES_ENABLED = False

ITEM_PIPELINES = ['lulu.pipelines.LuluPipeline',]

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'lulu (+http://www.yourdomain.com)'
