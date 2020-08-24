# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import base64
import logging
import random
import requests
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware

from .configure import *
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

from .utils import get_one_proxy, get_proxy, delete_proxy
from scrapy.http.response.html import HtmlResponse


class BookdoubanSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.

        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.

        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.

        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class BookdoubanDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest

        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class UserAgentMiddleware:

    def __init__(self, agents):
        self.ua = agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            agents=CUSTOM_USER_AGENT
        )

    def process_request(self, request, spider):
        if self.ua:
            request.headers.setdefault('User-Agent', random.choice(self.ua))


# class ProxyMiddleware:
#
#     def __init__(self, proxy_ip):
#         self.proxy_ip = proxy_ip
#
#     @classmethod
#     def from_crawler(cls, crawler):
#
#         ip = requests.get(url=GET_PROXY_IP_URL,headers=GET_PROXY_IP_HEADERS)
#         return cls(
#             proxy_ip=ip
#         )
#
#     def process_request(self, request, spider):
#         if self.proxy_ip:
#             request.meta['proxy'] = self.proxy_ip

# API接口，返回格式为json
api_url = 'http://127.0.0.1:5010/get/'
# 非开放代理且未添加白名单，需用户名密码认证


username = "1079980583"
password = "x2gaz894"
logger = logging.getLogger(__name__)


class ProxyDownloadMiddleware:

    def process_request(self, request, spider):

        if request.url.startswith("http://"):
            request.meta['proxy'] = "http://{proxy_ip}".format(proxy_ip=get_proxy(api_url))
        elif request.url.startswith("https://"):
            request.meta['proxy'] = "https://{proxy_ip}".format(proxy_ip=get_proxy(api_url))

    def process_response(self, request, response, spider):

        if response.status != 200:

            failed_ip = request.meta['proxy']
            delete_proxy(failed_ip)
            if request.url.startswith("http://"):
                request.meta['proxy'] = "http://{proxy_ip}".format(proxy_ip=get_proxy(api_url))
            elif request.url.startswith("https://"):
                request.meta['proxy'] = "https://{proxy_ip}".format(proxy_ip=get_proxy(api_url))
            return request
        else:
            return response

    def process_exception(self, request, exception, spider):

        failed_ip = request.meta['proxy']
        delete_proxy(failed_ip)

        if request.url.startswith("http://"):
            request.meta['proxy'] = "http://{proxy_ip}".format(proxy_ip=get_proxy(api_url))
        elif request.url.startswith("https://"):
            request.meta['proxy'] = "https://{proxy_ip}".format(proxy_ip=get_proxy(api_url))

        return request

# class ProxyDownloadMiddleware(RetryMiddleware):
#
#     def process_exception(self, request, exception, spider):

# if '10061' in str(exception) or '10060' in str(exception):
#     if request.url.startswith("http://"):
#         request.meta['proxy'] = "http://{proxy_ip}".format(proxy_ip=get_one_proxy(api_url))
#     elif request.url.startswith("https://"):
#         request.meta['proxy'] = "https://{proxy_ip}".format(proxy_ip=get_one_proxy(api_url))
#     logging.debug("using proxy: {}".format(request.meta['proxy']))
#     # 使用私密代理或独享代理需要将用户名和密码进行base64编码，然后赋值给request.headers["Proxy-Authorization"]
#     #
#     # 如果是开放代理就不需要以下步骤，直接设置代理IP即可
#     user_password = "{username}:{password}".format(username=username, password=password)
#     b64_user_password = base64.b64encode(user_password.encode("utf-8"))
#     request.headers["Proxy-Authorization"] = "Basic " + b64_user_password.decode("utf-8")
#
# if isinstance(exception, self.EXCEPTIONS_TO_RETRY) and not request.meta.get('dont_retry', False):
#     return self._retry(request, exception, spider)

# if request.url.startswith("http://"):
#     request.meta['proxy'] = "http://{proxy_ip}".format(proxy_ip=get_one_proxy(api_url))
# elif request.url.startswith("https://"):
#     request.meta['proxy'] = "https://{proxy_ip}".format(proxy_ip=get_one_proxy(api_url))
# logging.debug("using proxy: {}".format(request.meta['proxy']))
# # 使用私密代理或独享代理需要将用户名和密码进行base64编码，然后赋值给request.headers["Proxy-Authorization"]
# #
# # 如果是开放代理就不需要以下步骤，直接设置代理IP即可
# user_password = "{username}:{password}".format(username=username, password=password)
# b64_user_password = base64.b64encode(user_password.encode("utf-8"))
# request.headers["Proxy-Authorization"] = "Basic " + b64_user_password.decode("utf-8")
# return None
