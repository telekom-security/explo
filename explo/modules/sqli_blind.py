"""
    explo.modules.sqli_blind
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Check for time based blind SQL-Injections
"""
from eliot import Message

from explo.connection import http_request
from explo.util import required_fields
from explo import color

def execute(block, scope):
    """
    Execute block and check for blind SQL injection
    """

    name = block['name']
    opts = block['parameter']

    required_fields(opts, ['delay_seconds'])

    delay_seconds = float(opts['delay_seconds'])

    _, response = http_request(block, scope)
    time_diff = response.elapsed.total_seconds()

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
        message="Response time: {}, delay_seconds: {}".format(color.cyan(time_diff), color.cyan(delay_seconds))
    )

    if time_diff > delay_seconds:
        return True, scope
    else:
        return False, scope
