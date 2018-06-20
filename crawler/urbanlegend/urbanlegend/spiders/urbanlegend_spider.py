import scrapy
import re 

from urbanlegend.items import UrbanlegendItem

#from factcheck.items import FactcheckItem

class UrbanlegendSpider(scrapy.Spider):
    name = "urbanlegend"

    def start_requests(self):
        urls = [
                "https://urbanlegends.about.com"
                ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        item = UrbanlegendItem()

        item['url'] = response.xpath('//li[contains(@class, "g-item block-list-item")]/a/@href').extract()

        #print(self.list_strip(response.xpath('//div[@class="entry-meta"]').extract()))
        for info in item['url']:
            yield response.follow(info, callback=self.parse_veracity, meta={'item':{"url": info}})

#        next_page = response.xpath('//li[@class="page-item page-item-direction page-item-next"]//span//a/@href').extract_first() 
#        if next_page is not None:
#            yield response.follow(next_page, callback=self.parse)


    def parse_veracity(self, response):
        item = response.meta['item']
        #claim???
        item['title'] = response.xpath('//div[@class="header-title"]/text()').extract_first()
        item['date'] = self.get_date(response.xpath('//div[@id="updated-label_1-0"]/text()').extract_first())
        item['claim'] = response.xpath('//div[@class="comp flex article-content"]/p/text()').extract_first()
        item['source'] = 'urbanlegend'
        item['postid'] = item['url'].split('-')[-1]
        rating = response.xpath('//div[@class="comp flex article-content"]/p').extract()
#        print(rating)
        rating = self.get_veracity(rating)
        if rating != None:
            item['veracity'] = rating
            yield item

    def get_date(self, date):
        if date != None:
            return date.replace("Updated ", "")

    def get_veracity(self, rating):
        for item in rating:
            if "Status:" in item:
                item = self.remove_tag(item)
                item = item.split("Status:")[1]
                item = item.replace(' ', '')
                #print(item)
                return item
    
    def remove_tag(self, content):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', content)
        cleanr = re.compile(' ?\([^)]+\)')
        cleantext = re.sub(cleanr, '', cleantext)
        return cleantext 


