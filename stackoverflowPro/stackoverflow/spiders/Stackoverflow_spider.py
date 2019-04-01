#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import scrapy
from stackoverflowPro.stackoverflow.items import StackoverflowItem


formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('monitor')
logger.setLevel(logging.INFO)

fh = logging.FileHandler('monitor.log')
fh.setLevel(logging.INFO)

fh.setFormatter(formatter)
logger.addHandler(fh)


class stackoverflow(scrapy.Spider):

    name = "stackoverflow"

    def __init__(self):
        self.count = 1

    def start_requests(self):
        _url = 'https://stackoverflow.com/questions?page={page}&sort=votes&pagesize=50'
        urls = [_url.format(page=page) for page in range(1, 100001)]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=False)   # dont_filter=False去重

    def parse(self, response):
        for index in range(1, 51):
            self.count += 1
            if self.count % 100 == 0:
                logger.info(self.count)

            sel = response.xpath('//*[@id="questions"]/div[{index}]'.format(index=index))
            item = StackoverflowItem()
            item['votes'] = sel.xpath(
                '/html/body/div[4]/div[2]/div[1]/div[3]/div[2]/div[1]/div[1]/div[1]/div/span/strong/text()').extract()
            item['answers'] = sel.xpath(
                '/html/body/div[4]/div[2]/div[1]/div[3]/div[2]/div[1]/div[1]/div[2]/strong/text()').extract()
            item['views'] = "".join(
                sel.xpath('/html/body/div[4]/div[2]/div[1]/div[3]/div[2]/div[1]/div[2]/@title').extract()).split()[0].replace(",", "")
            item['questions'] = sel.xpath('/html/body/div[4]/div[2]/div[1]/div[3]/div[2]/div[2]/h3/a/text()').extract()
            item['links'] = "".join(
                sel.xpath('/html/body/div[4]/div[2]/div[1]/div[3]/div[2]/div[2]/h3/a/@href').extract()).split("/")[2]
            item['tags'] = sel.xpath('/html/body/div[4]/div[2]/div[1]/div[3]/div[2]/div[2]/div[2]/a/text()').extract()

            # 进入该话题网页url
            url = 'https://stackoverflow.com' \
                   + sel.xpath('/html/body/div[4]/div[2]/div[1]/div[3]/div[1]/div[2]/h3/a/@href').extract()[0]
            # 请求下一层网页
            yield scrapy.Request(url, meta={'item': item}, callback=self.parse_s, dont_filter=False)  # 请求第二个parse
            '''
            item['votes'] = sel.xpath(
                'div[1]/div[2]/div[1]/div[1]/span/strong/text()').extract()
            item['answers'] = sel.xpath(
                'div[1]/div[2]/div[2]/strong/text()').extract()
            item['views'] = "".join(
                sel.xpath('div[1]/div[3]/@title').extract()).split()[0].replace(",", "")
            item['questions'] = sel.xpath('div[2]/h3/a/text()').extract()
            item['links'] = "".join(
                sel.xpath('div[2]/h3/a/@href').extract()).split("/")[2]
            item['tags'] = sel.xpath('div[2]/div[2]/a/text()').extract()
            '''

    def parse_s(self, response):
        item = response.meta['item']
        # new_sel = response.xpath('/html/body/div[4]/div[2]/div/div[1]')
        # print(response.body)
        # print(new_sel.extract())

        # 判断是否存在question_state、adopted_code、adopted，再进行爬取
        # 爬取问题陈述question_state
        question_state_sel = response.xpath('/html/body/div[4]/div[2]/div/div[1]/div[3]/div[1]/div/div[2]/div[1]')
        if "".join(question_state_sel.extract()):
            # 两种样式
            # item['question_state'] = "".join(question_state_sel.extract())
            item['question_state'] = question_state_sel.xpath('string(.)').extract()

        # 爬取被采纳回答中的代码adopted_code
        adopted_code_sel_flag = response.xpath(
            '/html/body/div[4]/div[2]/div/div[1]/div[3]/div[3]/div[2]/div/div[1]/div/div[2]/svg')
        adopted_code_sel = response.xpath(
            '/html/body/div[4]/div[2]/div/div[1]/div[3]/div[3]/div[2]/div/div[2]/div[1]//code')
        # print(adopted_sel.extract())
        if "".join(adopted_code_sel_flag.extract()):
            if "".join(adopted_code_sel.extract()):
                # 两种样式
                # item['adopted_code'] = adopted_code_sel.xpath('normalize-space(string(//*))').extract()
                # item['adopted_code'] = "".join(adopted_code_sel.extract())
                item['adopted_code'] = adopted_code_sel.xpath('string(.)').extract()
        # print(item['adopted_code'])

        # 爬取完整被采纳回答adopted
        adopted_sel = response.xpath('/html/body/div[4]/div[2]/div/div[1]/div[3]/div[3]/div[2]/div/div[2]/div[1]')
        if "".join(adopted_code_sel_flag.extract()):
            # 两种样式
            # item['adopted'] = adopted_sel.xpath('normalize-space(string(//*))').extract()
            # item['adopted'] = "".join(adopted_sel.extract())
            item['adopted'] = adopted_sel.xpath('string(.)').extract()

        yield item
