"""
Copyright (c) 2014-2020 Cyberhaven

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging
import sys
import urllib.parse

import scrapy
from scrapy.selector import Selector
from scrapy.http import Request

from crawler.items import CrawlerItem
from crawler.filetype import is_document

logger = logging.getLogger(__name__)


class DocumentSpider(scrapy.Spider):
    name = 'DocumentSpider'
    start_urls = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        start_url = kwargs.get('start_url')
        if start_url is None:
            logger.error('Please specify start_url option')
            sys.exit(1)

        self.start_urls = [start_url]

        u = urllib.parse.urlsplit(start_url)
        self.allowed_domains = [u.hostname]

    # pylint: disable=arguments-differ
    def parse(self, response):
        logger.debug('Getting URL: %s', response.url)
        items = []

        if is_document(response.url):
            item = CrawlerItem()
            item['body'] = response
            item['link'] = response.url
            items.append(item)
            return items

        try:
            sel = Selector(response)
            for link in sel.xpath('//a'):
                href = link.xpath('@href').extract()

                if not href:
                    continue

                lnk = href[0].strip()
                if lnk.startswith('#') or not lnk or lnk.startswith('mailto:'):
                    continue

                url = urllib.parse.urljoin(response.url, lnk)
                items.append(Request(url))
        except Exception as e:
            logger.error(e)

        return items
