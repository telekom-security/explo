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
        id: "'A"
    session: login.session
    find: You have an error in your SQL syntax
"""

BLOCKS_CSRF = """
name: csrf_token
description: get a csrf token to exploit form
module: http
parameter:
    url: http://test.com/contact
    method: GET
    extract:
        csrf: [CSS, "#csrf"]
---
name: exploit
description: exploit with csrf token
module: http
parameter:
    url: http://test.com/contact
    method: POST
    body:
        name: "'A"
        csrf: "{{csrf_token.extracted.csrf}}"
    find: You have an error in your SQL syntax
"""

def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))

@responses.activate
def test_workflow_simple():
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

    assert explo.core.process_blocks(blocks)

@responses.activate
def test_workflow_csrf_token():
    """ Test a simple http get and the extraction of a css selector """

    body_contact = b'<form><input type="hidden" name="csrf" id="csrf" value="token_1337"><input type="text" name="name"></form>'
    body_success = b'<div id=error>You have an error in your SQL syntax</div>'

    def request_callback_csrf(request):
        """ Checks for a valid CSRF token (token_1337) and returns a fake 'sql injection success' message """
        assert 'csrf=token_1337' in request.body

        return (200, {}, body_success)

    responses.add(responses.GET, 'http://test.com/contact',
                  body=body_contact, status=200,
                  content_type='text/html')

    responses.add_callback(
        responses.POST, 'http://test.com/contact',
        callback=request_callback_csrf,
        content_type='text/html',
    )

    blocks = explo.core.load_blocks(BLOCKS_CSRF)

    assert explo.core.process_blocks(blocks)
