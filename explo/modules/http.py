"""
    explo.modules.http
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Simple HTTP request/response checks
"""
import re

from eliot import Message

from explo.connection import http_request
from explo.util import extract

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
        success = (re.search(opts['find'], response.text, flags=re.MULTILINE) != None)

        if not success:
            Message.log(
                level='status',
                message="Could not find '%s' in response body" % opts['find'])
        else:
            Message.log(level='status', message="Found '%s' in response body" % opts['find'])

    return success, scope

