import datetime
import re
import emoji
from scrapy import Request

import pymysql
from scrapy.pipelines.images import ImagesPipeline


class BookdoubanPipeline:
    def process_item(self, item, spider):
        return item


class ImagePipeline(ImagesPipeline):

    def get_media_requests(self, item, info):

        name = item['book_name_main'].strip()
        img_url = item['img_url_small']
        yield Request(url=img_url, meta={'name': name})

    def file_path(self, request, response=None, info=None):
        name = request.meta.get('name') + '.' + request.url.split('/')[-1].split('.')[-1]
        return name


class DataCleaning:

    def process_item(self, item, spider):
        book_name_main = item['book_name_main']
        if not book_name_main:
            book_name_main = ''
        book_name_sub = item['book_name_sub']
        if not book_name_sub:
            book_name_sub = ''
        item['book_name'] = book_name_main.strip() + book_name_sub.strip()

        item['page_number'] = item['page_number'].strip() if item['page_number'] else None
        item['author'] = item['author'].strip() if item['author'] else None
        item['publisher'] = item['publisher'].strip() if item['publisher'] else None
        item['pub_time'] = item['pub_time'].strip() if item['pub_time'] else None
        item['price'] = item['price'].strip() if item['price'] else None

        if item['star'] and item['star'].strip()[-2:] != 'pl':
            if item['mark']:
                item['mark'] = item['mark'].strip()
            else:
                item['mark'] = None
            item['eval_num'] = re.search(r'(\d+)', item['eval_num']).group(1)
            if item['star'].strip()[-2:] == '00':
                item['star'] = '0'
            else:
                star_list = list(item['star'].strip())
                item['star'] = star_list[-2] + '.' + star_list[-1]
        else:
            item['star'] = None
            item['mark'] = None
            item['eval_num'] = None



        if item['book_introduction']:
            item['book_introduction'] = emoji.demojize(item['book_introduction'].strip())
        if item['author_introduction']:
            item['author_introduction'] = emoji.demojize(item['author_introduction'].strip())
        if item['content']:
            item['content'] = item['content'].strip()
        item['img_name'] = book_name_main.strip() + '.' + item['img_url_small'].split('.')[-1]
        return item


class MysqlPipeline(object):

    def __init__(self, host, port, database, user, password):

        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            port=crawler.settings.get('MYSQL_PORT'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
        )

    def open_spider(self, spider):
        self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=self.port)
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        data = {
            'book_name': item['book_name'],
            'page_number': item['page_number'],
            'author': item['author'],
            'publisher': item['publisher'],
            'pub_time': item['pub_time'],
            'star': item['star'],
            'mark': item['mark'],
            'eval_num': item['eval_num'],
            'price': item['price'],
            'book_introduction': item['book_introduction'],
            'author_introduction': item['author_introduction'],
            'book_id': item['book_id'],
            'img_url_small': item['img_url_small'],
            'img_url_big': item['img_url_big'],
            'img_name': item['img_name']
        }
        keys = ','.join(data.keys())
        values = ','.join(['%s'] * len(data))
        sql_book = 'insert into book (%s) values (%s)' % (keys, values)
        self.cursor.execute(sql_book, tuple(data.values()))
        self.db.commit()
        if item['content']:
            title_list = item['content'].split('\n')
            book_id = item['book_id']
            sql_content = 'insert into bookcontent(content,book_id) values (%s,%s)'
            for title in title_list:
                title = title.strip()
                if title and title.find('(收起)') == -1:
                    self.cursor.execute(sql_content, (title, book_id))
                    self.db.commit()
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.db.close()
