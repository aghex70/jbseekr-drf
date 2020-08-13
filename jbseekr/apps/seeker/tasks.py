from __future__ import absolute_import, unicode_literals
import logging
import time
from datetime import datetime

from celery import chord, group, chain, shared_task
from celery import exceptions as celery_exceptions

from .models import Position, Company
from .crawler import infojobs
from .scraper import linkedin

logger = logging.getLogger('msd')


@shared_task(bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
#@app.task(bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
def generate_offers(self, **kwargs):
	if not kwargs:
		kwargs = {
		"role": "Python",
		"location": "Madrid",
	}
	print(f"seeker TASK")

	try:
		tasks_group = group(generate_infojobs_offers.s(**kwargs), generate_linkedin_offers.s(**kwargs))
		chord(tasks_group)(ekekekek.s(kwargs))

	except (celery_exceptions.ChordError, Exception) as exc:
		logger.error(f"[ERROR] on global task: {exc}")

	return {
		'success': True
	}

@shared_task(bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
#@app.task(bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
def generate_infojobs_offers(self, **kwargs):
	print("SEEKER 1")
	crawler = infojobs.InfojobsCrawler()
	crawler.execute()
	time.sleep(2)
	crawler.search_jobs(**kwargs)
	positions = crawler.retrieve_details()

	try:
		for position in positions:
			if not Position.objects.filter(
					link=position.get("url"),
					minimum_salary=position.get("minimum_salary"),
					maximum_salary=position.get("maximum_salary")).exists():

				new_position = Position.objects.create(
					link=position.get("url"),
					role=position.get("role"),
					posted_date=position.get("posted_date"),
					maximum_salary=position.get("maximum_salary"),
					minimum_salary=position.get("minimum_salary"),
					city=position.get("city"),
					location=position.get("location"),
					description=position.get("description"),
					address=position.get("address"),
					modified_date=position.get("modified_date"),
					top_skills=position.get("top_skills"),
					source=position.get("source"),
					company=position.get("company"),
					keywords=kwargs,
					closed=position.get("closed"),
					experience=position.get("experience"),
					level=position.get("level"),
					staff_in_charge=position.get("staff_in_charge"),
					contract_type=position.get("contract_type")
				)

				company, _ = Company.objects.get_or_create(
					name=position.get("company_name"),
					description=position.get("company_description"),
					web=position.get("company_url"),
					workers=position.get("workers"),
				)
				new_position.company = company
				new_position.save()
	except:
		for k,v in position.items():
			print(f"k ----> {k}")
			print(f"v ----> {len(str(v))}")

	print(kwargs)
	return {
		'hola1': kwargs
	}

@shared_task(bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
#@app.task(bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
def generate_linkedin_offers(self, **kwargs):
	print("SEEKER 2")
	scraper = linkedin.LinkedinScraper()
	scraper.filter_positions(**kwargs)
	positions_urls = scraper.retrieve_positions_urls()

	for url in positions_urls:
		position = scraper.retrieve_position(position_url=url)
		details = scraper.retrieve_position_details()

		if not Position.objects.filter(link=url).exists():
			new_position = Position.objects.create(
				link=url,
				role=details.get("title"),
				posted_date=details.get("datePosted"),
				description=details.get("description"),
				source=scraper.source,
				company=details.get("hiringOrganization").get("name"),
				keywords=kwargs,
				closed=True
				if datetime.strptime(details.get("validThrough"), "%Y-%m-%dT%H:%M:%S.000Z") <= datetime.now()
				else False,
				experience=details.get("experienceRequirements"),
				contract_type=details.get("employmentType")
			)

			company, _ = Company.objects.get_or_create(
				name=position.get("company_name"),
				description=position.get("company_description"),
				web=position.get("company_url"),
				workers=position.get("workers"),
			)
			new_position.company = company
			new_position.save()

	return {
		'hola2': kwargs
	}

@shared_task(bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
#@app.task(bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
def ekekekek(self, parametrownz1, parametrownz2, **kwargs):
	print(f"parametrownz1 -----> {parametrownz1}")
	print(f"parametrownz2 -----> {parametrownz2}")
	print(f" ekekekek kwargs ---> {kwargs}")