import re
import json
from json import JSONDecodeError
from datetime import datetime

from selenium.common.exceptions import InvalidSessionIdException

from .base import BaseCrawler


class InfojobsCrawler(BaseCrawler):

	def __init__(self):
		self.origin = "https://developer.infojobs.net/test-console/console.xhtml?operationEntityField=-offer" + \
					  "&methodfield=GET&versionfield=1&hmethodfield=LIST"
		self.url = None
		self.role = None
		self.location = None
		self.positions = []
		self.wrapped_positions = []
		self.detailed_positions = []
		super().__init__(source="Infojobs")

	def execute(self):
		self.open()
		self.get_url(self.origin)
		home_title = "InfoJobs Developer Site - Test Console"
		self.wait_until_title_contains_keyword(home_title)

	def search_jobs(self, **kwargs):
		self.role = kwargs.get("role", "Python").capitalize()
		self.location = kwargs.get("location", "Madrid").capitalize()
		self.fill_role(self.role)
		self.fill_location(self.location)
		self.set_update_desc_order()
		self.submit_search()
		self.wait_implicit_time(2)
		self.retrieve_positions()
		self.close()

	def fill_role(self, role):
		api_inputbox = self.get_by_id(id="apiuri")
		api_inputbox.send_keys(f"?q={role}")

	def fill_location(self, location):
		api_inputbox = self.get_by_id(id="apiuri")
		api_inputbox.send_keys(f"&province={location}")

	def set_update_desc_order(self):
		api_inputbox = self.get_by_id(id="apiuri")
		api_inputbox.send_keys(f"&order=updated-desc")

	def submit_search(self):
		search_button = self.get_by_id(id="send-button")
		search_button.click()

	def retrieve_positions(self):
		response = json.loads(self.get_by_id(id="formattedBody").text.replace(")\"\"", ")\""), strict=False)
		self.positions = response.get("items")
		self.retrieve_paginated_positions()

	@staticmethod
	def manual_parse_json(text):
		empty_reqs = re.sub(r'"requirementMin": ".*"', '"requirementMin": ""', text)
		empty_new_lines = re.sub(r'\n', '', re.sub(r'  ', '', empty_reqs))

		conflicting_fragments = ["hash maps", "data analysis", "data wrangling"]
		for fragment in conflicting_fragments:
			empty_new_lines = empty_new_lines.replace(f'"{fragment}"', fragment)
		return empty_new_lines

	def retrieve_paginated_positions(self):
		# Obtain only two more pages
		for index in range(2, 5):
			api_inputbox = self.get_by_id(id="apiuri")
			inputbox_text = api_inputbox.get_attribute("value")
			api_inputbox.clear()
			current_page = str(int(inputbox_text.split("page=")[1])+1) \
				if 'page' in inputbox_text else "2"
			api_inputbox.send_keys(f"{inputbox_text.split('&page')[0]}&page={current_page}")
			self.submit_search()
			self.wait_implicit_time(2)
			try:
				response = json.loads(self.get_by_id(id="formattedBody").text.replace(")\"\"", ")\""), strict=False)
			except json.JSONDecodeError as exc:
				# Manually parse json
				response = json.loads(
					self.manual_parse_json(self.get_by_id(id="formattedBody").text.replace(")\"\"", ")\"")), strict=False)
			self.positions = [*response.get("items"), *self.positions]

		for position in self.positions:
			position['company_description'] = position.pop('description', None)

	@staticmethod
	def wrap_salary(minimum_salary, maximum_salary):
		salary = None
		if minimum_salary and maximum_salary:
			salary = f"{minimum_salary} - {maximum_salary}"
		elif minimum_salary:
			salary = f"{minimum_salary}+"
		elif maximum_salary:
			salary = f"{maximum_salary}"
		return salary

	def wrap_positions(self):
		for position in self.positions:
			minimum_salary = position.get("salaryMin", {}).get("value")
			maximum_salary = position.get("salaryMax", {}).get("value")
			wrapped_position = {
				"company_name": position.get("author").get("name"),
				"id": position.get("id"),
				"role": position.get("title"),
				"city": position.get("city"),
				"location": position.get("province").get("value"),
				"description": position.get("description"),
				"posted_date": datetime.strptime(position.get("published"), "%Y-%m-%dT%H:%M:%S.000Z"),
				"modified_date": datetime.strptime(position.get("updated"), "%Y-%m-%dT%H:%M:%S.000Z"),
				"top_skills": position.get("top_skills"),
				"source": self.source,
				"url": position.get("link"),
				"keywords": position.get("keywords"),
				"highlighted": position.get("highlighted"),
				"consulting_firm": position.get("consulting_firm"),
				"closed": position.get("closed"),
				"salary": self.wrap_salary(minimum_salary, maximum_salary),
				"experience": position.get("experienceMin").get("value"),
				"contract_type": position.get("contract_type"),
			}
			self.wrapped_positions.append(wrapped_position)

	def reset_session(self):
		try:
			self.close()
		except Exception:
			pass
		self.open()
		self.get_url(self.origin)
		home_title = "InfoJobs Developer Site - Test Console"
		self.wait_until_title_contains_keyword(home_title)

	def retrieve_details(self):
		self.open()
		self.get_url(self.origin)
		home_title = "InfoJobs Developer Site - Test Console"
		self.wait_until_title_contains_keyword(home_title)
		self.retrieve_position_details()
		self.wrap_positions()
		self.close()
		return self.wrapped_positions

	def retrieve_position_details(self):
		i = 0
		while i < len(self.positions):
			try:
				position_id = self.positions[i].get("id")
				api_inputbox = self.get_by_id(id="apiuri")
				api_inputbox.clear()
				api_inputbox.send_keys(f"https://api.infojobs.net/api/7/offer/{position_id}")
				self.submit_search()
				self.wait_implicit_time(0.5)
				response = json.loads(self.get_by_id(id="formattedBody").text.replace(")\"\"", ")\""), strict=False)
				position_details = {
					"company_url": response.get("profile").get("url"),
					"description": response.get("description"),
					"company_description": response.get("profile").get("description"),
					"workers": response.get("profile").get("numberWorkers"),
					"address": response.get("fiscalAddress"),
					"top_skills":
						sorted([skill.get("skill").capitalize() for skill in response.get("skillsList")]),
					"job_level": response.get("jobLevel").get("value"),
					"staff_in_charge": response.get("staffInCharge", {}).get("value"),
					"contract_type": response.get("contractType", {}).get("value"),
				}
				updated_position = {**self.positions[i], **position_details}
				self.detailed_positions.append(updated_position)

			except JSONDecodeError:
				cleansed_line = self.cleanse_fields(self.get_by_id(id="formattedBody").text)
				position_details = {
					"company_url": cleansed_line.get("company_url"),
					"description": cleansed_line.get("description"),
					"company_description": cleansed_line.get("company_description"),
					"workers": cleansed_line.get("workers"),
					"address": cleansed_line.get("address"),
					"top_skills": cleansed_line.get("top_skills"),
					"job_level": cleansed_line.get("job_level"),
					"staff_in_charge": cleansed_line.get("staff_in_charge"),
					"contract_type": cleansed_line.get("contract_type"),
				}
				updated_position = {**self.positions[i], **position_details}
				self.detailed_positions.append(updated_position)

			except InvalidSessionIdException:
				self.reset_session()
				continue
			i += 1
		self.positions = self.detailed_positions
		return self.positions

	def cleanse_fields(self, line):
		cleansed_fields = {
			"company_url": self.retrieve_raw_field(line, "web", "web", "numberWorkers"),
			"description": self.retrieve_raw_field(line, "description", "minRequirements", "desiredRequirements"),
			"company_description": self.retrieve_raw_field(line, "description", "description", "province"),
			"workers": self.retrieve_raw_field(line, "numberWorkers", "numberWorkers", ",", integer=True),
			"top_skills": self.retrieve_raw_field(
				line, "skillsList", "skillsList", "salaryDescription", _list=True),
			"job_level": self.retrieve_raw_field(line, "value", "jobLevel", "staffInCharge", _dict=True),
			"staff_in_charge": self.retrieve_raw_field(
				line, "value", "staffInCharge", "hasKillerQuestions", _dict=True),
			"contract_type": self.retrieve_raw_field(line, "value", "contractType", "journey", _dict=True)
		}

		return cleansed_fields

	@staticmethod
	def retrieve_raw_field(
			data, field, upper_limit, bottom_limit, integer=False, _list=False, _dict=False):
		if integer:
			test = json.dumps(data)
			field_description = test.split(f'\\\"{upper_limit}\\\": ')[1].split(bottom_limit)[0]
			joined_field_pieces = field_description

		elif _list:
			field_description = data.split(f'"{upper_limit}": ')[1].split(f'"{bottom_limit}"')[0]
			if field != upper_limit:
				field_description = field_description.split(f'"{field}": "')[1]
			joined_field_pieces = "".join(field_description.split('\\",')).replace("],", "]").replace("\n", "")

		elif _dict:
			field_description = data.split(f'"{upper_limit}": ')[1].split(f'"{bottom_limit}"')[0]
			joined_field_pieces = "[" + field_description.replace("\n", "") + "]"
			fields_list = eval(joined_field_pieces)
			joined_field_pieces = ",".join(sorted([field_.get(field).strip() for field_ in fields_list]))

		else:
			field_description = data.split(f'"{upper_limit}": "')[1].split(f'"{bottom_limit}"')[0]
			if field != upper_limit:
				field_description = field_description.split(f'"{field}": "')[1]
			joined_field_pieces = "".join(field_description.split('\\",'))

		cleansed_field_description = '"' + joined_field_pieces.replace('",', '').replace('"', '') + '"'
		return cleansed_field_description
