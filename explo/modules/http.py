"""
    explo.modules.http
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Simple HTTP request/response checks
"""
import re

from pyquery import PyQuery as pq
from eliot import Message

from explo.exceptions import ExploException, ParserException
from explo.connection import http_request

def execute(block, scope):
    """
    Simple HTTP request, also does basic extracting and finding in the response text
    """

    name = block['name']
    opts = block['parameter']

    _, response = http_request(block, scope)

    Message.log(
        level='status',
        message='Response: %s (%s bytes)' % (response.status_code, len(response.content)))

    scope[name] = {
        'response': {
            'content':response.text,
            'cookies':response.cookies,
            'headers':response.headers
        }
    }

    success = True

    if 'extract' in opts:
        scope[name]['extracted'] = extract(response.text, opts['extract'])

    if 'find' in opts:
        success = (re.search(opts['find'], response.text, flags=re.MULTILINE) != None)

        if not success:
            Message.log(
                level='status',
                message="Could not find '%s' in response body" % opts['find'])
        else:
            Message.log(level='status', message="Found '%s' in response body" % opts['find'])

    return success, scope

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
