import sys
VERSION = sys.version_info[0]

import hashlib
import gzip
import socket
import json
import binascii
import os
import argparse
from datetime import datetime
from time import time

import logging
logging.basicConfig(level=logging.INFO)

from QuoraScraper import QuoraScraper

if VERSION == 2:
	from StringIO import StringIO
	ConnectionRefusedError = socket.error

parser = argparse.ArgumentParser(description='Start Quora scraping client.')
parser.add_argument('HOST', type=str, default="localhost", nargs='?', help='address of server')
parser.add_argument('PORT', type=int, default=9999, nargs='?', help='port server is listening on')
parser.add_argument('-o', '--output', type=str, default=None, nargs=1, help="directory to write output to")
parser.add_argument('-t', '--wait', type=int, default=7, nargs=1, help="how long to wait between requets")
args = parser.parse_args()

HOST = args.HOST
PORT = args.PORT

if args.output is None:
	OUTPUT_DIRECTORY = "data"
else:
	OUTPUT_DIRECTORY = args.output[0]

EMPTY_REQUEST = {
	"links"	: [],
	"url"	: "",
	"error" : False,
	"data"	: False
}

def getUrl(data):
	data = json.dumps(data).encode('utf-8') + b'\n'
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		sock.connect((HOST, PORT))
		sock.sendall(data)
		f = sock.makefile()
		url = f.readline().strip()
		f.close()

	finally:
		sock.close()

	return url

def writeFile(url, output):
	if not os.path.isdir(OUTPUT_DIRECTORY):
		os.mkdir(OUTPUT_DIRECTORY)
	hashed_url = hashlib.md5(url.encode('utf-8')).hexdigest()
	fn = '{}/{}_{}.out'.format(OUTPUT_DIRECTORY, t, hashed_url)
	with open(fn, 'w') as f:
		json.dump(output, f)
	return fn

def compressHTML(html):
	if VERSION == 3:
		compressed_html = binascii.b2a_hex(gzip.compress(bytes(html, 'utf-8'))).decode('utf-8')
	else:
		out = StringIO()
		with gzip.GzipFile(fileobj=out, mode="w") as f:
			f.write(html.encode('utf-8'))
		compressed_html = out.getvalue()
		compressed_html = binascii.b2a_hex(compressed_html).decode('utf-8')
	return compressed_html

scraper = QuoraScraper(args.wait)
logging.info("Connecting to {} on port {}".format(HOST, PORT))
try:
	url = getUrl(EMPTY_REQUEST)
	while True:
		ts = ts = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
		logging.info("[{}] URL = {}".format(ts, url))
		t = int(time())

		html, log, data = None, None, None
		try:
			html = scraper.processUrl(url)
			try:
				log = scraper.processLog(url)
				data = scraper.getQuestion(html)
			except Exception as e:
				logging.error("Bad processing:")
				logging.error(e)
		except Exception as e:
			logging.error("Unable to get HTML:")
			logging.error(e)

		error = False
		if not all([html, log, data]):
			error = True
		if html:
			compressed_html = compressHTML(html)
			output = {
				"html"	: compressed_html,
				"time"	: t,
				"url"	: url
			}
			if data:
				output['data'] = data
				if not data['links']:
					logging.warn("No links on page.")
			if log:
				output['log'] = log

			fn = writeFile(url, output)

			request = {
				"links" : data['links'] if data else list(),
				"url" : url,
				"error" : error,
				"data" : {
					"time" : t,
					"path" : os.path.abspath(fn)
				}
			}
		else:
			request = {
				'links'	: list(),
				'url'	: url,
				'error'	: error,
				'data'	: None
			}
		url = getUrl(request)

except ConnectionRefusedError:
	logging.info("Server unreachable, quitting.")

finally:
	scraper.close()
