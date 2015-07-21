from __future__ import unicode_literals

import sys
sys.path.append('../PyLinear')

from Quora.QuoraScraper import QuoraScraper, dehtml
from pyquery import PyQuery as pq
from pprint import pprint
from lxml.etree import tostring

def parseLogPage():
	print("Parsing html")
	parsed = pq(html)
	entries = []
	for i in parsed.find('.QuestionLog')[0].getchildren()[:-1]:
		top, bottom = i.getchildren()[0].getchildren()
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
		pprint(entry)
		print()
	return entry

if __name__ == '__main__':
	import json
	from Pylinear.feature import getFiles

	actionTypes = set()
	for fn in getFiles('/export/a04/wpovell/logPages'):
		with open(fn) as f:
			html = json.load(f)['html']
		processed = parseLogPage(html)
		for i in processed:
			actionTypes.add(i['actionType'])
	print(actionTypes)