import re
from pyquery import PyQuery as pq

from eliot import Message

from explo.exceptions import ParserException, ExploException

def required_fields(opts, fields):
    """
    Check if all ensured fields passed by `fields` are set in the options
    """

    if not all(k in opts for k in fields):
        raise ParserException(
            'not all required parameters were passed. required: ' \
            ','.join(fields)
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

            if not '?P<extract>' in pattern:
                raise ExploException('extract error: no "extract" match group found in regular expression.')

            regex_res = re.search(pattern, data, re.MULTILINE)
            if regex_res:
                result[name] = regex_res.group('extract')

    if extract_fields.items() and not result:
        Message.log(
            level='warning',
            message='No value found for extracting.')

    return result
