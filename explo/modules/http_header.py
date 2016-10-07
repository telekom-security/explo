"""
    explo.modules.http_header
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Check a http response for required headers to be set.
"""

from eliot import Message

from explo.exceptions import ParserException
from explo.connection import http_request
from explo.util import required_fields

def execute(block, scope):
    """
    Simple HTTP request, also does basic extracting and finding in the response text
    """
    opts = block['parameter']
    name = block['name']

    required_fields(opts, ['headers_required'])

    _, response = http_request(block, scope)

    scope[name] = {
        'response': {
            'content':response.text,
            'cookies':response.cookies,
            'headers':response.headers
        }
    }

    success = False

    headers_required = opts['headers_required']

    if not isinstance(headers_required, dict):
        raise ParserException('headers_required must be a list of headers')

    for header in headers_required:
        if header in response.headers:
            if headers_required[header] == '.':
                continue

            if str(headers_required[header]) != response.headers[header]:
                Message.log(
                    level='status',
                    message="Header '%s: %s' different from response header '%s: %s'" % (header, headers_required[header], header, response.headers[header]))
                success = True
        else:
            success = True
    return success, scope
