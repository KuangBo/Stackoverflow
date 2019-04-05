# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import re

from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi

import scrapy
import pymysql
import pymysql.cursors

from scrapy.pipelines.files import FilesPipeline
from urllib.parse import urlparse
from os.path import basename, dirname, join


class GithubPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlPipeline(object):
    # 采用同步的机制写入mysql
    def __init__(self):
        # 连接MySQL数据库
        # self.conn = pymysql.connect
        # ('127.0.0.1', 'root', 'root', 'developer_community', charset="utf8", use_unicode=True)
        self.conn = pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            passwd="root",
            db="developer_community",
            charset="utf8")
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        # 写入数据
        insert_sql = "insert ignore into github_info(" \
              "author, title, star, des, tag, update_date, file_urls) " \
              "values(%s, %s, %s, %s, %s, %s, %s)"
        self.cursor.execute(insert_sql,
                            ("".join(item['author']), "".join(item['title']), item['star'],
                             "".join(item['des']), " ".join(item['tag']),
                             "Updated ".join(item['update_date']),
                             item['file_urls']))
        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()


# 暂未使用
class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(clsc, setting):
        dbparms = dict(
            host=setting["MYSQL_HOST"],
            db=setting["MYSQL_DBNAME"],
            user=setting["MYSQL_USER"],
            password=setting["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return clsc(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)


class MyFilePipeline(FilesPipeline):
    # print('99999999999999')

    def get_media_requests(self, item, info):
        # print('0000000000000')
        for file_url in item["file_urls"]:
            yield scrapy.Request(file_url)

    def item_completed(self, results, item, info):
        # print('11111111111111')
        file_paths = [x["path"] for ok, x in results if ok]
        print(file_paths)
        if not file_paths:
            raise DropItem("Item contains no files")
        return item

    def file_path(self, request, response=None, info=None):
        # 对下载文件进行重命名
        # print('22222222222222')
        path = urlparse(request.url).path
        # print('6666666666' + path.replace('/', ''))
        return path.replace('/', '_')[1:]
        # return join(basename(dirname(path)), basename(path))
