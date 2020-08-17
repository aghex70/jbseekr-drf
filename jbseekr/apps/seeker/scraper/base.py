import requests
from requests_html import HTMLSession

from bs4 import BeautifulSoup


class BS4Scraper:

	def __init__(self, source, origin):
		self.source = source
		self.origin = origin
		self.content = None
		self.parser = None

	def retrieve_content(self, url):
		response = requests.get(url)
		self.content = response.text
		return self.content

	def parse_content(self):
		if not self.content:
			self.retrieve_content(self.origin)
		self.parser = BeautifulSoup(self.content, "html.parser")


class RequestsHTMLParser:
	def __init__(self, source, origin):
		self.source = source
		self.origin = origin
		self.session = HTMLSession()
		self.content = None
		self.positions = []

	def fetch_url(self, url):
		self.content = self.session.get(url)
