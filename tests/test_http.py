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
        exploCSS: [CSS, "#explo"]
        exploRegexp: [REGEX, "<div id=explo>(?P<extract>.*?)</div>"]
"""

    body = '<div id=explo>explo</div>'

    responses.add(responses.GET, 'http://test.com/',
                  body=body, status=200,
                  content_type='text/html')

    blocks = explo.core.load_blocks(block_raw)

    _, scope = http.execute(blocks[0], {})

    assert scope['test']['response']['content'] == body
    assert scope['test']['extracted']['exploCSS'] == 'explo'
    assert scope['test']['extracted']['exploRegexp'] == 'explo'

def test_extract_html():
    """ Test invalid block (required field description/parameter missing) """

    content = "<html><body><input id=test value=foobar></body></html>"

    ret = http.extract(content, {'input':['CSS', '#test']})

    assert 'input' in ret and ret['input'] == 'foobar'

@responses.activate
def test_cookies():
    """ Test basic cookies support  """

    blocks_raw = """
name: get_cookie
description: Get a cookie
module: http
parameter:
    url: http://test.com/get
    method: GET
---
name: test
description: test
module: http
parameter:
    url: http://test.com/test
    cookies: get_cookie.response.cookies
    method: GET
"""

    cookie = 'foo=bar'

    def request_get_cookie(request):
        """ Return a simple cookie """
        headers = {'Set-Cookie': cookie}

        return (200, headers, '')

    def request_test_cookie(request):
        """ Return a simple cookie """
        assert 'Cookie' in request.headers and request.headers['Cookie'] == cookie

        return (200, {}, '')

    responses.add_callback(
        responses.GET, 'http://test.com/get',
        callback=request_get_cookie,
        content_type='text/html'
    )

    responses.add_callback(
        responses.GET, 'http://test.com/test',
        callback=request_test_cookie,
        content_type='text/html'
    )

    blocks = explo.core.load_blocks(blocks_raw)
    assert explo.core.process_blocks(blocks)
