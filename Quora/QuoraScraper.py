# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
VERSION = sys.version_info[0]

from pyquery import PyQuery as pq
import datetime as dt
from datetime import datetime, timedelta

if VERSION == 3:
	from urllib.parse import quote
else:
	from urllib import quote

import os
import re
from time import time, sleep

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from lxml.etree import tostring

from Quora.util.DataHolder import DataHolder

import numpy
import logging
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)


############### Thanks to xperroni/bit4 from http://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python

from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
import re

class _HTMLToText(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self._buf = []
		self.hide_output = False

	def handle_starttag(self, tag, attrs):
		# <p> and <br> add newline
		if tag in ('p', 'br') and not self.hide_output:
			self._buf.append('\n')
		elif tag in ('script', 'style'):
			self.hide_output = True

	def handle_startendtag(self, tag, attrs):
		if tag == 'br':
			self._buf.append('\n')

	def handle_endtag(self, tag):
		if tag == 'p':
			self._buf.append('\n')
		elif tag in ('script', 'style'):
			self.hide_output = False

	def handle_data(self, text):
		if text and not self.hide_output:
			self._buf.append(re.sub(r'\s+', ' ', text))

	def handle_entityref(self, name):
		if name in name2codepoint and not self.hide_output:
			c = unichr(name2codepoint[name])
			self._buf.append(c)

	def handle_charref(self, name):
		if not self.hide_output:
			n = int(name[1:], 16) if name.startswith('x') else int(name)
			self._buf.append(unichr(n))

	def get_text(self):
		return re.sub(r' +', ' ', ''.join(self._buf))


def dehtml(text):
	'''Takes HTML and returns a plain-text string representation'''
	parser = _HTMLToText()
	parser.feed(text)
	parser.close()
	return parser.get_text()

#############

class QuoraScraper:
	'''Scrapes and parses data from Quora.com'''
	# These values may be changed for a specific instance
	SLEEP_TIME = 7
	TIMEOUT = 60

	USER_AGENT = "QuoraScraper"
	LOGIN_URL = "https://www.quora.com"

	DAYS = [dt.date(2001, 1, i).strftime('%a') for i in range(1,8)]

	# Javascript functions used in headless browser
	funcs = '''
		// Returns all answers loaded on page
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
		// Determines if number of loaded answers matches count at top of page
		function isLoaded() {
			var count = document.getElementsByClassName('answer_count');
			if(count.length) {
				count = parseInt(count[0].textContent.split(" "));
				if (isNaN(count)) {
					count = 0
				}
			} else {
				count = 0;
			}
			return getAnswers().length >= count;
		}
		// Scrolls to bottom of page
		function scroll() {
			var elms = document.getElementsByClassName('pager_next');
			for(var i = 0; i < elms.length; i++) {
				simulateClick(elms[i]);
			}
		}
		// Clicks an element (replacement for jQuery)
		function simulateClick(el) {
			var evt;
			if (document.createEvent) {
				evt = document.createEvent("MouseEvents");
				evt.initMouseEvent("click", true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
			}
			(evt) ? el.dispatchEvent(evt) : (el.click && el.click());
		}
		// Returns last element on page (used for log pages only)
		function getLastElement() {
			var els = document.getElementsByClassName('LogOperation');
			var e = els[els.length - 1];
			return e;
		}
		// Checks if the last element is loaded (used for log pages only)
		function isLoadedLast() {
			return getLastElement().children[0].children[0].innerHTML.startsWith("Question added by");
		}
		// Gets time from log entry
		function getTime() {
			var arr = getLastElement().children[1].textContent.split('•');
			return arr[arr.length - 1].trim();q
		}
		// Gets revision from log entry
		function getRevision() {
			var elms = getLastElement().children;
			return elms[elms.length - 1].textContent;
		}
		// Gets author from log entry
		function getAuthor() {
			var e = getLastElement().children[0].children[0].children[1];
			if(e) {
				return e.attributes['href'].value
			} else {
				return undefined;
			}
		}
	'''

	def __init__(self, login=False, email=None, passwd=None, wait=7, timeout=60):
		self.closed = False
		self.SLEEP_TIME = wait
		self.TIMEOUT = timeout
		self.logged = login

		# Set user-agent
		dcap = dict(DesiredCapabilities.PHANTOMJS)
		dcap["phantomjs.page.settings.userAgent"] = self.USER_AGENT

		# Phantomjs binary location
		ex_path = "/home/wpovell/phantomjs/bin/phantomjs"
		if not os.path.isfile(ex_path):
			ex_path="/usr/local/bin/phantomjs"

		# Disable the loading of images
		self.driver = webdriver.PhantomJS(executable_path=ex_path, service_log_path='/dev/null', service_args=["--ignore-ssl-errors=true", "--load-images=no"], desired_capabilities=dcap)

		if login:
			self.driver.get(self.LOGIN_URL)
			sleep(1)

			self.driver.execute_script("document.getElementsByClassName('header_login_text_box')[0].value = '{}';".format(email))

			self.driver.execute_script("document.getElementsByClassName('header_login_text_box')[1].value = '{}';".format(passwd))

			self.driver.execute_script("document.getElementsByClassName('submit_button')[4].click();")
			c = 0
			while(len(self.driver.find_elements_by_class_name('HomeMain')) == 0):
				if c > 10:
					self.close()
					raise Exception("Timeout")
				if self.driver.find_elements_by_class_name('LoginUserRateLimited'):
					self.close()
					raise Exception("Account Locked")			
				sleep(5)	
				c += 1

	def getRealTopics(self, url):
		if self.logged:
			self.driver.get(url)
			mores = self.driver.find_elements_by_css_selector('.ViewMoreLink > a')
			for i in mores:
				i.click()
			topic_elements = self.driver.find_elements_by_css_selector('a.topic_name')
			topics = []
			for t in topic_elements:
				topics.append(t.get_attribute('href'))
			self.wait(self.SLEEP_TIME)
			return topics
		else:
			return None

	@staticmethod
	def wait(SLEEP_TIME):
		'''Uses gamma function to wait an amount of time randomly-near SLEEP_TIME.
		The idea is to make requests a little more variable and organic.
		'''
		if SLEEP_TIME:
			t = numpy.random.gamma(SLEEP_TIME * 2, 0.5)
		else:
			t = 0

		sleep(t)

	def logout(self):
		self.driver.execute_script("$('.nav_item_link .profile_photo_img').click()")
		logout = self.driver.find_elements_by_css_selector('a.logout')[0]
		self.driver.execute_script("document.getElementsByClassName('logout')[2];")

	def close(self):
		'''Closes headless browser and logs out if needed.
		NOTE: This is very important. Phantomjs processes will never exit if this method isn't called.
		'''
		if self.logged:
			self.logout()

		self.driver.close()
		self.driver.quit()
		self.closed = True

	def processUrl(self, url):
		'''Takes a question url and returns the HTML of the expanded page.
		A headless browser is necessary here since Quora loads pages dynamically with Javascript.
		'''
		# Scraping breaks if https url is used
		if url.startswith('https'):
			logging.warn('URL started with "https", replacing with "http"')
			url = url.replace('https', 'http', 1)

		logging.debug("\tLoading page")

		# Scraper gets block if cookies persist
		self.driver.delete_all_cookies()
		self.driver.get(url)

		logging.debug("\tChecking if error page")
		if self.driver.find_elements_by_id('ErrorMain'):
			return None

		# Autoscrolls page every 0.5s
		scrollRepeat = '''
		var rep = setInterval(function() {
			if(!isLoaded()) {
				scroll();
			} else {
				clearInterval(rep);
			}
		}, 500);
		'''

		# Determines if all questions have been loaded
		# See QuoraScraper.funcs
		check = 'return isLoaded();'

		# Clicks on comments, collapsed answers, etc.
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
		self.driver.execute_script(self.funcs + scrollRepeat);

		logging.debug("\tWaiting for answers to load")
		start = time()
		num_questions = -1
		while not self.driver.execute_script(self.funcs + check):
			qs = self.driver.execute_script(self.funcs + "return getAnswers().length;")
			if qs != num_questions:
				num_questions = qs
				start = time()
			elif time() - start > self.TIMEOUT:
				logging.error("TIMEOUT")
				return None
			sleep(1)

		logging.debug("\tExpanding answers and comment chains")
		self.driver.execute_script(self.funcs + clickOnStuff)

		# Sleep before next request
		logging.debug("\tSleeping")
		self.wait(self.SLEEP_TIME)

		return self.driver.page_source

	def processLog(self, url):
		'''Takes a question url and returns the post time and author.
		TODO: Very similar code as processUrl, maybe combine some parts into single method?
		'''
		url += '/log'

		# Scraping breaks if https url is used
		if url.startswith('https'):
			logging.warn('URL started with "https", replacing with "http"')
			url = url.replace('https', 'http', 1)

		logging.debug("\tLoading log page")

		# Scraper gets block if cookies persist
		self.driver.delete_all_cookies()
		self.driver.get(url)
		self.driver.get(url)

		logging.debug("\tChecking if error page")
		if self.driver.find_elements_by_id('ErrorMain'):
			return None

		scrollRepeat = '''
		var rep = setInterval(function() {
			if(!isLoadedLast()) {
				scroll();
			} else {
				clearInterval(rep);
			}
		}, 500);
		'''

		check = 'return isLoadedLast();'

		logging.debug("\tExecuting main script")
		self.driver.execute_script(self.funcs + scrollRepeat);

		logging.debug("\tWaiting for answers to load")
		start = time()
		revision = -1

		while not self.driver.execute_script(self.funcs + check):
			new_revision = self.driver.execute_script(self.funcs + "return getRevision();")
			if new_revision != revision:
				revision = new_revision
				start = time()
			elif time() - start > self.TIMEOUT:
				logging.error("TIMEOUT")
				return None
			sleep(1)
		sleep(2) # more sleeping bc quora dynamic content is a pain in the ass
		date = self.processDate(self.driver.execute_script(self.funcs + "return getTime();"))
		author = self.driver.execute_script(self.funcs + "return getAuthor();")

		if author:
			author = author[1:]
		ret = {
			"html"   : self.driver.page_source,
			"date"   : date,
			"author" : author
		}

		# Sleep before next request
		logging.debug("\tSleeping")
		self.wait(self.SLEEP_TIME)
		return ret

	@classmethod
	def processDate(cl, s, t=None):
		'''Takes a Quora string date and returns timestamp'''
		if t is None:
			t = datetime.now()
		else:
			t = datetime.fromtimestamp(float(t))

		dh = DataHolder()
		# Type 1, e.g. 14d ago
		if dh.set(re.findall(r'(\d+)d ago', s)):
			date = (t - timedelta(days=int(dh.get()[0]))).replace(hour=0, minute=0, second=0, microsecond=0)
		#Type 2, e.g. 15 Mar, 2014
		elif dh.set(re.findall(r'[\d]{1,2} [A-Za-z]{3}, [\d]{4}', s)):
			date = datetime.strptime(dh.get()[0], "%d %b, %Y")
		#Type 3, e.g. 15 Mar
		elif dh.set(re.findall(r'[\d]{1,2} [A-Za-z]{3}', s)):
			date = datetime.strptime(dh.get()[0], "%d %b")
			date = date.replace(year=t.year)
		#Type 4, e.g. 5h ago
		elif dh.set(re.findall(r'(\d+)h ago', s)):
			date = (t - timedelta(hours=int(dh.get()[0]))).replace(minute=0, second=0, microsecond=0)
		#Type 5, e.g. 3m ago
		elif dh.set(re.findall(r'(\d+)m ago', s)):
			date = (t - timedelta(minutes=int(dh.get()[0]))).replace(second=0, microsecond=0)
		#Type 6, e.g. 3am
		elif dh.set(re.findall(r'([\d]{1,2})(am|pm)', s)):
			d = dh.get()
			d = (d[0][0] + ' ' + d[0][1]).upper()
			d = datetime.strptime(d, '%I %p')
			date = d.replace(year=t.year, month=t.month, day=t.day, minute=0, second=0)
		#Type 7, e.g. yesterday
		elif "yesterday" in s:
			date = (t - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
		#Type 8, e.g. Thu
		elif dh.set(re.findall(r'(Written|Updated) ([A-Za-z]{3})$', s)):
			delta = t.weekday() - cl.DAYS.index(dh.get()[0][1])
			if delta < 0:
				delta += 7
			date = (t - timedelta(days=delta)).replace(hour=0, minute=0, second=0, microsecond=0)
		else:
			logging.error("BAD DATE: {}".format(s))
			return None
		date = int((date - datetime(1970,1,1)).total_seconds())
		return date

	@staticmethod
	def numToInt(s):
		'''Converts Quora upvote count to int'''
		s = s.replace(',','')
		if not s:
			return 0
		elif s.endswith('k'):
			return int(float(s[:-1]) * 1000)
		elif s.endswith('m'):
			return int(float(s[:-1]) * 1000000)
		else:
			return int(s)

	@classmethod
	def getQuestionPage(cl):
		'''Seeds the scraper with questions from sitemap/questions
		Another (currenty unused) source is sitemap/recent
		'''
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
			cl.wait(cl.SLEEP_TIME)

	@staticmethod
	def getAnswerText(answer):
			'''Takes answer html and returns plain-text'''
			# TYPE-1 ANSWER
			# Seen on http://www.quora.com/Would-human-blood-be-a-healthy-drink-for-humans
			answer = answer.cssselect('.ExpandedAnswer')[0]
			text = answer.cssselect('div > div > div')
			if text:
				answer_text = dehtml(tostring(text[0]))
			# TYPE-2 ANSWER
			# Majority of questions
			else:
				s = tostring(answer)
				# Messy way to remove the footer div thrown in at the end, but I don't know of anything better
				s = re.sub(r'<div class="ContentFooter AnswerFooter">.*', '', s)
				answer_text = dehtml(s)

			return answer_text

	@classmethod
	def getQuestion(cl, html, scrapeTime=None):
		'''Takes processed html and returns parsed out data'''

		# For when parseUrl has returned bad data
		if html is None:
			return None

		parsed = pq(html)

		# Star
		star = False
		if parsed('h1 .question_text_icons > span > span'):
			star = True

		# Question
		question = parsed('div.question_text_edit > h1')
		if not question:
			question = parsed('h1.review_question_text')
		question = dehtml(tostring(question[0]))
		question = question.replace(u'\u2605', '', 1)


		# Question details
		details = dehtml(tostring(parsed('.question_details > div')[0]))

		# Followers
		followers = parsed('.follow_button .no_count') + parsed('.follow_button .count')
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
		link_elements = parsed('.logged_out_related_questions_container a') + parsed('.SidebarTopicBestQuestions a') + parsed('.RelatedQuestions a')
		links = set()
		for e in link_elements:
			links.add("http://www.quora.com" + quote(e.attrib['href'].encode('utf-8')))
		links = list(links)

		# Answers
		logging.debug("\tLooping through answers")
		answer_info = []
		answers = parsed('.Answer:not(.ActionBar)')
		c = 0
		for a in answers:
			upvotes = cl.numToInt(a.cssselect('a.vote_item_link > span')[0].text_content())

			author_info = a.cssselect('div.author_info > a')
			if author_info:
				author_info = author_info[0].get('href')[1:]
			else:
				author_info = None # User is anonymous

			answer_text = cl.getAnswerText(a)
			if not answer_text:
				logging.error("No answer text.")

			strDate = str(a.cssselect('.answer_permalink')[0].text_content())
			date = cl.processDate(strDate, scrapeTime)

			answer_info.append({
				'author'    : author_info,
				'text'      : answer_text,
				'upvotes'   : upvotes,
				'time'      : date,
			})

		ret = {
			'question'  : question,
			'topics'    : topics,
			'links'     : links,
			'details'   : details,
			'followers' : followers,
			'answers'   : answer_info
		}

		return ret

	@classmethod
	def getUser(cl, user):
		'''Takes username and returns information from profile.
		This method is static since a headless browser is not needed to load profiles.
		'''
		url = 'http://www.quora.com/' + user
		parsed = pq(url, headers={'user-agent': cl.USER_AGENT})

		questions, answers, posts, followers, following, edits = [cl.numToInt(i.text_content()) for i in parsed('span.profile_count')]

		ret = {
			'user'      : user,
			'questions' : questions,
			'answers'   : answers,
			'posts'     : posts,
			'followers' : followers,
			'following' : following,
			'edits'     : edits,
			'star'      : star
		}

		# Sleep before next request
		cl.wait(cl.SLEEP_TIME)

		return ret

	def __del__(self):
		if not self.closed:
			self.close()

if __name__ == '__main__':
	import argparse
	from pprint import pprint

	logging.basicConfig(level=logging.DEBUG)

	parser = argparse.ArgumentParser(description='Scrape info from Quora question url.')
	parser.add_argument('url', type=str, nargs=1, help='url to scrape')
	url = parser.parse_args().url[0]

	# Scraping breaks if https url is used
	if url.startswith('https'):
		logging.warn('URL started with "https", replacing with "http"')
		url = url.replace('https', 'http', 1)

	try:
		scraper = QuoraScraper(wait=0) # No need to sleep since we're only loading one page
		html = scraper.processUrl(url)
		log = scraper.processLog(url)
		data = scraper.getQuestion(html)
		print("{}:".format(url))
		if data is None:
			print("ERROR")
		else:
			pprint(log)
			pprint(data)
	finally:
		scraper.close()
