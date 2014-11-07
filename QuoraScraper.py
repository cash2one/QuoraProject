import sys
VERSION = sys.version_info[0]

from pyquery import PyQuery as pq

if VERSION == 3:
	from urllib.parse import quote
else:
	from urllib import quote

import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import logging
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

class QuoraScraper:
	SLEEP_TIME = 15
	USER_AGENT = "QuoraScraper"

	def __init__(self, wait=15):
		SLEEP_TIME = wait

		# Set user-agent
		dcap = dict(DesiredCapabilities.PHANTOMJS)
		dcap["phantomjs.page.settings.userAgent"] = self.USER_AGENT

		ex_path = "/home/wpovell/phantomjs-1.9.8-linux-i686/bin/phantomjs"
		if not os.path.isfile(ex_path):
			ex_path="/usr/local/bin/phantomjs"

		# Disable the loading of images
		self.driver = webdriver.PhantomJS(executable_path=ex_path, service_log_path='/dev/null', service_args=['--load-images=no'], desired_capabilities=dcap)

	def close(self):
		self.driver.close()

	def processUrl(self, url):
		# Scraping breaks if https url is used
		if url.startswith('https'):
			logging.warn('URL started with "https", replacing with "http"')
			url = url.replace('https', 'http', 1)

		logging.debug("\tLoading page")
		self.driver.delete_all_cookies()
		self.driver.get(url)

		logging.debug("\tChecking if error page")
		if self.driver.find_elements_by_id('ErrorMain'):
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
				simulateClick(elms[i]);
			}
		}
		function simulateClick(el) {
				var evt;
				if (document.createEvent) {
					evt = document.createEvent("MouseEvents");
					evt.initMouseEvent("click", true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
				}
				(evt) ? el.dispatchEvent(evt) : (el.click && el.click());
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
			var elms = Array.prototype.slice.call(document.getElementsByClassName('CollapsedAnswersSectionCollapsed')).concat(
						Array.prototype.slice.call(document.getElementsByClassName('view_comments'))).concat(
						Array.prototype.slice.call(document.getElementsByClassName('comment_replies_show_child_link'))).concat(
						Array.prototype.slice.call(document.getElementsByClassName('more_link')));

			for(var i = 0; i < elms.length; i++) {
				simulateClick(elms[i]);
			}
		'''

		logging.debug("\tExecuting main script")
		self.driver.execute_script(funcs + scrollRepeat);

		logging.debug("\tWaiting for answers to load")
		while not self.driver.execute_script(funcs + check): pass

		logging.debug("\tExpanding answers and comment chains")
		self.driver.execute_script(funcs + clickOnStuff)

		# Sleep before next request
		logging.debug("\tSleeping")
		sleep(self.SLEEP_TIME)

		return self.driver.page_source

	@staticmethod
	def numToInt(s):
		'''Converts Quora upvote count to int'''
		s = s.replace(',','')
		if not s:
			return 0
		elif s.endswith('k'):
			return int(float(s[:-1]) * 1000)
		elif s.endswith('m'):
			return int(float(s[:-1] * 1000000))
		else:
			return int(s)

	@classmethod
	def getQuestionPage(cl):
		qs = 'http://www.quora.com/sitemap/questions?page_id='
		#  = 'http://www.quora.com/sitemap/recent?page_id='
		c = 1
		while True:
			parsed = pq(qs + str(c), headers={'user-agent': cl.USER_AGENT})
			for qElm in parsed('.content > div > div')[0].getchildren():
				url = qElm.getchildren()[0].attrib['href'][7:]
				url = 'http://' + quote(url)
				yield url
			c += 1
			sleep(cl.SLEEP_TIME)

	@classmethod
	def getQuestion(cl, html):
		parsed = pq(html)

		# Question
		question = parsed('div.question_text_edit > h1')
		if not question:
			question = parsed('h1.review_question_text')
		question = question[0].text_content()

		# Question details
		details = parsed('.question_details > div')[0].text_content()

		# Followers
		followers = parsed('span.count')
		if followers:
			followers = cl.numToInt(followers[0].text_content())
		else:
			followers = 0

		# Topics
		tops = parsed('.BreadCrumb a') + parsed('.QuestionTopicListItem a')
		topics = []
		if not tops:
			logging.warn("No topics for question")
		else:
			for t in tops:
				topics.append(t.attrib['href'])

		# Other links
		link_elements = parsed('.logged_out_related_questions_container a') + parsed('.SidebarTopicBestQuestions a')
		links = []
		for e in link_elements:
			links.append("http://www.quora.com" + e.attrib['href'])

		# Answers
		logging.debug("\tLooping through answers")
		answer_info = []
		answers = parsed('.Answer:not(.ActionBar)')
		c = 0
		for a in answers:

			upvotes = cl.numToInt(a.cssselect('a.vote_item_link > span')[0].text_content())

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
				'author'	: author_info,
				'text'		: answer_text,
				'upvotes'	: upvotes
			})

		ret = {
			'question'	: question,
			'topics'	: topics,
			'links'		: links,
			'details'	: details,
			'followers'	: followers,
			'answers'	: answer_info
		}

		return ret

	@classmethod
	def getUser(cl, user):
		url = 'http://www.quora.com/' + user
		parsed = pq(url, headers={'user-agent': cl.USER_AGENT})

		questions, answers, posts, followers, following, edits = [cl.numToInt(i.text_content()) for i in parsed('span.profile_count')]

		ret = {
			'user'		: user,
			'questions'	: questions,
			'answers'	: answers,
			'posts'		: posts,
			'followers'	: followers,
			'following'	: following,
			'edits'		: edits
		}

		# Sleep before next request
		sleep(cl.SLEEP_TIME)

		return ret

if __name__ == '__main__':
	import argparse
	from pprint import pprint

	logging.basicConfig(level=logging.DEBUG)

	parser = argparse.ArgumentParser(description='Scrape info from Quora question url.')
	parser.add_argument('url', type=str, nargs=1, help='url to scrape')
	url = parser.parse_args().url[0]

	try:
		scraper = QuoraScraper()
		html = scraper.processUrl(url)
		data = scraper.getQuestion(html)
		print("{}:".format(url))
		if data is None:
			print("ERROR")
		else:
			pprint(data)
	finally:
		scraper.close()