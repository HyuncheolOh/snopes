import scrapy

from snopes.items import SnopesItem
from snopes.items import ArticleItem

class MmlabSpider(scrapy.Spider):
    name = "snopes_category"
    allowed_domains = ["snopes.com"]
    max_news_num = 10
    start_urls = ["https://www.snopes.com/fact-check"
            ]
    
    def data_processing(self, data_type, data_list):
        if data_type=="category":
            category_list = []
            for i in range(self.max_news_num):
                category_list.append((data_list[i].replace('<div class="breadcrumbs">',"").replace('<i class="fa fa-angle-right"></i>','_').replace('</div>', '')).strip())
            return category_list
        elif data_type=="description":
            desc_list = []
            for i in range(0, self.max_news_num * 2, 2):
                desc_list.append(data_list[i+1].strip())
            return desc_list
        elif data_type=="post_id":
            id_list = []
            for i in range(self.max_news_num):
                _ids = data_list[i].split()
                id_idx = 0
                for word in _ids:
                    if "post-" in word:
                        id_list.append(word.split('-')[-1])
                        break
            return id_list
        else: 
            return data_list[0:10]


    def parse(self, response):
        item = SnopesItem()
        item['post_id'] = self.data_processing("post_id", response.xpath('//article//a/@class').extract())
        item['category'] = self.data_processing("category", response.xpath('//article//div[@class="article-link-container"]//div[@class="breadcrumbs"]').extract())
        for info in zip(item['category'], item['post_id']):
            scraped_info = {
                    'category' : info[0],
                    'post_id' : info[1],
                    }
            #recursive page request
            yield scraped_info

        next_page = response.xpath('//div[contains(@class, "pagination-inner-wrapper")]//a[contains(., "Next")]/@href').extract_first()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)


