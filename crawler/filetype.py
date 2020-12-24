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
from zipfile import is_zipfile, ZipFile

import oletools.oleid

logger = logging.getLogger(__name__)


# en.wikipedia.org/wiki/List_of_Microsoft_Office_filename_extensions
_type_extensions = {
    'filetype:pdf': ['pdf'],
    'filetype:archive': ['tgz', 'tar', 'bz2', 'gz', '7z', 'rar', 'zip', 'zipx'],
    'filetype:msoffice-word': [
        'rtf', 'doc', 'dot',
        'docx', 'docm', 'dotx', 'dotm', 'docb'
    ],
    'filetype:msoffice-excel': [
        'xls', 'xlt', 'xlm',
        'xlsx', 'xlsm', 'xltx', 'xltm',
        'xlsb', 'xla', 'xlam', 'xll', 'xlw',
    ],
    'filetype:msoffice-powerpoint': [
        'ppt', 'pot', 'pps',
        'pptx', 'pptm', 'potx', 'potm',
        'ppam', 'ppsx', 'ppsm', 'sldx', 'sldm',
    ],
}

_extension_types = {
    ext: tp for tp, exts in _type_extensions.items() for ext in exts
}

_document_types = [
    'filetype:pdf',
    'filetype:msoffice-word', 'filetype:msoffice-excel', 'filetype:msoffice-powerpoint'
]


def get_file_type(file_name):
    """ Determine file type based on the filename extension """

    name_parts = file_name.split('.')

    try:
        name_idx = next(n for n, p in enumerate(name_parts) if p)
    except StopIteration:
        return None

    ext_parts = name_parts[name_idx+1:]

    for n in range(len(ext_parts)):
        file_type = _extension_types.get('.'.join(ext_parts[n:]), None)
        if file_type:
            return file_type

    return None


def is_archive(file_name):
    ft = get_file_type(file_name)
    return ft == 'filetype:archive'


def get_office_open_xml_types_for_file(filelike_object):
    """
    Returns a list of msoffice file types for given argument, or [].
    Looks at the argument as a zip file and checks for file names corresponding
    to Office Open XML formats for Word, Excel and Powerpoint
    """

    types = []
    try:
        # should be a zip file with these two files present
        if not is_zipfile(filelike_object):
            return []
        z = ZipFile(filelike_object)
        z.getinfo('[Content_Types].xml')
        z.getinfo('_rels/.rels')
    except:
        return []

    # check for the standard file names for each app
    try:
        z.getinfo('word/document.xml')
        types += ['filetype:msoffice-word']
    except:
        pass

    try:
        z.getinfo('xl/workbook.xml')
        types += ['filetype:msoffice-excel']
    except:
        pass

    try:
        z.getinfo('ppt/presentation.xml')
        types += ['filetype:msoffice-powerpoint']
    except:
        pass

    return types


def get_archive_types_for_content(content):
    """Returns ['filetype:archive'] or [] based on the given content."""
    # https://en.wikipedia.org/wiki/List_of_file_signatures
    headers = ['\x1f\x9d', '\x1f\xa0', 'PK', 'Rar!', 'CD001',
               'x\x01s\x0dbb\x60', 'xar!']

    if any(content.startswith(h) for h in headers):
        return ['filetype:archive']
    return []


def get_office_ole_types_for_content(content):
    types = []
    try:
        oid = oletools.oleid.OleID(content)
        indicators = oid.check()
        for i in indicators:
            logger.info('%s, %s=%s',  str(i), str(i.id), str(i.value))
            if i.id == 'word' and i.value:
                types += ['filetype:msoffice-word']
            if i.id == 'excel' and i.value:
                types += ['filetype:msoffice-excel']
            if i.id == 'ppt' and i.value:
                types += ['filetype:msoffice-powerpoint']
    except Exception as e:
        logger.info('oleid exception: %s', str(e))

    return types


def _is_msword_mime(content):
    indicators = ['MIME-Version', 'filelist.xml', '.mso']
    return all(ind in content for ind in indicators)


def guess_content_type(target_file):
    """
    Guesses the type of the file based on its content.
    """

    types = []

    header = target_file.read(8)
    target_file.seek(0)

    if header[:4] == '%PDF':
        types += ['filetype:pdf']
    elif header[:4] == '\177CGC':
        types += ['filetype:cgc']
    elif header[:5] == '{\\rtf':
        types += ['filetype:msoffice-word']
    else:
        content = target_file.read()
        target_file.seek(0)
        types += get_office_ole_types_for_content(content)
        types += get_office_open_xml_types_for_file(target_file.file)
        if _is_msword_mime(content):
            types += ['filetype:msoffice-word']
        types += get_archive_types_for_content(content)

    if not types:
        return None

    return types[0]


def is_document(filename):
    for dt in _document_types:
        for ext in _type_extensions[dt]:
            if filename.endswith(ext):
                return True
    return False
