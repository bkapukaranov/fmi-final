__author__ = 'Borislav Kapukaranov'

import scrapy
import review_parser

# scrapy shell http://www.cinexio.com/sofia/movie/19579
# run with: scrapy runspider -s AUTOTHROTTLE_ENABLED=1 -s DOWNLOAD_DELAY=1 cinexio_single_crawler.py

class CinexioSpider(scrapy.Spider):

    name = 'cinexio'
    allowed_domains = ['cinexio.com']

    # use for full site crawl
    start_urls = ['http://www.cinexio.com/sofia/movie/19579']

    def parse(self, response):
        review_parser.parse_review(response)