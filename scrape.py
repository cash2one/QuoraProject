from pyquery import PyQuery as pq
from lxml.etree import tostring

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import json

from pprint import pprint
from time import time

import atexit
import logging
from logging import info, warn

logging.basicConfig(level=logging.INFO)

user_agent = ("QuoraScraper")
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = user_agent

driver = webdriver.PhantomJS(service_args=['--load-images=no'], desired_capabilities=dcap)

def processUrl(url):
	global driver

	if url.startswith('https'):
		warn('URL started with "https", replacing with "http"')
		url = url[:4] + url[5:]
	info("\tLoading page")
	driver.get(url)
	info("\tChecking if error page")
	if driver.find_elements_by_id('ErrorMain'):
		return None

	funcs = '''
	function getAnswers() {
		var t_answers = document.getElementsByClassName('AnswerHeader');
		var answers = [];
		for(var i = 0; i < t_answers.length; i++) {
			if(t_answers[i].parentElement.parentElement.parentElement.className != "feed_item_content_related_question") {
				answers.push(t_answers[i]);
			}
		}
		return answers;
	}
	function isLoaded() {
		var count = document.getElementsByClassName('answer_count');
		if(count.length) {
			count = parseInt(count[0].textContent.split(" "));
		} else {
			count = 0;
		}
		return getAnswers().length == count;
	}
	function scroll() {
		var elms = document.getElementsByClassName('pager_next');
		for(var i = 0; i < elms.length; i++) {
			elms[i].click();
		}
	}
	'''

	scrollRepeat = '''
	var rep = setInterval(function() {
		if(!isLoaded()) {
			scroll();
		} else {
			clearInterval(rep);
		}
	}, 500);
	'''

	check = 'return isLoaded();'

	clickOnStuff = '''
		function simulateClick(el) {
			var evt;
			if (document.createEvent) {
				evt = document.createEvent("MouseEvents");
				evt.initMouseEvent("click", true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
			}
			(evt) ? el.dispatchEvent(evt) : (el.click && el.click());
		}
		var elms = Array.prototype.slice.call(document.getElementsByClassName('CollapsedAnswersSectionCollapsed')).concat(
					Array.prototype.slice.call(document.getElementsByClassName('view_comments'))).concat(
					Array.prototype.slice.call(document.getElementsByClassName('comment_replies_show_child_link'))).concat(
					Array.prototype.slice.call(document.getElementsByClassName('more_link')));

		for(var i = 0; i < elms.length; i++) {
			simulateClick(elms[i]);
		}
	'''

	info("\tExecuting main script")
	driver.execute_script(funcs + scrollRepeat);

	info("\tWaiting for answers to load")
	while not driver.execute_script(funcs + check): pass

	info("\tExpanding answers and comment chains")
	driver.execute_script(clickOnStuff)

	info("\tParsing")
	parsed = pq(driver.page_source)
	return parsed

def numToInt(s):
	s = s.replace(',','')
	if not s:
		return 0
	elif s.endswith('k'):
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

	question = parsed('div.question_text_edit > h1')
	if not question:
		question = parsed('h1.review_question_text')
	question = question[0].text_content()

	details = parsed('.question_details > div')[0].text_content()
	followers = parsed('span.count')
	if followers:
		followers = numToInt(followers[0].text_content())
	else:
		followers = 0

	answer_info = []
	answers = parsed('.Answer:not(.ActionBar)')
	c = 0
	info("\tLooping through answers")
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

@atexit.register
def closeBrowser():
	driver.close()

if __name__ == '__main__':
	from sys import argv

	if len(argv) > 1:
		url = argv[1]
		data = getQuestion(url)
		print("{}:".format(url))
		if data is None:
			print("\t(SKIPPED)")
		else:
			pprint(data)
	else:
		try:
			with open("data/{}.json".format(int(time())), 'w') as f:
				avg = 0
				for i, q in enumerate(getQuestionPage()):
					print("{} : {}".format(i, q))
					start = time()
					data = getQuestion(q)
					if data is None:
						print("\t(SKIPPED)")
					else:
						avg += time() - start
						f.write(json.dumps(data) + '\n')
		except KeyboardInterrupt:
			print('\n\n{}'.format(avg / (i + 1)))