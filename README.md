spider-m-sohu
=============

环境配置
============

1. 安装python, pip等python开发必备工具，此处yy你已经有了。

2. 安装scrapy爬虫小少侠

	`pip install scrapy`

   Debian环境下，如果遇到“error: command ‘gcc’ failed with exit status 1”错误，可以先执行apt-get install python-dev libxml2-dev libxslt-dev -y 后再pip install scrapy.

3. 然后，到官网下载redis，解压安装，略。

4. 接着，需要安装python的redis client：

	`pip install redis`

启动程序
==========

1. 到redis根目录下：

	src/redis-server

2. 然后稍等一下喝杯茶，等它说ready了再到spider-m-sohu根目录下运行：

	scrapy crawl sohu

   然后可以傻傻地盯着终端看信息也可以勾搭妹子去了。

   可以在根目录看到log文件，里面就是每次运行抓到的死链啦。另外lulu/spiders中附了一个我之前运行的log文件。

   若要定时执行可以参照cronjob.sh以及crontab文件。
   
BTW
==========

主要代码都在sohu_spider.py中。
