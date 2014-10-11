from pyquery import PyQuery as pq
from lxml.etree import tostring

from pprint import pprint
def getQuestionPage():
	qs = 'https://www.quora.com/sitemap/questions?page_id='
	#  = 'https://www.quora.com/sitemap/recent?page_id=''
	c = 1
	while True:
		parsed = pq(qs + str(c), headers={'user-agent': 'QuoraScraper'})
		for qElm in parsed('.content > div > div')[0].getchildren():
			yield qElm.getchildren()[0].attrib['href']
		c += 1
def readQuestion(url):
	parsed = pq(url, headers={'user-agent': 'QuoraScraper'})

	question = parsed('div.question_text_edit > h1')[0].text_content()
	details = parsed('.question_details > div')[0].text_content()
	followers = int(parsed('span.count')[0].text_content())

	ret = {
		'url':url,
		'question': question,
		'details':details,
		'followers':followers
	}
	return ret

q = getQuestionPage().__next__()
pprint(readQuestion(q))