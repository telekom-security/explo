import os

proxies = {
    'http': os.environ.get('http_proxy', None),
    'https': os.environ.get('https_proxy', None),
}
