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
module: header
parameter:
    url: http://test.com/valid
    method: GET
    headers_required:
        X-XSS-Protection: 1
        Content-Type: .
"""

    responses.add(
        responses.GET,
        "http://test.com/valid",
        body="success",
        status=200,
        adding_headers={"X-XSS-Protection": "1"},
        content_type="text/html",
    )

    blocks = explo.core.load_blocks(block_raw)
    ret, scope = http.execute(blocks[0], {})

    print(ret, scope)

    assert ret == True
    assert scope["test"]["response"]["content"] == "success"

@responses.activate
def test_header_missing():
    """ Test a simple http response """

    block_raw = """
name: test
description: test
module: header
parameter:
    url: http://test.com/missing
    method: GET
    headers_required:
        X-XSS-Protection: 1
        Content-Type: .
"""

    responses.add(
        responses.GET,
        "http://test.com/missing",
        body="success",
        status=200,
        content_type="text/html",
    )

    blocks = explo.core.load_blocks(block_raw)
    ret, scope = http.execute(blocks[0], {})

    assert not ret


@responses.activate
def test_multiple_headers():
    """ Test if one of the given headers is missing """

    block_raw = """
name: test
description: test
module: header
parameter:
    url: http://test.com/missing
    method: GET
    headers_required:
        iDontExist: NoNo
        Content-Type: .
"""

    responses.add(
        responses.GET,
        "http://test.com/missing",
        body="success",
        status=200,
        content_type="text/html",
    )

    blocks = explo.core.load_blocks(block_raw)
    ret, scope = http.execute(blocks[0], {})

    assert not ret
