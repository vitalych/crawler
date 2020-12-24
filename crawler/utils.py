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

import os
from trans import trans


def get_sanitized_filename(filename):
    """
    Sanitize the given file name by replacing all special characters with an underscore
    and keeping the extension if present.
    """

    # 1. discard the directory
    filename = os.path.basename(filename)

    # 2. transliterate all special characters to ascii
    filename = trans(filename).encode('ascii', 'ignore').decode('utf-8', 'ignore')

    # 3. split into non-empty extension components
    comp = [s for s in filename.split('.') if s]

    # 4. replace unwanted characters
    table = ''.join(c if c.isalnum() else '_' for c in map(chr,range(256)))

    comp = [s.translate(table) for s in comp]

    # 5. recompose filename
    filename = '.'.join(comp)
    if not filename:
        filename = 'file_to_analyze'
    return filename
