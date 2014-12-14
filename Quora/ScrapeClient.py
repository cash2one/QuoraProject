import sys
VERSION = sys.version_info[0]

import hashlib
import gzip
import socket
import json
import binascii
import os
from datetime import datetime
from time import time

import logging
logging.basicConfig(level=logging.INFO)

from Quora.QuoraScraper import QuoraScraper

if VERSION == 2:
	from StringIO import StringIO
	ConnectionRefusedError = socket.error

EMPTY_REQUEST = {
	"links"	: [],
	"url"	: "",
	"error" : False,
	"data"	: False
}

def getUrl(data):
	'''Takes data and sends to server. Return next job url.'''
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
	'''Takes output data and writes to disk'''
	if not os.path.isdir(OUTPUT_DIRECTORY):
		os.mkdir(OUTPUT_DIRECTORY)
	# Uses hash of url in case two files are made within the same second
	hashed_url = hashlib.md5(url.encode('utf-8')).hexdigest()
	fn = '{}/{}_{}.out'.format(OUTPUT_DIRECTORY, t, hashed_url)

	with open(fn, 'w') as f:
		json.dump(output, f)
	return fn

def compressHTML(html):
	'''Compresses html with gzip and returns hex-encoded binary string'''
	if VERSION == 3:
		compressed_html = binascii.b2a_hex(gzip.compress(bytes(html, 'utf-8'))).decode('utf-8')
	else:
		out = StringIO()
		with gzip.GzipFile(fileobj=out, mode="w") as f:
			f.write(html.encode('utf-8'))
		compressed_html = out.getvalue()
		compressed_html = binascii.b2a_hex(compressed_html).decode('utf-8')
	return compressed_html

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description='Start Quora scraping client.')
	parser.add_argument('HOST', type=str, default="localhost", nargs='?', help='address of server')
	parser.add_argument('PORT', type=int, default=9999, nargs='?', help='port server is listening on')
	parser.add_argument('-o', '--output', type=str, default=None, nargs=1, help="directory to write output to")
	parser.add_argument('-t', '--wait', type=int, default=7, nargs=1, help="how long to wait between requets")
	args = parser.parse_args()

	HOST = args.HOST
	PORT = args.PORT

	# Directory to write output files to
	if args.output is None:
		OUTPUT_DIRECTORY = "data"
	else:
		OUTPUT_DIRECTORY = args.output[0]

	scraper = QuoraScraper(args.wait)
	logging.info("Connecting to {} on port {}".format(HOST, PORT))
	try:
		# Send empty request to get first job
		url = getUrl(EMPTY_REQUEST)
		while True:
			# Logging time
			ts = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
			logging.info("[{}] URL = {}".format(ts, url))

			# Output file time
			t = int(time())

			# Scrape and process data
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
				# Data sent written to disk
				output = {
					"html"	: compressed_html,
					"time"	: t,
					"url"	: url,
					# data
					# log
				}
				if data:
					output['data'] = data
					if not data['links']:
						logging.warn("No links on page.")
				if log:
					output['log'] = log

				fn = writeFile(url, output)

				# Data sent back to server
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
				# Error sent back to server
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