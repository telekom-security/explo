""" Test the core http module """
import os
import time
import responses

import explo
from explo.modules import sqli_blind

ROOT = os.path.dirname(os.path.realpath(__file__))

@responses.activate
def test_timed_sqli():
    """ Test a time based sql injection"""

    block_raw = """
name: test
description: test
module: sqli_blind
parameter:
    url: http://test.com/
    method: GET
    delay_seconds: 0.5
"""


    def request_callback(request):
        time.sleep(0.5)
        return (200, {}, 'success')

    responses.add_callback(
        responses.GET, 'http://test.com/',
        callback=request_callback,
        content_type='application/json'
    )

    blocks = explo.core.load_blocks(block_raw)

    ret, scope = sqli_blind.execute(blocks[0], {})

    print(scope)

    assert ret

@responses.activate
def test_timed_sqli_invalid():
    """ Test a time based sql injection"""

    block_raw = """
name: test
description: test
module: sqli_blind
parameter:
    url: http://test.com/
    method: GET
    delay_seconds: 1
"""


    def request_callback(request):
        return (200, {}, 'success')

    responses.add_callback(
        responses.GET, 'http://test.com/',
        callback=request_callback,
        content_type='application/json'
    )

    blocks = explo.core.load_blocks(block_raw)

    ret, scope = sqli_blind.execute(blocks[0], {})

    print(scope)

    assert ret is False
