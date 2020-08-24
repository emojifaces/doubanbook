import scrapy


class BookdoubanItem(scrapy.Item):
    book_id = scrapy.Field()        # 书籍id
    book_name = scrapy.Field()  # 书籍名称
    book_name_main = scrapy.Field()  # 书籍名称 主标题
    book_name_sub = scrapy.Field()  # 书籍名称  副标题
    page_number = scrapy.Field()  # 总页数
    author = scrapy.Field()  # 作者
    publisher = scrapy.Field()  # 出版社
    pub_time = scrapy.Field()   # 出版时间
    star = scrapy.Field()  # 星级
    mark = scrapy.Field()  # 分数
    eval_num = scrapy.Field()       # 评价人数
    price = scrapy.Field()  # 价格
    book_introduction = scrapy.Field()  # 书籍简介
    author_introduction = scrapy.Field()  # 作者简介
    tag = scrapy.Field()  # 标签
    img_url_small = scrapy.Field()  # 图片url(小)
    img_url_big = scrapy.Field()  # 图片url（大）
    img_name = scrapy.Field()       # 图片名称
    content = scrapy.Field()  # 目录


