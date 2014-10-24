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
		for i, q in enumerate(scrape.getQuestionPage()):
			scrape.driver.delete_all_cookies()
			print("{} : {}".format(i, q))
			data = scrape.processUrl(q)
			if data is None:
				print("\t(SKIPPED)")
			else:
				data = data('.grid_page_center_col')
				if len(data) == 0:
					print("\t(SKIPPED)")
					scrape.logError(q)
				else:
					output.append({
						'html' : binascii.b2a_hex(gzip.compress(tostring(data[0]))).decode('utf-8'),
						'time' : time()
					})
	except KeyboardInterrupt:
		pass
	with open('data/scraped_{}.json'.format(int(time())), 'w') as f:
		f.write('\n'.join([json.dumps(i) for i in output]))