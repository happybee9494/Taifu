# -*- coding: utf-8 -*-
#!/usr/bin/env python2.7
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from builtins import print

from htmltreediff import diff
from bs4 import BeautifulSoup


import json
import scrapy
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider, Rule

#crawled_web_pages = {}
#r = 0 #used by TwitterMonitor.py


class TatesterPipeline(object):
    def __init__(self):
        self.ids_seen = set()


    # def process_item(self, item, spider):
    #     line = json.dumps(dict(item)) + ""
    #     print(line)#.replace('\n', ''))
    #     return item
    def close_spider(self, spider):
        #print(crawled_web_pages)
        # page1 = crawled_web_pages['https://mobile.twitter.com/settings'][0]
        # page2 = crawled_web_pages['https://mobile.twitter.com/account'][0]
        # page1_content = BeautifulSoup(page1, "html.parser")
        # page2_content = BeautifulSoup(page2, "html.parser")
        # html1 = page1_content.findAll('html', recursive=True)
        # html2 = page2_content.findAll('html', recursive=True)
        # html1String = ''
        # html2String = ''
        # for k in html1[0]:
        #     html1String = html1String + k.encode('ascii')
        # for k in html2[0]:
        #     html2String = html2String + k.encode('ascii')
        #
        # if html1String:
        #     try:
        #         print(diff(html1String, html2String, pretty=True))
        #         # print (diff(html1Line,html2Line , pretty=True))
        #     except NameError:
        #         print('exception')

        print('end !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
