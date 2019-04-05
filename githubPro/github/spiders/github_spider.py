#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import scrapy
from githubPro.github.items import GithubItem

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('monitor')
logger.setLevel(logging.INFO)

fh = logging.FileHandler('monitor.log')
fh.setLevel(logging.INFO)

fh.setFormatter(formatter)
logger.addHandler(fh)


class githubPro(scrapy.Spider):

    name = "githubPro"

    def __init__(self):
        self.count = 1

    def start_requests(self):
        _url = 'https://github.com/search?p={page}&q=java&type=Repositories'
        # _url = 'https://stackoverflow.com/questions?page={page}&sort=votes&pagesize=50'
        # 100页数据，每页10条
        urls = [_url.format(page=page) for page in range(1, 101)]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=False)   # dont_filter=False去重

    def parse(self, response):
        # 每页只有10条数据
        for index in range(1, 11):
            self.count += 1
            if self.count % 100 == 0:
                logger.info(self.count)

            sel = response.xpath('//*[@id="js-pjax-container"]/div/div[3]/div/ul/li[{index}]'.format(index=index))
            item = GithubItem()
            title_sel = response.xpath('//*[@id="js-pjax-container"]/div/div[3]/div/ul/li[{index}]/div[1]/h3/a'.format(index=index))
            #item['title'] = "".join(
            #    sel.xpath('//*[@id="js-pjax-container"]/div/div[3]/div/ul/li[{index}]/div[1]/h3/a/text()'.format(index=index)).extract())
            item['title'] = title_sel.xpath('string(.)').extract()
            item['star'] = "".join(sel.xpath(
                '//*[@id="js-pjax-container"]/div/div[3]/div/ul/li[{index}]/div[2]/div[2]/a/text()'.format(index=index)).extract()[1])
            item['tag'] = sel.xpath('//*[@id="js-pjax-container"]/div/div[3]/div/ul/li[{index}]/div[2]/div[1]/text()'.format(index=index)).extract()
            item['des'] = "".join(
                sel.xpath('//*[@id="js-pjax-container"]/div/div[3]/div/ul/li[{index}]/div[1]/p/text()'.format(index=index)).xpath('string(.)').extract())
            item['update_date'] = sel.xpath(
                '//*[@id="js-pjax-container"]/div/div[3]/div/ul/li[{index}]/div[1]/div[2]/p/relative-time/text()'.format(index=index)).extract()
            '''
            print(item['title'])
            print(item['star'])
            print(item['tag'])
            print(item['des'])
            print(item['update_date'])
            print('++++++++++++++++')
            '''
            # 进入该话题网页url
            url = 'https://github.com'\
                  + sel.xpath('//*[@id="js-pjax-container"]/div/div[3]/div/ul/li[{index}]/div[1]/h3/a/@href'.format(index=index)).extract()[0]
            # 请求下一层网页
            yield scrapy.Request(url, meta={'item': item}, callback=self.parse_s, dont_filter=False)  # 请求第二个parse

    @staticmethod
    def parse_s(response):
        item = response.meta['item']
        s_sel = response.xpath('//*[@id="js-repo-pjax-container"]/div[2]/div[1]')
        print(''.join(item['tag']) + '---------------')
        if ''.join(item['tag']):
            item['author'] = s_sel.xpath(
                '//*[@id="js-repo-pjax-container"]/div[2]/div[1]/div[6]/div[2]/a[1]/text()').extract()
        else:
            item['author'] = s_sel.xpath(
                '//*[@id="js-repo-pjax-container"]/div[2]/div[1]/div[5]/div[2]/a[1]/text()').extract()
        yield item