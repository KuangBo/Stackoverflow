# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GithubproItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
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
    pass
