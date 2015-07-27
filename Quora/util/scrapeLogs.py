from Quora.QuoraScraper import QuoraScraper
import hashlib
import json
import gzip
from StringIO import StringIO
import binascii
import urllib2
import os
import selenium.common

basePath = '/export/a04/wpovell/'
if 'SCRAPE_LOG_BASEPATH' in os.environ:
    basePath = os.environ['SCRAPE_LOG_BASEPATH']

with open(os.path.join(basePath, 'scrapedUrls.txt')) as f:
    inp = set(f.read().strip().split('\n'))
with open(os.path.join(basePath, 'rescrapedUrls.txt')) as f:
    done = set(f.read().strip().split('\n'))
doneF = open(os.path.join(basePath, 'rescrapedUrls.txt'), 'a')

qs = QuoraScraper()
for line in list(inp - done):
    try:
        ret = qs.processLog(line)
    except Exception:
        print("BAD: {}".format(line))
        continue
    out = StringIO()
    try:
        with gzip.GzipFile(fileobj=out, mode="w") as f:
            f.write(ret['html'].encode('utf-8'))
    except TypeError:
        print("BAD: {}".format(line))
        continue

    compressed_html = out.getvalue()
    compressed_html = binascii.b2a_hex(compressed_html).decode('utf-8')
    fn = hashlib.md5(line.encode('utf-8')).hexdigest()
    with open(os.path.join(basePath, 'logPages/{}'.format(fn)), 'w') as f:
        json.dump({
            'html' : compressed_html,
            'url'  : line
        }, f)
    doneF.write('{}\n'.format(line))
    print(line)
