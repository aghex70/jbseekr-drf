import json
from json import JSONDecodeError

from selenium.common.exceptions import InvalidSessionIdException

from datetime import datetime

from .base import BaseCrawler


class InfojobsCrawler(BaseCrawler):

	def __init__(self):
		self.origin = "https://developer.infojobs.net/test-console/console.xhtml?operationEntityField=-offer" + \
					  "&methodfield=GET&versionfield=1&hmethodfield=LIST"
		self.url = None
		self.role = None
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

	def retrieve_paginated_positions(self):
		# Obtain only two more pages
		for index in range(2, 4):
			api_inputbox = self.get_by_id(id="apiuri")
			inputbox_text = api_inputbox.get_attribute("value")
			api_inputbox.clear()
			current_page = str(int(inputbox_text.split("page=")[1])+1) \
				if 'page' in inputbox_text else "2"
			api_inputbox.send_keys(f"{inputbox_text.split('&page')[0]}&page={current_page}")
			self.submit_search()
			self.wait_implicit_time(2)
			response = json.loads(self.get_by_id(id="formattedBody").text.replace(")\"\"", ")\""), strict=False)
			self.positions = [*response.get("items"), *self.positions]

		for position in self.positions:
			position['company_description'] = position.pop('description', None)

	def wrap_positions(self):
		for position in self.positions:
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
				"minimum_salary": position.get("salaryMin", {}).get("value"),
				"maximum_salary": position.get("salaryMax", {}).get("value"),
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

	# TODO chhange default params calls
	def cleanse_fields(self, line):
		cleansed_fields = {
			"company_url": self.retrieve_raw_field(line, "web", "web", "numberWorkers"),
			"description": self.retrieve_raw_field(line, "description", "minRequirements", "desiredRequirements"),
			"company_description": self.retrieve_raw_field(line, "description", "description", "province"),
			"workers": self.retrieve_raw_field(line, "numberWorkers", "numberWorkers", ",", True),
			"top_skills": self.retrieve_raw_field(line, "skillsList", "skillsList", "salaryDescription", False, True, "skill"),
			"job_level": self.retrieve_raw_field(line, "value", "jobLevel", "staffInCharge", False, False, None, True),
			"staff_in_charge": self.retrieve_raw_field(line, "value", "staffInCharge", "hasKillerQuestions", False, False, None, True),
			"contract_type": self.retrieve_raw_field(line, "value", "contractType", "journey", False, False, None, True),
		}

		return cleansed_fields

	@staticmethod
	def retrieve_raw_field(
			data, field, upper_limit, bottom_limit, integer=False, list=False, list_key=None, dict=False):
		if integer:
			test = json.dumps(data)
			field_description = test.split(f'\\\"{upper_limit}\\\": ')[1].split(bottom_limit)[0]
			joined_field_pieces = field_description

		elif list:
			field_description = data.split(f'"{upper_limit}": ')[1].split(f'"{bottom_limit}"')[0]
			if field != upper_limit:
				field_description = field_description.split(f'"{field}": "')[1]
			joined_field_pieces = "".join(field_description.split('\\",')).replace("],", "]").replace("\n", "")
			fields_list = sorted(field.get("skill").capitalize() for field in eval(joined_field_pieces))

		elif dict:
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

import time
import asyncio
import pyppeteer
from pyppeteer import launch

pyppeteer.DEBUG = True

class NewInfojobsCrawler():

	def __init__(self):
		self.origin = "https://developer.infojobs.net/test-console/console.xhtml?operationEntityField=-offer" + \
					  "&methodfield=GET&versionfield=1&hmethodfield=LIST"
		self.browser = None
		self.page = None
		self.role = None
		self.location = None
		self.positions = None
		self.scroll_start_height = 0
		self.client_height = 0
		self.wrapped_positions = []
		self.detailed_positions = []
		self.source = "Infojobs"

	def __await__(self):
		return self.execute().__await__()

	async def execute(self):
		await self.get_browser()
		await self.open_browser()
		await self.get_url(self.origin)
		await self.page.screenshot(path="fallo.png")
		self.wait_until_page_has_loaded()
		kwargs = {}
		await self.search_jobs(**kwargs)
		positions = await self.retrieve_details()

	async def get_browser(self):
		self.browser = await launch()
		return self.browser

	async def open_browser(self):
		self.page = await self.browser.newPage()

	async def close_browser(self):
		await self.browser.close()

	async def get_url(self, url):
		await self.page.goto(url)

	async def search_jobs(self, **kwargs):
		self.role = kwargs.get("role", "Python").capitalize()
		self.location = kwargs.get("location", "Madrid").capitalize()
		await self.fill_role(self.role)
		await self.fill_location(self.location)
		await self.set_update_desc_order()
		await self.submit_search()
		await self.retrieve_positions()
		await self.close_browser()

	async def fill_role(self, role):
		await self.page.type("#apiuri", f"?q={role}")

	async def fill_location(self, location):
		await self.page.type("#apiuri", f"&province={location}")

	async def set_update_desc_order(self):
		await self.page.type("#apiuri", f"&order=updated-desc")

	async def submit_search(self):
		await asyncio.wait([
			self.page.click("#send-button"),
			self.page.waitForNavigation(),
		])

	async def retrieve_positions(self):
		self.wait_implicit_time(3)
		await self.page.screenshot(path="fallo1.png")
		response_container = await self.get_by_id("formattedBody")
		print(f"response_container ----> {response_container}")
		print(f"response_container.__dict__ ----> {response_container.__dict__}")
		response = await self.page.evaluate("response_container =>  response_container.textContent", response_container)
		response = response.replace(")\"\"", ")\"")
		response = response.replace("\'", "\"")
		print(f"response ----> {response}")
		response = json.loads(response, strict=False)
		self.positions = response.get("items")
		await self.retrieve_paginated_positions()

	async def retrieve_element_text(self, id):
		response_container = await self.get_by_id(id)
		text = await self.page.evaluate("response_container =>  response_container.textContent", response_container)
		return text

	async def clear_inputbox(self, id):
		await self.page.click(f"#{id}", {"clickCount": 3})
		await self.page.keyboard.press('Backspace')

	async def fill_inputbox(self, id, text):
		await self.page.type(f"#{id}", text)

	# Method to clear inputbox
	async def retrieve_paginated_positions(self):
		print("213123213123")
		# Obtain only two more pages
		for index in range(2, 4):
			api_inputbox = await self.get_by_id(id="apiuri")
			# Method to clear inputbox
			inputbox_text = await self.retrieve_element_text("apiuri")
			current_page = str(int(inputbox_text.split("page=")[1]) + 1) \
				if 'page' in inputbox_text else "2"
			await self.clear_inputbox("apiuri")
			await self.fill_inputbox("apiuri", f"{inputbox_text.split('&page')[0]}&page={current_page}")
			await self.submit_search()

			self.wait_until_page_has_loaded()
			text = await self.retrieve_element_text("formattedBody")
			response = json.loads(text.replace(")\"\"", ")\""), strict=False)
			self.positions = [*response.get("items"), *self.positions]

		for position in self.positions:
			position['company_description'] = position.pop('description', None)

	def wrap_positions(self):
		for position in self.positions:
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
				"minimum_salary": position.get("salaryMin", {}).get("value"),
				"maximum_salary": position.get("salaryMax", {}).get("value"),
				"experience": position.get("experienceMin").get("value"),
				"contract_type": position.get("contract_type"),
			}
			self.wrapped_positions.append(wrapped_position)

	async def reset_session(self):
		try:
			await self.close_browser()
		except Exception:
			pass
		await self.open_browser()
		await self.get_url(self.origin)
		self.wait_until_page_has_loaded()

	async def retrieve_details(self):
		print(f"self.positions ----> {self.positions}")
		await self.open_browser()
		await self.get_url(self.origin)
		await self.get_url(self.origin)
		self.wait_until_page_has_loaded()
		await self.retrieve_position_details()
		self.wrap_positions()
		await self.close_browser()
		return self.wrapped_positions

	async def retrieve_position_details(self):
		i = 0
		while i < len(self.positions):
			print(i)
			try:
				position_id = self.positions[i].get("id")
				await self.clear_inputbox("apiuri")
				await self.fill_inputbox("apiuri", f"https://api.infojobs.net/api/7/offer/{position_id}")
				await self.submit_search()

				self.wait_until_page_has_loaded()
				text = await self.retrieve_element_text("formattedBody")
				response = json.loads(text.replace(")\"\"", ")\""), strict=False)
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
				text = await self.retrieve_element_text("formattedBody")
				cleansed_line = self.cleanse_fields(text)
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
				await self.reset_session()
				continue
			i += 1
		self.positions = self.detailed_positions
		return self.positions

	def cleanse_fields(self, line):
		cleansed_fields = {
			"company_url": self.retrieve_raw_field(line, "web", "web", "numberWorkers"),
			"description": self.retrieve_raw_field(line, "description", "minRequirements", "desiredRequirements"),
			"company_description": self.retrieve_raw_field(line, "description", "description", "province"),
			"workers": self.retrieve_raw_field(line, "numberWorkers", "numberWorkers", ",", True),
			"top_skills": self.retrieve_raw_field(line, "skillsList", "skillsList", "salaryDescription", False, True, "skill"),
			"job_level": self.retrieve_raw_field(line, "value", "jobLevel", "staffInCharge", False, False, None, True),
			"staff_in_charge": self.retrieve_raw_field(line, "value", "staffInCharge", "hasKillerQuestions", False, False, None, True),
			"contract_type": self.retrieve_raw_field(line, "value", "contractType", "journey", False, False, None, True),
		}

		return cleansed_fields

	@staticmethod
	def retrieve_raw_field(
			data, field, upper_limit, bottom_limit, integer=False, list=False, list_key=None, dict=False):
		if integer:
			test = json.dumps(data)
			field_description = test.split(f'\\\"{upper_limit}\\\": ')[1].split(bottom_limit)[0]
			joined_field_pieces = field_description

		elif list:
			field_description = data.split(f'"{upper_limit}": ')[1].split(f'"{bottom_limit}"')[0]
			if field != upper_limit:
				field_description = field_description.split(f'"{field}": "')[1]
			joined_field_pieces = "".join(field_description.split('\\",')).replace("],", "]").replace("\n", "")
			fields_list = sorted(field.get("skill").capitalize() for field in eval(joined_field_pieces))

		elif dict:
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

	async def get_by_id(self, id):
		return await self.page.querySelector(f"#{id}")

	async def get_by_class(self, class_name):
		return await self.page.querySelector(f".{class_name}")

	async def get_by_tag(self, tag):
		return await self.page.querySelector(tag)

	async def get_by_css(self, css):
		return await self.page.querySelector(css)

	async def get_by_xpath(self, xpath):
		return await self.page.xpath(xpath)

	async def get_by_text(self, text):
		return await self.page.xpath(f"//*[contains(text(), '{text}')]")

	async def get_elements_by_id(self, id):
		return await self.page.querySelectorAll(f"#{id}")

	async def get_elements_by_class(self, class_name):
		return await self.page.querySelectorAll(f".{class_name}")

	async def get_elements_by_tag(self, tag):
		return await self.page.querySelectorAll(tag)

	async def get_elements_by_css(self, css):
		return await self.page.querySelectorAll(css)

	async def get_elements_by_xpath(self, xpath):
		return await self.page.xpath(xpath)

	async def get_elements_by_text(self, text):
		return await self.page.xpath(f"//*[contains(text(), '{text}')]")

	async def get_client_height(self):
		return await self.page.evaluate("return document.body.clientHeight")

	async def open_in_new_tab(self, url):
		return await self.page.evaluate(f"window.open('{url}','_blank');")

	async def select_dropdown_option_by_id(self, id, text):
		option = await self.get_by_xpath(xpath=f'//*[@id = "{id}"]/option[text() = "{text}"]')
		value = await (await option.getProperty('value')).jsonValue()
		await self.page.select('#selectId', value)

	async def scroll_down(self):
		self.client_height = await self.get_client_height()
		script = f"window.scrollTo({self.scroll_start_height},{self.scroll_start_height+self.client_height});"
		await self.page.evaluate(script)

	async def scroll_bottom(self):
		script = "window.scrollTo(0,document.body.scrollHeight);"
		await self.page.evaluate(script)

	async def get_class_name_attribute(self, class_name, attribute):
		element = await self.page.querySelector(f".{class_name}")
		value = await element.getProperty(attribute)
		return value

	async def get_inner_elements_by_tag(self, container_tag, tag):
		container = await self.get_by_tag(container_tag)
		return await container.querySelectorAll(tag)

	async def get_inner_elements_by_id(self, container_id, id):
		container = await self.get_by_id(container_id)
		return await container.querySelectorAll(f"#{id}")

	async def get_inner_elements_by_class(self, container_class, class_name):
		container = await self.get_by_class(container_class)
		return await container.querySelectorAll(f".{class_name}")

	async def get_inner_elements_by_text(self, container_id, text):
		container = await self.get_by_id(container_id)
		return await container.xpath((f"//*[contains(text(), '{text}')]"))

	def wait_until_page_has_loaded(self):
		time.sleep(2)
		#pass
		#await self.page.waitForNavigation()
			#{"waitUntil": "networkidle"})

	async def wait_until_element_is_loaded_by_xpath(self, xpath):
		await self.page.waitForXpath(xpath)

	async def wait_until_element_is_loaded_by_class(self, class_name):
		await self.page.waitForSelector(f".{class_name}")

	async def wait_until_element_is_loaded_by_id(self, id):
		await self.page.waitForSelector(f"#{id}")

	@staticmethod
	def wait_implicit_time(seconds):
		time.sleep(seconds)


async def main():
    crawler = await NewInfojobsCrawler()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
