""" Test the http_header module """
import os
import responses

import explo
from explo.modules import http_header as http

ROOT = os.path.dirname(os.path.realpath(__file__))

@responses.activate
def test_header_available():
    """ Test a simple http response """

    block_raw = """
name: test
description: test
module: http_header
parameter:
    url: http://test.com/valid
    method: GET
    headers_required:
        X-XSS-Protection: 1
"""

    responses.add(responses.GET, 'http://test.com/valid',
                  body='success', status=200,
                  adding_headers={'X-XSS-Protection':'1'},
                  content_type='text/html')

    blocks = explo.core.load_blocks(block_raw)
    ret, scope = http.execute(blocks[0], {})

    print(ret, scope)

    assert ret
    assert scope['test']['response']['content'] == 'success'

@responses.activate
def test_header_missing():
    """ Test a simple http response """

    block_raw = """
name: test
description: test
module: http_header
parameter:
    url: http://test.com/missing
    method: GET
    headers_required:
        X-XSS-Protection: 1
"""

    responses.add(responses.GET, 'http://test.com/missing',
                  body='success', status=200,
                  content_type='text/html')

    blocks = explo.core.load_blocks(block_raw)
    ret, scope = http.execute(blocks[0], {})

    assert ret == False
    assert scope['test']['response']['content'] == 'success'
