import os
import pystache
import six

import requests
from requests.exceptions import ProxyError
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from eliot import Message

from explo.exceptions import ParserException, ProxyException, ConnectionException
from explo import color

proxies = {
    'http': os.environ.get('http_proxy', None),
    'https': os.environ.get('https_proxy', None),
}

def http_request(block, scope):
    """
    Extract data from block and construct http request
    """
    required_fields = ['method', 'url']

    opts = block['parameter']

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
            Message.log(
                level='warning',
                message='could not retrieve cookies from scope or previous step,' \
                        'the step "%s" was not found.' % cookies_path)

    # Use mustache template on string
    if isinstance(data, dict):
        for key, val in data.items():
            data[key] = pystache.render(val, scope)
    elif isinstance(data, six.string_types):
        data = pystache.render(data, scope)

    # Use mustache template on headers
    for key, val in headers.items():
        headers[key] = pystache.render(str(val), scope)

    req = requests.Request(opts['method'], opts['url'], headers=headers, data=data, cookies=cookies)
    request = req.prepare()

    if proxies.get('http', None):
        Message.log(level='status', message='Using proxies {}'.format(proxies))

    try:
        sess = requests.Session()
        resp = sess.send(request, allow_redirects=allow_redirects, proxies=proxies, verify=False)
    except ProxyError as exc:
        raise ProxyException(exc)
    except Exception as exc:
        raise ConnectionException(exc)

    Message.log(
        level='status',
        message='HTTP Response: %s (%s bytes)' % (resp.status_code, len(resp.content)))

    pretty_print_request(request)
    pretty_print_response(resp)

    return request, resp

def pretty_print_request(req):
    """ Print a request """

    output = '{} {} {}\n'.format(color.yellow(req.method), color.cyan(req.url), color.grayscale[14]('HTTP/1.1'))
    output += '\n'.join('{}: {}'.format(color.grayscale[14](k), color.cyan(v)) for k, v in req.headers.items())
    output += '\n\n{}'.format(req.body)

    Message.log(level='request', message=output)

def pretty_print_response(res):
    """ Print a response """

    # Status line
    output = color.yellow('HTTP') + color.grayscale[14]('/1.1 %s %s\n' % (res.status_code, res.reason))

    # Headers
    for name, value in res.headers.items():
        output += '%s: %s\n' % (color.grayscale[14](name), color.cyan(value))

    output += '\n'

    # Body
    output += res.text

    Message.log(level='response', message=output)
