import scrape
from time import time
from lxml.etree import tostring
import json
import gzip
import binascii
import logging

if __name__ == '__main__':
	output = []
	try:
		for i, url in enumerate(scrape.getQuestionPage()):
			scrape.driver.delete_all_cookies()
			print("{} : {}".format(i, url))
			data = scrape.processUrl(url)
			if data is None:
				print("\t(SKIPPED)")
			else:
				data = data('.grid_page_center_col')
				if len(data) == 0:
					print("\t(SKIPPED)")
					scrape.logError(url)
				else:
					output.append({
						'html' : binascii.b2a_hex(gzip.compress(tostring(data[0]))).decode('utf-8'),
						'time' : time(),
						'url'  : url
					})
	except KeyboardInterrupt:
		pass
	with open('data/scraped_{}.json'.format(int(time())), 'w') as f:
		f.write('\n'.join([json.dumps(i) for i in output]))