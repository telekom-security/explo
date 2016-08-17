"""
    explo.modules.http_header
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Check a http response for required headers to be set.
"""
import requests
import pystache

from eliot import Message

from explo.exceptions import ExploException, ParserException
from explo.modules.http import pretty_print_request, pretty_print_response
from explo.connection import proxies

def execute(block, scope):
    """
    Simple HTTP request, also does basic extracting and finding in the response text
    """
    required_fields = ['method', 'url', 'headers_required']

    opts = block['parameter']
    name = block['name']

    cookies = dict()

    if not all(k in opts for k in required_fields):
        raise ParserException('not all required parameters were passed')

    headers = opts.get('headers', {})
    headers_required = opts.get('headers_required', {})
    data = opts.get('body', {})
    cookies_path = opts.get('cookies', '')
    allow_redirects = opts.get('allow_redirects', False)

    if cookies_path != '':
        try:
            cookie_module = cookies_path.split('.', 1)[0]
            cookies = scope[cookie_module]['response']['cookies']
        except KeyError:
            Message.log(level='warning', message='could not retrieve cookies from scope or previous step, the step "%s" was not found.' % cookies_path)

    # Use mustache template on string
    try:
        if isinstance(data, dict):
            for key, val in data.items():
                data[key] = pystache.render(val, scope)
        elif isinstance(data, basestring):
            data = pystache.render(data, scope)
    except Exception as e:
        raise ParserException('error while parsing explo file: %s' % e)

    # Use mustache template on headers
    for key, val in headers.items():
        headers[key] = pystache.render(val, scope)


    req = requests.Request(opts['method'], opts['url'], headers=headers, data=data, cookies=cookies)
    request_prepared = req.prepare()

    sess = requests.Session()
    resp = sess.send(request_prepared, allow_redirects=allow_redirects, proxies=proxies, verify=False)

    Message.log(level='status', message='Response: %s (%s bytes)' % (resp.status_code, len(resp.content)))

    scope[name] = {
        'response': {
            'content':resp.text,
            'cookies':resp.cookies,
            'headers':resp.headers
        }
    }

    success = True

    if not isinstance(headers_required, dict):
        raise ParserException('headers_required must be a list of headers')

    for header in headers_required:
        if not header in resp.headers:
            success = False
            Message.log(level='status', message="Could not find '%s' header" % header)
        else:
            if headers_required[header] != '.':
                if str(headers_required[header]) != resp.headers[header]:
                    success = False
                    Message.log(level='status', message="Header '%s: %s' different from response header '%s: %s'" % (header, headers_required[header], header, resp.headers[header]))

    pretty_print_request(request_prepared)
    pretty_print_response(resp)

    return success, scope
