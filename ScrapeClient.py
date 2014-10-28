import sys
VERSION = sys.version_info[0]

import gzip
import socket
import json
import binascii
import os.path
import argparse
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
args = parser.parse_args()

HOST = args.HOST
PORT = args.PORT

OUTPUT_DIRECTORY = "data"
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

scraper = QuoraScraper()
logging.info("Connecting to {} on port {}".format(HOST, PORT))
try:
	url = getUrl(EMPTY_REQUEST)
	while True:
		logging.info("URL = {}".format(url))
		t = int(time())
		html = scraper.processUrl(url)
		data = scraper.getQuestion(html)

		error = False
		if data is None:
			error = True
			data = False
		else:
			if VERSION == 3:
				compressed_html = binascii.b2a_hex(gzip.compress(bytes(html, 'utf-8'))).decode('utf-8')
			else:
				out = StringIO()
				with gzip.GzipFile(fileobj=out, mode="w") as f:
					f.write(html.encode('utf-8'))
				compressed_html = out.getvalue()
				compressed_html = binascii.b2a_hex(compressed_html).decode('utf-8')
			output = {
				"html"	: compressed_html,
				"data"	: data,
				"time"	: t,
				"url"	: url
			}

			if not os.path.isdir(OUTPUT_DIRECTORY):
				os.mkdir(OUTPUT_DIRECTORY)
			fn = OUTPUT_DIRECTORY + "/" + url.split('/')[-1] + '.out'
			with open(fn, 'w') as f:
				json.dump(output, f)
		if not data['links']:
			logging.warn("No links on page.")
		request = {
			"links" : data['links'],
			"url" : url,
			"error" : error,
			"data" : {
				"time" : t,
				"path" : os.path.abspath(fn)
			}
		}
		url = getUrl(request)

except ConnectionRefusedError:
	logging.info("Server unreachable, quitting.")

finally:
	scraper.close()