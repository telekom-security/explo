"""
    explo.modules.http
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Simple HTTP request/response checks
"""
import re

from eliot import Message

from explo.connection import http_request
from explo.util import extract
from explo import color

def execute(block, scope):
    """
    Simple HTTP request, also does basic extracting and finding in the response text
    """

    name = block['name']
    opts = block['parameter']

    _, response = http_request(block, scope)

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
        keyword = opts['find']
        success = (keyword in response.text)

        if not success:
            Message.log(
                level='status',
                message="==> Not found in BODY: '%s'" % color.cyan(keyword))
        else:
            Message.log(
                level='status',
                message="==> Found in BODY: '%s'" % color.cyan(keyword))

    if 'find_regex' in opts:
        pattern = opts['find_regex']
        success = (re.search(pattern, response.text, flags=re.MULTILINE) != None)

        if not success:
            Message.log(
                level='status',
                message="==> Not found in BODY: '%s'" % color.cyan(pattern))
        else:
            Message.log(
                level='status',
                message="==> Found in BODY: '%s'" % color.cyan(pattern))

    return success, scope
