__author__ = 'Borislav Kapukaranov'

import scrapy
import review_parser

# run with: scrapy runspider -s AUTOTHROTTLE_ENABLED=1 -s DOWNLOAD_DELAY=1 cinexio_homepage_crawler.py

class CinexioSpider(scrapy.Spider):

    name = 'cinexio'
    allowed_domains = ['cinexio.com']

    # use for full site crawl
    start_urls = ['http://www.cinexio.com/sofia/movie/%d' %(n) for n in range(0, 25000)]

    def parse(self, response):
        review_parser.parse_review(response)