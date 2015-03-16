__author__ = 'Borislav Kapukaranov'

import review_parser
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

# run with: scrapy runspider -s AUTOTHROTTLE_ENABLED=1 -s DOWNLOAD_DELAY=1 cinexio_homepage_crawler.py

class CinexioSpider(CrawlSpider):

    name = 'cinexio'
    allowed_domains = ['cinexio.com']

    start_urls = ['http://www.cinexio.com/sofia/now']
    rules = [Rule(LinkExtractor(allow=['/sofia/movie/\d+']), 'parse_movie')]

    def parse_movie(self, response):
        review_parser.parse_review(response)