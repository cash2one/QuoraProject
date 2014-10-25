import socket
import sys
import json
import gzip
import binascii
import os.path
import argparse
from time import time

import logging
logging.basicConfig(level=logging.INFO)

from QuoraScraper import QuoraScraper

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
		with sock.makefile() as f:
			url = f.readline().strip()
	finally:
		sock.close()

	return url

try:
	logging.info("Connecting to {} on port {}".format(HOST, PORT))
	url = getUrl(EMPTY_REQUEST)
	scraper = QuoraScraper()
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
			output = {
				"html"	: binascii.b2a_hex(gzip.compress(bytes(html, 'utf-8'))).decode('utf-8'),
				"data"	: data,
				"time"	: t,
				"url"	: url
			}

			if not os.path.isdir(OUTPUT_DIRECTORY):
				os.mkdir(OUTPUT_DIRECTORY)
			fn = OUTPUT_DIRECTORY + "/" + url.split('/')[-1] + '.out'
			with open(fn, 'w') as f:
				json.dump(output, f)

		request = {
			"links" : list(),
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