import json
import urllib2

from Quora.QuoraScraper import QuoraScraper

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description='Complete previously scraped data.')
	parser.add_argument('EMAIL', help='Quora account email.')
	parser.add_argument('PASS', help='Quora account password.')
	parser.add_argument('-r', '--read', default="fileInfo.txt", help='File to read data info from.')
	parser.add_argument('-o', '--output', default="completeData.txt", help="File to write results to.")
	parser.add_argument('-s', '--seen', default="seenData.txt", help="File to write seen files to.")
	args = parser.parse_args()

	s_nl = QuoraScraper()
	s = QuoraScraper(True, args.EMAIL, args.PASS)

	f = open(args.read)
	o = open(args.output, 'a')
	with open(args.seen) as seenF:
		data = set(seenF.read().split('\n'))

	seen = open(args.seen, 'a')
	c = 0
	try:
		for line in f.readlines():
			fn, url, hasData, hasTime = json.loads(line)
			if fn in data or not hasData:
				continue
			if not hasTime:
				hasTime = s_nl.processLog(url)
			topics = s.getRealTopics(url)
			o.write(json.dumps((fn, url, hasTime, topics)) + '\n')
			seen.write(fn + '\n')
			print(c)
			c += 1
	except KeyboardInterrupt:
		pass
	finally:
		s_nl.close()
		s.close()

		f.close()
		o.close()
		seen.close()