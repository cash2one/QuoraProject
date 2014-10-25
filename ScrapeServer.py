import socketserver
import json
import os.path
import itertools
import argparse
from queue import Queue

import logging
logging.basicConfig(level=logging.INFO)

from QuoraScraper import QuoraScraper

DIRECTORY_FILE = 'data/directory.json'
LINKS_FILE = 'data/links.json'
ERROR_FILE = 'data/error.log'
QUEUE_REFILL = 10

# Prevents "Address already in use" error
socketserver.TCPServer.allow_reuse_address = True

class ScrapeServer(socketserver.StreamRequestHandler):
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
				if c >= QUEUE_REFILL:
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

		for url in data['links']:
			if url not in self.server.directory:
				self.server.queue.put(url)

		if data['error']:
			self.logError(data['url'])

		self.checkQueue()
		self.wfile.write(bytes(self.server.queue.get() + '\n ', 'utf-8'))

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Start Quora scraping server.')
	parser.add_argument('PORT', type=int, default=9999, nargs='?', help='port to run server on')
	args = parser.parse_args()

	HOST = "localhost"
	PORT = args.PORT

	logging.info("Starting server on port {}".format(PORT))
	server = socketserver.TCPServer((HOST, PORT), ScrapeServer)

	### ADD GLOBAL DATA TO SERVER INSTANCE ###
	server.directory = {}
	server.queue = Queue()
	server.urlGen = QuoraScraper.getQuestionPage()

	if os.path.isfile(DIRECTORY_FILE):
		with open(DIRECTORY_FILE) as f:
			server.directory = json.load(f)

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
		with open(DIRECTORY_FILE, 'w') as f:
			json.dump(server.directory, f)
		with open(LINKS_FILE, 'w') as f:
			json.dump(list(server.queue.queue), f)