# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TruthorfictionItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    postid = scrapy.Field()
    title = scrapy.Field()
    claim = scrapy.Field()
    url = scrapy.Field()
    veracity = scrapy.Field()
    date = scrapy.Field()
    source = scrapy.Field()
    category = scrapy.Field()
