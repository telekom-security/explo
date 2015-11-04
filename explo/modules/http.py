""" Core HTTP functionalities """
import requests
from pyquery import PyQuery as pq

def execute(block, scope=None):
    """ Do HTTP request with options from block """
    required_fields = ['method', 'url']

    opts = block['parameter']

    if not all(k in opts for k in required_fields):
        raise Exception('not all required parameters were passed')

    headers = opts.get('headers', {})
    data = opts.get('body', {})

    resp = requests.request(opts['method'], opts['url'], headers=headers, data=data)

    ret = {
        'response': {
            'content':resp.content,
            'cookies':resp.cookies
        }
    }

    print('Response: %s (%s bytes)' % (resp.status_code, len(resp.content)))

    if 'extract' in opts:
        ret['extracted'] = extract(resp.content, opts['extract'])

    return ret

def extract(data, fields):
    """ Extract selectors from a html document """
    doc = pq(data)

    result = {}

    for key, val in fields.items():
        res = doc(val)
        found = None

        if len(res) > 1:
            raise Exception('extract error: found more than 1 result for "%s"' % val)

        if res.attr('value'):
            found = res.attr('value')
        elif res.text():
            found = res.text()

        result[key] = found

    return result
