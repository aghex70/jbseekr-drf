import json

from contextlib import suppress

from .base import BS4Scraper

ORIGIN_BY_ROLE = {
	"Python": "/python-jobs",
	"Java": "/search?query=&industry[]=49&type=Permanent%3BContract",
	"Cloud": "/search?query=&industry[]=28&type=Permanent%3BContract",
	"Devops": "/search?query=&industry[]=4&type=Permanent%3BContract"
}


class FRGScraper(BS4Scraper):

	def __init__(self):
		self.location = None
		self.role = None
		self.positions = None
		self.filtered_positions = []
		super().__init__(source="FRG", origin="https://www.frgconsulting.com")

	def filter_positions(self, **kwargs):
		if not kwargs:
			kwargs = {
				"role": "Python",
				"location": "Madrid",
			}
		self.location = kwargs.get("location").lower().capitalize()
		self.role = kwargs.get("role").lower().capitalize()
		self.origin += ORIGIN_BY_ROLE.get(self.role) + "?page=1"
		self.retrieve_content(url=self.origin)

	def retrieve_positions(self):
		self.parse_content()
		pages = self.retrieve_pagination()
		self.positions = self.parser.find_all(class_="item new")
		if pages > 1:
			for page in range(2, pages+1):
				self.origin = self.origin.replace("?page="+str(page-1), "?page="+str(page))
				self.retrieve_content(url=self.origin)
				self.parse_content()
				self.positions = [*self.positions, *self.parser.find_all(class_="item new")]

	def retrieve_pagination(self):
		pages = self.parser.find(class_="top-pagination").find_all("li")
		filtered_pages = []
		for page in pages:
			with suppress(ValueError):
				filtered_pages.append(int(str(page.text)))
		return max(filtered_pages)

	def filter_positions_details(self):
		skip = False
		for position in self.positions:
			job_details = {}
			position_details = position.find(class_="details").find_all("li")
			for detail in position_details:
				if "Salary" in detail.text:
					job_details["salary"] = detail.text.split("Salary:")[1].strip()
				elif "Location" in detail.text:
					location = detail.text.split("Location:")[1].strip()
					# Can't filter by date, so if location doesn't match our desired location, skip job position
					if self.location not in location:
						print(f"location {location} SKIP!!!!")
						skip = True
						break
				elif "Date Posted" in detail.text:
					job_details["posted_date"] = detail.text.split("Date Posted:")[1].strip()
			if skip:
				skip = not skip
				continue

			position_url = position.find(class_="btn btn-primary-theme btn-view")['href']
			job_details["url"] = position_url
			job_details["location"] = self.role
			job_details["source"] = self.source
			job_details["role"] = self.role
			self.filtered_positions.append(job_details)

	def fill_position_details(self):
		for position in self.filtered_positions:
			self.origin = position.get("url")
			self.retrieve_content(url=self.origin)
			self.parse_content()
			description = self.parser.find(class_="padding-top-job").text
			position['description'] = description
		return self.filtered_positions
