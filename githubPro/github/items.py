# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GithubItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 作者
    author = scrapy.Field()
    # 标题
    title = scrapy.Field()
    # star数量
    star = scrapy.Field()
    # 项目描述
    des = scrapy.Field()
    # 标签
    tag = scrapy.Field()
    # 更新日期
    update_date = scrapy.Field()
    # 文件链接地址
    file_urls = scrapy.Field()
    # 文件
    files = scrapy.Field()
    pass
