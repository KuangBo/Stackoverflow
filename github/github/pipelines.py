# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi

import pymysql
import pymysql.cursors


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
              "author, title, star, des, tag, update_date) " \
              "values(%s, %s, %s, %s, %s, %s)"
        self.cursor.execute(insert_sql,
                            (item['author'], item['title'], item['star'],
                             item['des'], item['tag'],
                             "Updated ".join(item['update_date'])))
        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()


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
