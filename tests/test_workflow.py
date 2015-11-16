""" Test a basic workflow """
import responses

import explo
import explo.core
from explo.modules import http

BLOCKS_RAW = """
name: login
description: do a login before exploiting the profile page
module: http
parameter:
    url: http://test.com/login
    method: POST
    body:
        username: test
        password: test
    find: Login Successful      # ensure login succeeded
---
name: exploit
description: test
module: http
parameter:
    url: http://test.com/profile
    method: GET
    body:
        id='A
    session: login.session
    find: You have an error in your SQL syntax
"""

@responses.activate
def test_simple_get():
    """ Test a simple http get and the extraction of a css selector """

    body_login = b'<div id=login>Login Successful</div>'
    body_sqli = b'<div id=error>You have an error in your SQL syntax</div>'

    responses.add(responses.POST, 'http://test.com/login',
                  body=body_login, status=200,
                  content_type='text/html')

    responses.add(responses.GET, 'http://test.com/profile',
                  body=body_sqli, status=200,
                  content_type='text/html')

    blocks = explo.core.load_blocks(BLOCKS_RAW)

    assert explo.core.proccess_blocks(blocks)
