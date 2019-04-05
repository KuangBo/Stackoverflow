# -*- coding=utf8 -*-
from scrapy import cmdline


# cmdline.execute("scrapy crawl githubPro -L WARNING".split())  # 不打印Debug信息
cmdline.execute("scrapy crawl github".split())
