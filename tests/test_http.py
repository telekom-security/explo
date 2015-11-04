""" Test the core http module """
import os
import responses

import explo
from explo.modules import http

ROOT = os.path.dirname(os.path.realpath(__file__))

@responses.activate
def test_simple_get():
    """ Test a simple http get and the extraction of a css selector """

    block_raw = """
name: test
description: test
module: http
parameter:
    url: http://test.com/
    method: GET
    headers:
        user-agent: Mozilla/5.0
        content-type: application/x-www-form-urlencoded
    body:
        text: <div id=explo>explo</div>
    extract:
        explo: "#explo"
"""

    body = b'<div id=explo>explo</div>'

    responses.add(responses.GET, 'http://test.com/',
                  body=body, status=200,
                  content_type='text/html')

    blocks = explo.core.load_blocks(block_raw)

    ret = http.execute(blocks[0])

    assert ret['response']['content'] == body
    assert ret['extracted']['explo'] == 'explo'

def test_extract_html():
    """ Test invalid block (required field description/parameter missing) """

    content = "<html><body><input id=test value=foobar></body></html>"

    ret = http.extract(content, {'input':'#test'})

    assert 'input' in ret and ret['input'] == 'foobar'
