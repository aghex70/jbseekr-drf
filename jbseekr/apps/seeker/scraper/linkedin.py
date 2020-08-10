from urllib.parse import urlencode

from .base import BS4Scraper
import re

from ..models import Position

class LinkedinScraper(BS4Scraper):

	def __init__(self, source):
		super().__init__(source=source)
		self.url = "https://es.linkedin.com/jobs/search"

	def filter_positions(self, position, location):
		filters = {
			"role": position,
			"location": location,
		}

		# print(f"self.url ---> {self.url}")
		self.url += f"?{urlencode(filters)}"
		# print(f"self.url ---> {self.url}")
		self.retrieve_content()

	def parse_positions(self):
		self.parse()
		# print(f"self.parse() --->{self.parse()}")
		positions_links = [position.get("href") for position in self.parser.select("a.result-card__full-card-link")]
		# print(f"positions ---> {positions_links}")
		return positions_links

	def retrieve_position(self, position_link):
		self.url = position_link
		return self.retrieve_content(url=position_link)

	def retrieve_position_details(self):
		self.parse()
		title = self.parser.select(".topcard__title")[0].text
		contents = self.parser.select(".show-more-less-html__markup")[0].contents
		cleansed_contents = \
			[re.sub("<.?strong>|<.?u>|<.?p>|</li>|<ul>", "", re.sub("<br.?>|<li>|</ul>", "\n", str(content))) for content in contents]
		details = "".join(cleansed_contents)
		print(f"self.url ---> {self.url}")
		return title, details

if __name__ == "__main__":
	parser = LinkedinScraper(source="Linkedin")
	parser.filter_positions(position="Python", location="Madrid")
	parsed_positions = parser.parse_positions()
	for pos in parsed_positions[0:10]:
		position = parser.retrieve_position(pos)
		title, details = parser.retrieve_position_details()
		print(f"title ----> {title}")
		print(f"details ----> {details}")
		Position.objects.create(title=title, description=details, url=parser.url)