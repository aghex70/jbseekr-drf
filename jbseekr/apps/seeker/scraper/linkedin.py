import json
from urllib.parse import urlencode

from .base import BS4Scraper


class LinkedinScraper(BS4Scraper):

	def __init__(self):
		super().__init__(source="Linkedin", origin="https://es.linkedin.com/jobs/search")

	def filter_positions(self, **kwargs):
		if not kwargs:
			kwargs = {
				"keywords": "Python",
				"location": "Madrid",
			}
		else:
			kwargs["keywords"] = kwargs.pop("role")

		self.origin += f"?{urlencode(kwargs)}"
		self.retrieve_content(url=self.origin)

	def retrieve_positions_urls(self):
		self.parse_content()
		positions_urls = [position.get("href") for position in self.parser.select("a.result-card__full-card-link")]
		return positions_urls

	def retrieve_position(self, position_url):
		return self.retrieve_content(url=position_url)

	def retrieve_position_details(self):
		self.parse_content()
		details = json.loads(self.parser.find('script', type='application/ld+json').contents[0])
		return details
