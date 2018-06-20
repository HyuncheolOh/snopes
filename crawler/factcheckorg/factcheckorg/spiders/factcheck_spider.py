import scrapy
from factcheckorg.items import FactcheckorgItem

#from factcheck.items import FactcheckItem

class FactCheckSpider(scrapy.Spider):
    name = "factcheckorg"

    def start_requests(self):
        urls = [
                "https://www.factcheck.org/featured-posts/",
                "https://www.factcheck.org/scicheck/",
                "https://www.factcheck.org/the-factcheck-wire/"
                ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        item = FactcheckorgItem()

        #print(self.list_strip(response.xpath('//div[@class="entry-meta"]').extract()))
        item['title'] = response.xpath('//div[@class="col-12 col-sm-4"]//a/@aria-label').extract()
        item['url']= response.xpath('//div[@class="col-12 col-sm-4"]//a/@href').extract()
        item['date'] = self.list_strip(response.xpath('//div[@class="entry-meta"]//text()').extract())
        item['claim'] = response.xpath('//div[@class="col-12 col-sm-8"]//div[@class="entry-content"]/p/text()').extract()
        for info in zip(item['title'], item['url'], item['date'], item['claim']):
            scraped_info = {
                    'title' : info[0],
                    'url' : info[1],
                    'date' : info[2],
                    'claim' : info[3]
                    }
            yield response.follow(info[1], callback=self.parse_veracity, meta={'item':scraped_info})

        next_page = response.xpath('//li[@class="page-item page-item-direction page-item-next"]//span//a/@href').extract_first() 
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)


    def parse_veracity(self, response):
        item = response.meta['item']
        #claim???
        item['postid'] = response.xpath('//link[@rel="shortlink"]/@href').extract_first().split('?p=')[1]
        item['source'] = 'factcheck.org'
        rating_image = response.xpath('//img[contains(@src, "rating_images")]/@src').extract_first()
        if rating_image != None:
            #parse image name
            image_name = rating_image.split('/')[-1]
            image_name = image_name.replace('.png', '')
            item['veracity'] = image_name
            yield item

    def list_strip(self, list_data):
        return [x.strip() for x in list_data]
