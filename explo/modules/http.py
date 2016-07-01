"""
    explo.modules.http
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Core HTTP request functionalities
"""
import re
import requests
import pystache
import six

from pyquery import PyQuery as pq
from eliot import Message

from explo.exceptions import ExploException, ParserException

def execute(block, scope):
    """
    Simple HTTP request, also does basic extracting and finding in the response text
    """
    required_fields = ['method', 'url']

    opts = block['parameter']
    name = block['name']

    cookies = dict()

    if not all(k in opts for k in required_fields):
        raise ParserException('not all required parameters were passed')

    headers = opts.get('headers', {})
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
    if isinstance(data, dict):
        for key, val in data.items():
            data[key] = pystache.render(val, scope)
    elif isinstance(data, six.string_types):
        data = pystache.render(data, scope)

    # Use mustache template on headers
    for key, val in headers.items():
        headers[key] = pystache.render(val, scope)

    req = requests.Request(opts['method'], opts['url'], headers=headers, data=data, cookies=cookies)
    request_prepared = req.prepare()

    sess = requests.Session()
    resp = sess.send(request_prepared, allow_redirects=allow_redirects)

    Message.log(level='status', message='Response: %s (%s bytes)' % (resp.status_code, len(resp.content)))

    scope[name] = {
        'response': {
            'content':resp.text,
            'cookies':resp.cookies,
            'headers':resp.headers
        }
    }

    success = True

    if 'extract' in opts:
        scope[name]['extracted'] = extract(resp.text, opts['extract'])

    if 'find' in opts:
        success = (re.search(opts['find'], resp.text, flags=re.MULTILINE) != None)

        if not success:
            Message.log(level='status', message="Could not find '%s' in response body" % opts['find'])
        else:
            Message.log(level='status', message="Found '%s' in response body" % opts['find'])

    pretty_print_request(request_prepared)
    pretty_print_response(resp)

    return success, scope

def extract(data, extract_fields):
    """ Extract selectors from a html document """

    result = {}

    for name, opts in extract_fields.items():
        if len(opts) != 2:
            raise ParserException('extract error: mailformed extract entry.')

        method, pattern = opts

        if method == 'CSS':
            doc = pq(data)

            res = doc(pattern)
            found = None

            if len(res) > 1:
                raise ExploException('extract error: found more than 1 result for "%s"' % pattern)

            if res.attr('value'):
                found = res.attr('value')
            elif res.text():
                found = res.text()

            result[name] = found

        if method == 'REGEX':
            regex_res = re.search(pattern, data, re.MULTILINE)
            if regex_res:
                result[name] = regex_res.group('extract')

    return result

def pretty_print_request(req):
    """ Print a request """

    output = '{} HTTP/1.1\n{}\n\n{}'.format(
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    )

    Message.log(level='request', message=output)

def pretty_print_response(res):
    """ Print a response """


    # Status line
    output = 'HTTP/1.1 %s %s\n' % (res.status_code, res.reason)

    # Headers
    for name, value in res.headers.items():
        output += '%s: %s\n' % (name, value)

    output += '\n'

    # Body
    output += res.text

    Message.log(level='response', message=output) 
