import sys
VERSION = sys.version_info[0]

if VERSION == 3:
	import socketserver
	from urllib.parse import quote
else:
	import SocketServer as socketserver
	from urllib import quote

import socket
import json
import os.path
import itertools
import random
from datetime import datetime

import logging
logging.basicConfig(level=logging.INFO)

from Quora.QuoraScraper import QuoraScraper

# Prevents "Address already in use" error
socketserver.TCPServer.allow_reuse_address = True

class ScrapeServer(socketserver.StreamRequestHandler):
	QUEUE_REFILL = 10

	@staticmethod
	def logError(url):
		'''Log problematic url to ERROR_FILE for later reference'''
		with open(ERROR_FILE, 'a') as f:
			f.write(url + '\n')

	def checkQueue(self):
		'''Refills url queue from seeder if empty'''
		if len(server.urls_to_use) == 0:
			c = 0
			for i in self.server.urlGen:
				if not i in self.server.directory:
					self.server.urls_to_use.add(i)
					c += 1
				if c >= self.QUEUE_REFILL:
					break

	def handle(self):
		'''Handles job requests from clients'''
		data = self.rfile.readline().strip()
		data = json.loads(data.decode('utf-8'))
		ts = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
		# Initial request
		if not data['url']:
			logging.info("[{}] {} {}".format(ts, self.client_address, "REQUEST URL"))
		# Request with data
		else:
			logging.info("[{}] {} {}".format(ts, self.client_address, "RETURN URL = {}".format(data['url'])))

		# Write data to disk if exists
		if data['data']:
			self.server.directory[data['url']] = data["data"]
			with open(DIRECTORY_FILE, 'a') as f:
				f.write(json.dumps({data['url'] : data["data"]}) + '\n')

		# Add scraped links to queue
		for url in data['links']:
			if url not in self.server.directory:
				self.server.urls_to_use.add(url)

		# If there was a problem, log it
		if data['error']:
			self.logError(data['url'])

		# Refill queue
		self.checkQueue()

		# Choose a random url from queue and return it
		return_url = random.sample(self.server.urls_to_use, 1)[0]
		self.server.urls_to_use.remove(return_url)
		self.wfile.write((return_url + '\n ').encode('utf-8'))

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description='Start Quora scraping server.')
	parser.add_argument('PORT', type=int, default=9999, nargs='?', help='port to run server on')
	parser.add_argument('-o', '--output', type=str, default=None, nargs=1, help="directory to write output to")
	args = parser.parse_args()

	# Directory to write directory, link, and error files to
	if args.output is None:
		DATA_DIR = "data"
	else:
		DATA_DIR = args.output[0]
	if not os.path.isdir(DATA_DIR):
		os.mkdir(DATA_DIR)

	DIRECTORY_FILE = DATA_DIR + '/directory.json'
	LINKS_FILE = DATA_DIR + '/links.json'
	ERROR_FILE = DATA_DIR + '/error.log'

	# Empty string must be used here
	# localhost/hostname cause clients to be unable to connect
	HOST = '' 
	PORT = args.PORT

	logging.info("Starting server on {}:{}".format(HOST, PORT))
	server = socketserver.TCPServer((HOST, PORT), ScrapeServer)

	### ADD GLOBAL DATA TO SERVER INSTANCE ###

	# Seen links
	server.directory = {}
	# Queue
	server.urls_to_use = set()
	# Seeder
	server.urlGen = QuoraScraper.getQuestionPage()

	# Load previously scraped links
	if os.path.isfile(DIRECTORY_FILE):
		with open(DIRECTORY_FILE) as f:
			data = f.read().strip().split('\n')
			server.directory = {}
			for entry in data:
				entry = json.loads(entry)
				key = entry.keys()[0]
				server.directory[key] = entry[key]
	else:
		f = open(DIRECTORY_FILE, 'w')
		f.close()

	# Load previously saved seed links
	if os.path.isfile(LINKS_FILE):
		with open(LINKS_FILE) as f:
			for url in json.load(f):
				server.urls_to_use.add(url)
	##########################################

	# Clients should not connect until execution reaches this point
	try:
		logging.info("Server ready")
		server.serve_forever()
	except KeyboardInterrupt:
		pass
	finally:
		logging.info("Shutting down server")
		server.shutdown()
		# qdel sends a SIGKILL, which is uncachable, so links will never be stored
		with open(LINKS_FILE, 'w') as f:
			json.dump(list(server.urls_to_use), f)