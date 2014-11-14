import sys
VERSION = sys.version_info[0]

if VERSION == 3:
	import socketserver
	from queue import Queue
else:
	import SocketServer as socketserver
	from Queue import Queue

import socket
import json
import os.path
import itertools

import logging
logging.basicConfig(level=logging.INFO)

from QuoraScraper import QuoraScraper

# Prevents "Address already in use" error
socketserver.TCPServer.allow_reuse_address = True

class ScrapeServer(socketserver.StreamRequestHandler):
	QUEUE_REFILL = 10

	@staticmethod
	def logError(url):
		with open(ERROR_FILE, 'a') as f:
			f.write(url + '\n')

	def checkQueue(self):
		if self.server.queue.empty():
			c = 0
			for i in self.server.urlGen:
				if not i in self.server.directory:
					self.server.queue.put(i)
					c += 1
				if c >= self.QUEUE_REFILL:
					break

	def handle(self):
		data = self.rfile.readline().strip()
		data = json.loads(data.decode('utf-8'))
		if not data['url']:
			logging.info("{} : {}".format(self.client_address, "REQUEST URL"))
		else:
			logging.info("{} : {}".format(self.client_address, "RETURN URL = {}".format(data['url'])))

		if data['data']:
			self.server.directory[data['url']] = data["data"]
			with open(DIRECTORY_FILE, 'a') as f:
				f.write(json.dumps({data['url'] : data["data"]}) + '\n')

		for url in data['links']:
			if url not in self.server.directory:
				self.server.queue.put(url)

		if data['error']:
			self.logError(data['url'])

		self.checkQueue()
		self.wfile.write((self.server.queue.get() + '\n ').encode('utf-8'))

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description='Start Quora scraping server.')
	parser.add_argument('PORT', type=int, default=9999, nargs='?', help='port to run server on')
	parser.add_argument('-o', '--output', type=str, default=None, nargs=1, help="directory to write output to")
	args = parser.parse_args()

	if args.output is None:
		DATA_DIR = "data"
	else:
		DATA_DIR = args.output[0]

	DIRECTORY_FILE = DATA_DIR + '/directory.json'
	LINKS_FILE = DATA_DIR + '/links.json'
	ERROR_FILE = DATA_DIR + '/error.log'

	HOST = '' 
	PORT = args.PORT

	logging.info("Starting server on {}:{}".format(HOST, PORT))
	server = socketserver.TCPServer((HOST, PORT), ScrapeServer)

	### ADD GLOBAL DATA TO SERVER INSTANCE ###
	server.directory = {}
	server.queue = Queue()
	server.urlGen = QuoraScraper.getQuestionPage()

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

	if os.path.isfile(LINKS_FILE):
		with open(LINKS_FILE) as f:
			for url in json.load(f):
				server.queue.put(url)
	##########################################

	try:
		logging.info("Server ready")
		server.serve_forever()
	except KeyboardInterrupt:
		pass
	finally:
		logging.info("Shutting down server")
		server.shutdown()
		if not os.path.isdir(DATA_DIR):
			os.mkdir(DATA_DIR)
		with open(LINKS_FILE, 'w') as f:
			json.dump(list(server.queue.queue), f)