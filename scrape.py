from pyquery import PyQuery as pq
from lxml.etree import tostring

from pprint import pprint

def numToInt(s):
	s = s.replace(',','')
	if s.endswith('k'):
		return int(float(s[:-1]) * 1000)
	elif s.endswith('m'):
		return int(float(s[:-1] * 1000000))
	else:
		return int(s)

def getQuestionPage():
	qs = 'https://www.quora.com/sitemap/questions?page_id='
	#  = 'https://www.quora.com/sitemap/recent?page_id=''
	c = 1
	while True:
		parsed = pq(qs + str(c), headers={'user-agent': 'QuoraScraper'})
		for qElm in parsed('.content > div > div')[0].getchildren():
			yield qElm.getchildren()[0].attrib['href']
		c += 1

def getQuestion(url):
	parsed = pq(url, headers={'user-agent': 'QuoraScraper'})

	question = parsed('div.question_text_edit > h1')[0].text_content()
	details = parsed('.question_details > div')[0].text_content()
	followers = numToInt(parsed('span.count')[0].text_content())

	answer_info = []
	answers = parsed('.Answer:not(.ActionBar)')
	c = 0
	for a in answers:
		upvotes = numToInt(a.cssselect('a.vote_item_link > span')[0].text_content())
		answer_text = a.cssselect('div.TruncatedAnswer')
		if answer_text:
			author_info = a.cssselect('a.user')[0].attrib['href'][1:]
			answer_text = answer_text[0].text_content()
		else:
			author_info = a.cssselect('.author_info > a')[0].get('href')[1:]
			answer_text = a.cssselect('.ExpandedAnswer > div > div')[0].text_content()

		answer_info.append({
			'author':author_info,
			'text': answer_text,
			'upvotes': upvotes
		})

	ret = {
		'url':url,
		'question': question,
		'details':details,
		'followers':followers,
		'answers':answer_info
	}

	return ret

def getUser(user):
	url = 'https://www.quora.com/' + user
	parsed = pq(url, headers={'user-agent': 'QuoraScraper'})

	questions, answers, posts, followers, following, edits = [numToInt(i.text_content()) for i in parsed('span.profile_count')]

	ret = {
		'user': user,
		'questions': questions,
		'answers': answers,
		'posts': posts,
		'followers': followers,
		'following': following,
		'edits': edits
	}

	return ret

if __name__ == '__main__':
	print("TESTING:")
	print("\n= Get Question =")
	q = getQuestionPage().__next__()
	print(q)
	pprint(getQuestion(q))

	print('\n= Complex Question =')
	q = 'https://www.quora.com/What-are-some-of-the-best-rare-natural-phenomena-that-occur-on-Earth'
	pprint(getQuestion(q))

	print('\n= User =')
	pprint(getUser('Robert-Love-1'))