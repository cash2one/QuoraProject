from __future__ import unicode_literals

import sys
sys.path.append('../PyLinear')

from Quora.QuoraScraper import QuoraScraper, dehtml
from pyquery import PyQuery as pq
from pprint import pprint
from lxml.etree import tostring

def parseLogPage(html):
	qs = QuoraScraper()
	print("Parsing html")
	parsed = pq(html)
	entries = []
	for i in parsed.find('.QuestionLog')[0].getchildren()[:-1]:
		top, bottom = i.getchildren()[0].getchildren()
		if 'AddQuestionRedirectOperationView' in top.attrib['class']:
			text = dehtml(''.join(map(tostring, top.getchildren()[0].getchildren()[:2])))
			user = top.getchildren()[0].getchildren()[3].attrib['href']
			actionType = "MERGED"
		else:
			text = None
			if len(top) > 1:
				text = dehtml(tostring(top[1]))

			actionType = top.getchildren()[0].text
			userElm = top.getchildren()[0].getchildren()
			if len(userElm) > 1:
				user = top.getchildren()[0].getchildren()[1].attrib['href']
			else:
				user = None

		revision, date = bottom.text_content().split(u' \xe2\x80\xa2 ')
		entry = {
			"date"       : qs.processDate(date),
			"revision"   : revision,
			"user"       : user,
			"actionType" : actionType,
			"text"       : text
		}
		entries.append(entry)
	return entries

if __name__ == '__main__':
	import json
	from Pylinear.feature import getFiles
	import binascii
	import gzip
	from StringIO import StringIO

	actionTypes = set()
	c = 0
	for fn in getFiles('/export/a04/wpovell/logPages'):
		if c % 50 == 0:
			print(c)
		c += 1

		with open(fn) as f:
			compressed_html = json.load(f)['html']
		inpF = StringIO(binascii.a2b_hex(compressed_html))
		with gzip.GzipFile(fileobj=inpF) as f:
			html = f.read()
		try:
			processed = parseLogPage(html)
		except Exception as e:
			print(fn)
			raise e
		for i in processed:
			actionTypes.add(i['actionType'])
	print(actionTypes)
