# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SnopesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    post_id = scrapy.Field()
    url = scrapy.Field()
    image = scrapy.Field()
    category  = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    published_date = scrapy.Field()
    modified_date = scrapy.Field()
    veracity = scrapy.Field()
    share_count = scrapy.Field()
    fact_checker = scrapy.Field()
    claim = scrapy.Field()
    tag = scrapy.Field()
    source = scrapy.Field()
    detailed_description = scrapy.Field()


class ArticleItem(scrapy.Item):
    veracity = scrapy.Field()
    title = scrapy.Field()
    claim = scrapy.Field()
    fact_checker = scrapy.Field()
    published_date = scrapy.Field()
    post_id = scrapy.Field()
