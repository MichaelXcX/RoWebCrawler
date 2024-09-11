from urllib.parse import urlparse
import re

def filter_domain_from_url(url):
    try:
        uri = urlparse(url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=uri)
        return domain
    except Exception as e:
        print('There was a problem: %s' % (e))