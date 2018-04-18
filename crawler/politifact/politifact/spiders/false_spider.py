import scrapy

from politifact.items import PolitifactItem

class PolitifactSpider(scrapy.Spider):
    name = "politifact_false"

    def start_requests(self):
        urls = [
                "http://www.politifact.com/truth-o-meter/rulings/false/"
#                "http://www.politifact.com/truth-o-meter/rulings/true/"
                ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        item = PolitifactItem()
        page = response.url.split("/")[-1]
        #text = response.xpath('//div[@class="statement__body"]').extract()
        #text = response.xpath('//div[@class="statement__body"]//p').extract()
        text = response.xpath('//div[@class="statement__body"]//p[@class="statement__text"]/a/text()').extract()
        verdict = response.xpath('//div[@class="statement"]//div[@class="meter"]//a//img/@alt').extract()
        item['text'] = text
        item['verdict'] = verdict

        for i in zip(text, verdict):
            info = {
                    'text':i[0].strip(), 'verdict':i[1]
                    }
            yield info

        #next_page = response.xpath('//div[@class="pagination"]//span//a').extract_first()
        next_page = response.xpath('//div[@class="pagination"]//span//a[contains(@title, "Next")]/@href').extract_first()
        
        if next_page is not None:
        #if next_page is not None and '5' not in next_page:
            yield response.follow(next_page, callback=self.parse)
        #yield text, verdict
