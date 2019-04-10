# -*- coding: utf-8 -*-
import scrapy
from tutorial.items import WeiboItem
from selenium import webdriver
from scrapy import signals, Selector
from scrapy.xlib.pydispatch import dispatcher
import pymongo


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    allowed_domains = ['weibo.cn']

    # 重写请求，这个不要了
    # start_urls = ['http://quotes.toscrape.com/']

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        # 配置不加载图片
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        # 配置无头浏览器
        chrome_options.add_argument('--headless')
        self.browser = webdriver.Chrome(options=chrome_options)

        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['weibo']
        # self.browser.get('https://passport.weibo.cn/signin/login')
        # self.browser.implicitly_wait(5)
        #
        # # 登录新浪
        # self.browser.find_element_by_css_selector('#loginName').send_keys('erchua8167867@163.com')
        # self.browser.find_element_by_css_selector('#loginPassword').send_keys('CLJobu841In')
        # self.browser.find_element_by_css_selector('#loginAction').click()

        super(QuotesSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def start_requests(self):
        # 随便搜索一个关键字
        keyword = 'has'
        base_serach_url = 'https://m.weibo.cn/search?containerid=100103type%3D1%26q%3D'
        start_url = base_serach_url + keyword
        yield scrapy.Request(url=start_url, callback=self.parse)

    def spider_closed(self, spider):
        # 爬虫推出时候关闭debug
        self.browser.quit()
        self.client.close()

    def handle_column(self, ss):
        # 修整不规则字段
        if not ss:
            return ''
        if ss.strip() in ('赞', '评论', '转发'):
            return '0'
        return ss.strip()

    def parse(self, response):
        # body = response.body.decode('utf8')
        # selector = Selector(text=body)
        # cards = selector.css('div.card-main')
        # for card in cards:
        #     t_author = card.css('header > div > div > a > h3::text').get()
        #     t_created_at = card.css('.time::text').get()
        #     t_source = card.css('.from::text').get()
        #     t_text = card.css('.weibo-text::text').get()
        #     t_forward = card.css('.m-font.m-font-forward+h4::text').get()
        #     t_comment = card.css('.m-font.m-font-comment+h4::text').get()
        #     t_like = card.css('.m-icon.m-icon-like+h4::text').get()
        #
        #     author = self.handle_column(t_author)
        #     created_at = self.handle_column(t_created_at)
        #     source = self.handle_column(t_source)
        #     text = self.handle_column(t_text)
        #     forward = self.handle_column(t_forward)
        #     comment = self.handle_column(t_comment)
        #     like = self.handle_column(t_like)
        #
        #     weibo_item = WeiboItem()
        #     for field in weibo_item:
        #         weibo_item[field] = eval(field)
        #     yield weibo_item

        # 放到中间件中处理
        print('========== End ============')
        pass
