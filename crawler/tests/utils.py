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
import unittest
from unittest import TestCase

from crawler.utils import get_sanitized_filename

logger = logging.getLogger(__name__)


class FilenameTests(TestCase):
    def test_sanitize_filename(self):
        logger.info("Testing sanitize_filename")
        tests = (('simple.exe', 'simple.exe'),
                 ('some space.txt', 'some_space.txt'),
                 ('noext', 'noext'),
                 ('j4456.ext', 'j4456.ext'),
                 ('twoext.tar.gz', 'twoext.tar.gz'),
                 ('ab.!ex', 'ab._ex'),
                 ('!.ex', '_.ex'),
                 ('path/to/file', 'file'),
                 ('../file', 'file'),
                 ('../fileéà', 'fileea'),
                 ('../fileфыва', 'filefyva'),
                 ('.............', 'file_to_analyze'),
                 ('....../.......', 'file_to_analyze'),
                 ('a..b', 'a.b'),
                 ('.hidden', 'hidden'),
                 ('a...b', 'a.b'))

        for test in tests:
            self.assertEqual(get_sanitized_filename(test[0]), test[1])


if __name__ == '__main__':
    unittest.main()