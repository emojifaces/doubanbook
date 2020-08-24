from scrapy import cmdline

name = 'BookSpider'

cmd = f'scrapy crawl {name}'
cmdline.execute(cmd.split())
