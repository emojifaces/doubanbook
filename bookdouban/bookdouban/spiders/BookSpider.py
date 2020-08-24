import re

import scrapy
from ..configure import TAG
from urllib.parse import quote
from scrapy import Request
from ..items import BookdoubanItem


class BookspiderSpider(scrapy.Spider):
    name = 'BookSpider'
    allowed_domains = ['book.douban.com']
    base_url = 'https://book.douban.com/tag/%s'

    def start_requests(self):
        for tag in TAG:
            request_url = self.base_url % (quote(tag))
            yield Request(url=request_url, callback=self.parse)

        # url = self.base_url % (quote(TAG[0]))
        # yield Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        subject_item_list = response.xpath('//li[@class="subject-item"]')
        for subject_item in subject_item_list:
            book_item = BookdoubanItem()
            img_url_small = subject_item.xpath('.//div[@class="pic"]/a/img/@src').get()
            book_name_main = subject_item.xpath('.//div[@class="info"]/h2/a/text()').get()
            book_name_sub = subject_item.xpath('.//div[@class="info"]/h2/a/span/text()').get()
            star = subject_item.xpath('.//div[@class="info"]/div[@class="star clearfix"]/span[1]/@class').get()
            mark = subject_item.xpath('.//div[@class="info"]/div[@class="star clearfix"]/span[2]/text()').get()
            eval_num = subject_item.xpath('.//div[@class="info"]/div[@class="star clearfix"]/span[3]/text()').get()
            book_item['img_url_small'] = img_url_small
            book_item['book_name_main'] = book_name_main
            book_item['book_name_sub'] = book_name_sub
            book_item['star'] = star
            book_item['mark'] = mark
            book_item['eval_num'] = eval_num
            book_detail_url = subject_item.xpath('.//div[@class="info"]/h2/a/@href').get()

            yield Request(url=book_detail_url,
                          callback=lambda rsp, it=book_item: self.parse_book_detail(response=rsp, book_item=it))
        next = response.xpath('//span[@class="next"]/a/@href').get()
        if next:
            next_url = response.urljoin(next)
            yield Request(url=next_url, callback=self.parse)
        else:
            return None
    def parse_book_detail(self, response, book_item):
        book_info_node = response.xpath('//div[@id="info"]')
        author = book_info_node.xpath('.//span[contains(text(),"作者")]/following-sibling::a[1]/text()').get()
        publisher = book_info_node.xpath('.//span[contains(text(),"出版社")]/following-sibling::text()[1]').get()
        page_number = book_info_node.xpath('.//span[contains(text(),"页数")]/following-sibling::text()[1]').get()
        pub_time = book_info_node.xpath('.//span[contains(text(),"出版年")]/following-sibling::text()[1]').get()
        price = book_info_node.xpath('.//span[contains(text(),"定价")]/following-sibling::text()[1]').get()
        book_item['author'] = author
        book_item['publisher'] = publisher
        book_item['page_number'] = page_number
        book_item['pub_time'] = pub_time
        book_item['price'] = price
        img_url_big = response.xpath('//div[@id="mainpic"]/a/@href').get()
        book_item['img_url_big'] = img_url_big
        book_id = re.search(r'/subject/(\d+)', response.url).group(1)
        book_item['book_id'] = book_id


        book_introduction = response.xpath(
            '//div[@id="link-report"]/span[@class="all hidden"]/div/div[@class="intro"]').xpath('string(.)').get()
        if not book_introduction:
            book_introduction = response.xpath(
                '//div[@id="link-report"]/div/div[@class="intro"]').xpath('string(.)').get()
        author_introduction = response.xpath(
            '//div[@class="related_info"]/div[@class="indent "]/span[@class="all hidden "]/div[@class="intro"]').xpath(
            'string(.)').get()
        if not author_introduction:
            author_introduction = response.xpath(
                '//div[@class="related_info"]/div[@class="indent "]/div/div[@class="intro"]').xpath('string(.)').get()

        content = response.xpath(f'//div[@class="related_info"]/div[@id="dir_{book_id}_full"]').xpath('string(.)').get()
        if not content:
            content = response.xpath(f'//div[@class="related_info"]/div[@id="dir_{book_id}_short"]').xpath(
                'string(.)').get()



        book_item['book_introduction'] = book_introduction
        book_item['author_introduction'] = author_introduction
        book_item['content'] = content

        yield book_item
