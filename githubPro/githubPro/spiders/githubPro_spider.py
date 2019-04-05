#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import scrapy
from githubPro.githubPro.items import GithubproItem


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

            sel = response.xpath('//*[@id="js-pjax-container"]/div/div[3]/div/ul/li[index]'.format(index=index))

            item = GithubproItem()
            item['title'] = "".join(
                sel.xpath('//*[@id="js-pjax-container"]/div/div[3]/div/ul/li[1]/div[1]/h3/a/text()').extract())
            item['star'] = sel.xpath(
                '//*[@id="js-pjax-container"]/div/div[3]/div/ul/li[1]/div[2]/div[2]/a/text()').extract()
            item['tag'] = "".join(
                sel.xpath('//*[@id="js-pjax-container"]/div/div[3]/div/ul/li[1]/div[2]/div[1]/text()').extract())
            item['des'] = "".join(
                sel.xpath('//*[@id="js-pjax-container"]/div/div[3]/div/ul/li[1]/div[1]/p/text()').extract())
            item['update_date'] = sel.xpath\
                ('//*[@id="js-pjax-container"]/div/div[3]/div/ul/li[1]/div[1]/div[2]/p/relative-time/text()').extract()

            # 进入该话题网页url
            url = 'https://stackoverflow.com' \
                   + sel.xpath('/html/body/div[4]/div[2]/div[1]/div[3]/div[1]/div[2]/h3/a/@href').extract()[0]
            # 请求下一层网页
            yield scrapy.Request(url, meta={'item': item}, callback=self.parse_s, dont_filter=False)  # 请求第二个parse

    def parse_s(self, response):
        item = response.meta['item']
        question_state_sel = response.xpath('/html/body/div[4]/div[2]/div/div[1]/div[3]/div[1]/div/div[2]/div[1]')
        if "".join(question_state_sel.extract()):
            item['question_state'] = question_state_sel.xpath('string(.)').extract()
        adopted_code_sel_flag = response.xpath(
            '/html/body/div[4]/div[2]/div/div[1]/div[3]/div[3]/div[2]/div/div[1]/div/div[2]/svg')
        adopted_code_sel = response.xpath(
            '/html/body/div[4]/div[2]/div/div[1]/div[3]/div[3]/div[2]/div/div[2]/div[1]//code')
        if "".join(adopted_code_sel_flag.extract()):
            if "".join(adopted_code_sel.extract()):
                item['adopted_code'] = adopted_code_sel.xpath('string(.)').extract()
        adopted_sel = response.xpath('/html/body/div[4]/div[2]/div/div[1]/div[3]/div[3]/div[2]/div/div[2]/div[1]')
        if "".join(adopted_code_sel_flag.extract()):
            item['adopted'] = adopted_sel.xpath('string(.)').extract()

        yield item
