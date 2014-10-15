from pyquery import PyQuery as pq
from lxml.etree import tostring
from selenium import webdriver
import json

from pprint import pprint
from time import time

driver = webdriver.PhantomJS()

def processUrl(url):
	global driver
	driver.get(url)
	if driver.execute_script("return $('.ErrorMain');"):
		return None

	scrollRepeat = '''
	function isLoaded() {
		var count = $('.answer_count');
		if(count.length) {
			count = parseInt(count[0].textContent.split(" "));
		} else {
			count = 0;
		}
		return $(".AnswerHeader:not(.feed_item_answer > div > div > div > div.AnswerHeader)").length == count;
	}
	function scroll() {
		$('.pager_next.action_button').click();
	}
	var rep = setInterval(function() {
		if(!isLoaded()) {
			scroll();
		} else {
			clearInterval(rep);
		}
	}, 500);
	'''

	check = '''
		var count = $('.answer_count');
		if(count.length) {
			count = parseInt(count[0].textContent.split(" "));
		} else {
			count = 0;
		}
		return $(".AnswerHeader:not(.feed_item_answer > div > div > div > div.AnswerHeader)").length == count;
	'''

	driver.execute_script(scrollRepeat);

	while not driver.execute_script(check): pass

	parsed = pq(driver.page_source)
	return parsed

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
	parsed = processUrl(url)
	if parsed is None:
		return None

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
			author_info = a.cssselect('a.user')
			if author_info:
				author_info = a.cssselect('a.user')[0].get('href')[1:]
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
	try:
		with open("{}.json".format(int(time())), 'w') as f:
			avg = 0
			for i, q in enumerate(getQuestionPage()):
				start = time()
				data = getQuestion(q)
				if data is None:
					print("{} : (SKIPPED) {}".format(i, q))
				else:
					print("{} : {}".format(i, q))
					avg += time() - start
					f.write(json.dumps(data) + '\n')
	except KeyboardInterrupt:
		print()
		print()
		print(avg / (i + 1))