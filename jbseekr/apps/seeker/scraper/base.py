from bs4 import BeautifulSoup
import requests

class BS4Scraper:

	def __init__(self, source):
		self.source = source
		self.url = None
		self.content = None
		# self.title = None
		self.parser = None

	def retrieve_content(self, url=None):
		response = requests.get(self.url)
		# print(f"response ---> {response}")
		self.content = response.text
		# print(f"response.text ---> {response.text}")
		return self.content

	# @property
	# def title(self):
	# 	if not self.content:
	# 		self.retrieve_content()
	# 	return

	def parse(self):
		if not self.content:
			self.retrieve_content()
		self.parser = BeautifulSoup(self.content, "html.parser")

	@staticmethod
	def search(role, location):
		pass




