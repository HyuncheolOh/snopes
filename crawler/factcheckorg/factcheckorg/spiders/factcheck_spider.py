import scrapy

#from factcheck.items import FactcheckItem

class FactCheckSpider(scrapy.Spider):
    name = "factcheck"

    def start_requests(self):
        urls = [
                "https://www.factcheck.org/fake-news/"
                ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        page = response.url.split("/")[-1]
        text1 = response.xpath('//div[@class="entry-content"]')
        text2 = response.xpath('//div[@class="entry-content"]//p//text()').extract()
        for item in text1:
            #print(item)
            p_content = item.xpath('/p').extract()
            print(p_content)
        #remove Q: 
        text2 = [item[0] for item in text2]
        date = response.xpath('//div[@class="entry-meta"]/text()').extract()
        date = [item.rstrip() for item in date]
        verdict = ['False'] * len(date)
        for i in zip(text2, verdict, date):
            info = {
                    'text':i[0].strip(), 'verdict':i[1], 'date' : i[2].strip()
                    }
            yield info

        #next_page = response.xpath('//div[@class="pagination"]//span//a').extract_first()
        #next_page = response.xpath('//div[@class="pagination"]//span//a[contains(@title, "Next")]/@href').extract_first()
        next_page = response.xpath('//li[@class="page-item page-item-direction page-item-next"]//span//a/@href').extract_first()  
        #if next_page is not None:
#        if next_page is not None and '5' not in next_page:
            #yield response.follow(next_page, callback=self.parse)
        #yield text, verdict
