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

import hashlib
import logging
import os
import sys
import urllib.parse

from crawler import utils

logger = logging.getLogger(__name__)


def _get_path(basedir, digest, filename):
    digest = digest.lower()
    return os.path.join(basedir, digest[0:2], digest[2:4], digest[4:6], f'{digest}-{filename}')


class CrawlerPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        cls.output_dir = settings.get("output_dir")

        if cls.output_dir is None:
            logger.error("Please specify the output_dir setting")
            sys.exit(-1)

        return cls()

    # pylint: disable=unused-argument,no-self-use
    def process_item(self, item, spider):
        u = urllib.parse.urlsplit(item['link'])
        filename = utils.get_sanitized_filename(os.path.basename(u.path))

        body = item['body'].body
        digest = hashlib.sha256(body).hexdigest()
        path = _get_path(CrawlerPipeline.output_dir, digest, filename)
        logger.info(path)

        dirpath = os.path.dirname(path)
        os.makedirs(dirpath, 0o700, True)

        with open(path, 'wb') as f:
            f.write(body)

        # remove body and add path as reference
        del item['body']
        # let item be processed by other pipelines. ie. db store
        return item
