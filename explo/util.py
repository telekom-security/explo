import re
import sys
from pyquery import PyQuery as pq

from explo.exceptions import ParserException, ExploException

def required_fields(opts, fields):
    """
    Check if all ensured fields passed by `fields` are set in the options
    """

    if not all(k in opts for k in fields):
        raise ParserException(
            'not all required parameters were passed. required: ' \
            ','.join(required_fields)
        )

def extract(data, extract_fields):
    """ Extract selectors from a html document """

    result = {}

    for name, opts in extract_fields.items():
        if len(opts) != 2:
            raise ParserException('extract error: mailformed extract entry.')

        method, pattern = opts

        if method == 'CSS':
            doc = pq(data)

            res = doc(pattern)
            found = None

            if len(res) > 1:
                raise ExploException('extract error: found more than 1 result for "%s"' % pattern)

            if res.attr('value'):
                found = res.attr('value')
            elif res.text():
                found = res.text()

            result[name] = found

        if method == 'REGEX':
            regex_res = re.search(pattern, data, re.MULTILINE)
            if regex_res:
                result[name] = regex_res.group('extract')

    return result

# Color code is copied from https://github.com/reorx/python-terminal-color/blob/master/color_simple.py

"""
class Color:
    NO_COLOR = False

    @classmethod
    def make_color(code):
        def color_func(s):
            if not sys.stdout.isatty() or Color.NO_COLOR:
                return s
            tpl = '\x1b[{}m{}\x1b[0m'
            return tpl.format(code, s)
        return color_func

    red = make_color(31)
    green = make_color(32)
    yellow = make_color(33)
    blue = make_color(34)
    magenta = make_color(35)
    cyan = make_color(36)

    bold = make_color(1)
    underline = make_color(4)

    grayscale = {(i - 232): make_color('38;5;' + str(i)) for i in range(232, 256)}
"""
