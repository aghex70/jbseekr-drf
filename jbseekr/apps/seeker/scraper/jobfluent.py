import re
from urllib.parse import urlencode

from .base import RequestsHTMLParser


class JobFluent(RequestsHTMLParser):

	def __init__(self):
		super().__init__(
			source="JobFluent", origin="https://www.jobfluent.com/es/empleos-madrid")
		self.company_type = "Startup"

	def filter_positions(self, **kwargs):
		kwargs["q"] = kwargs.pop("role", "Python")
		kwargs["page"] = "1"

		self.origin += f"?{urlencode(kwargs)}"
		self.fetch_url(url=self.origin)

	def get_pagination(self):
		jobs_offered = int(self.content.html.find("#results-number")[0].text.split("\n")[1].split(" empleos")[0])
		pages = (jobs_offered // 25) + 1
		return pages

	def retrieve_positions(self):
		pages = self.get_pagination()
		pagination_end = False
		while not pagination_end:
			for i in range(1, pages + 1):
				positions = self.content.html.find(".offer-body")
				for position in positions:
					url = list(position.find(".offer-title")[0].links)[0]
					job_offer = {
						"role": position.find(".offer-title")[0].text,
						"link": re.sub("/es/empleos.*", url, self.content.url),
						"requirements": " - ".join(sorted(list({skill.text for skill in position.find(".label-skill")}))),
						"source": self.source,
						"salary": position.find(".salary")[0].text,
						"category": position.find(".label-category")[0].text,
						"industry": position.find(".label-industry")[0].text,
						"company_type": self.company_type
					}
					self.positions.append(job_offer)
				current_url = self.content.url
				if i == pages:
					pagination_end = True
					break
				next_query_page = f"page={i+1}"
				paginated_url = re.sub('page=[\d]*', next_query_page, current_url)
				self.fetch_url(url=paginated_url)

	def retrieve_position_details(self):
		for position in self.positions:
			self.fetch_url(url=position.get("link"))
			position["description"] = \
				self.content.html.find(".offer-description-content")[0].text.replace("DESCRIPTION\n", "")
			position["company_name"] = self.content.html.find(".company-link")[0].text
			company_details = self.content.html.find(".company-features")[0].find("li")
			for details in company_details:
				if "Sitio web" in details.text:
					position["company_web"] = details.text.split("Sitio web\n")[1]
				elif "Tamaño de la compañía" in details.text:
					position["workers"] = details.text.split("Tamaño de la compañía\n")[1]

		return self.positions
