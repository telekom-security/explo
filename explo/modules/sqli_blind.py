"""
    explo.modules.sqli_blind
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Check for Blind SQL-Injections
"""
from eliot import Message

from explo.connection import http_request
from explo.util import required_fields

def execute(block, scope):
    """
    Execute block and check for blind SQL injection
    """

    name = block['name']
    opts = block['parameter']

    required_fields(opts, ['type'])

    if opts['type'] == 'timed':
        required_fields(opts, ['delay_seconds'])

    delay_seconds = float(opts['delay_seconds'])

    _, response = http_request(block, scope)
    time_diff = response.elapsed.total_seconds()

    Message.log(
        level='status',
        message='Response: %s (%s bytes)' % (response.status_code, len(response.content)))

    scope[name] = {
        'response': {
            'content':response.text,
            'cookies':response.cookies,
            'headers':response.headers
        },
        'time_diff': time_diff
    }

    Message.log(
        level='status',
        message="Response time: {}, delay_seconds: {}".format(time_diff, delay_seconds)
    )

    if time_diff > delay_seconds:
        return True, scope
    else:
        return False, scope
