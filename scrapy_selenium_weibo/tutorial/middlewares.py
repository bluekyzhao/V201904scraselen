# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals, Selector
from scrapy.http import HtmlResponse
import time
from tqdm import tqdm
import pymongo


class TutorialSpiderMiddleware(object):
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

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
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


class TutorialDownloaderMiddleware(object):
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


class ChromeMiddleware:
    """使用selenium chrome 请求动态网页"""
    def __init__(self, page_num):
        self.page_num = page_num


    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            page_num=crawler.settings.get('PAGES')
        )

    def handle_column(self, ss):
        # 修整不规则字段
        if not ss:
            return ''
        if ss.strip() in ('赞', '评论', '转发'):
            return '0'
        return ss.strip()

    def process_request(self, request, spider):
        spider.browser.get(request.url)
        spider.browser.implicitly_wait(5)

        scroll_js = "window.scrollTo(0,document.body.scrollHeight);var lenOfPage = document.body.scrollHeight;return lenOfPage;"
        n = self.page_num
        for i in tqdm(range(n)):
            time.sleep(1)
            spider.browser.execute_script(scroll_js)

        selector = Selector(text=spider.browser.page_source)
        cards = selector.css('div.card-main')

        for card in cards:
            author = card.css('header > div > div > a > h3::text').get()
            created_at = card.css('.time::text').get()
            source = card.css('.from::text').get()
            text = card.css('.weibo-text::text').get()
            forward = card.css('.m-font.m-font-forward+h4::text').get()
            comment = card.css('.m-font.m-font-comment+h4::text').get()
            like = card.css('.m-icon.m-icon-like+h4::text').get()

            res_dict = {
                'author': self.handle_column(author),
                'created_at': self.handle_column(created_at),
                'source': self.handle_column(source),
                'text': self.handle_column(text),
                'forward': self.handle_column(forward),
                'comment': self.handle_column(comment),
                'like': self.handle_column(like)
            }

            spider.db.weibo.update_one({'text': self.handle_column(text)}, {'$set': res_dict}, True)

        return HtmlResponse(url=spider.browser.current_url, body=spider.browser.page_source, encoding='utf-8')
