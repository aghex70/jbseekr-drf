from __future__ import absolute_import, unicode_literals
import logging
import time
import re
from datetime import datetime

from celery import chord, group, chain, shared_task
from celery import exceptions as celery_exceptions

from .models import Position, Company
from .crawler import infojobs
from .scraper import linkedin, frg

import pytz
tz = 'Europe/Madrid'


logger = logging.getLogger('msd')


@shared_task(bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
def generate_offers(self, **kwargs):
	if not kwargs:
		kwargs = {
			"role": "Python",
			"location": "Madrid",
		}

	try:
		tasks_group = group(
			generate_infojobs_offers.s(**kwargs),
			generate_linkedin_offers.s(**kwargs),
			generate_frg_offers.s(**kwargs)
		)
		chord(tasks_group)(get_process_summary.s(kwargs))

	except (celery_exceptions.ChordError, Exception) as exc:
		logger.error(f"[ERROR] on global task: {exc}")

	return "Launched job offers retrieval process"


@shared_task(bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
def generate_infojobs_offers(self, positions_created=0, **kwargs):
	crawler = infojobs.InfojobsCrawler()
	crawler.execute()
	time.sleep(2)
	crawler.search_jobs(**kwargs)
	positions = crawler.retrieve_details()
	for position in positions:
		if not Position.objects.filter(
				link=position.get("url"),
				minimum_salary=position.get("minimum_salary"),
				maximum_salary=position.get("maximum_salary")).exists():

			new_position = Position.objects.create(
				link=position.get("url"),
				role=position.get("role"),
				posted_date=pytz.timezone(tz).localize(position.get("posted_date")),
				maximum_salary=position.get("maximum_salary"),
				minimum_salary=position.get("minimum_salary"),
				city=kwargs.get("location") if not position.get("city") else position.get("city"),
				location=position.get("location"),
				description=position.get("description"),
				address=position.get("address"),
				modified_date=pytz.timezone(tz).localize(position.get("modified_date")),
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
			positions_created += 1
	return {
		'infojobs_positions_created': positions_created
	}


@shared_task(bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
def generate_linkedin_offers(self, positions_created=0, **kwargs):
	scraper = linkedin.LinkedinScraper()
	scraper.filter_positions(**kwargs)
	positions_urls = scraper.retrieve_positions_urls()
	for url in positions_urls:
		cleansed_url = url.split("?refId=")[0]
		scraper.retrieve_position(position_url=url)
		details = scraper.retrieve_position_details()

		if not Position.objects.filter(link=cleansed_url).exists():
			new_position = Position.objects.create(
				link=cleansed_url,
				role=details.get("title"),
				posted_date=details.get("datePosted"),
				description=details.get("description"),
				source=scraper.source,
				keywords=kwargs,
				closed=True
				if datetime.strptime(details.get("validThrough"), "%Y-%m-%dT%H:%M:%S.000Z") <= datetime.now()
				else False,
				experience=details.get("experienceRequirements"),
				contract_type=details.get("employmentType"),
				city=kwargs.get("location"),
			)
			company, _ = Company.objects.get_or_create(
				name=details.get("hiringOrganization").get("name"),
			)
			new_position.company = company
			new_position.save()
			positions_created += 1
	return {
		'linkedin_positions_created': positions_created
	}


@shared_task(bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
def generate_frg_offers(self, positions_created=0, **kwargs):
	scraper = frg.FRGScraper()
	scraper.filter_positions(**kwargs)
	scraper.retrieve_positions()
	scraper.filter_positions_details()
	positions = scraper.fill_position_details()
	for position in positions:
		if not Position.objects.filter(link=position.get("url")).exists():
			scraped_date = position.get("posted_date")
			posted_date = datetime.strptime(re.sub("[th]|[st]|[nd]|[rd]", "", scraped_date), "%d %b, %Y")
			posted_date = pytz.timezone(tz).localize(posted_date)
			Position.objects.create(
				link=position.get("url"),
				role=position.get("role"),
				source=position.get("source"),
				posted_date=posted_date,
				description=position.get("description"),
				city=kwargs.get("location"),
				keywords={
					"role": kwargs.get("role"),
					"location": kwargs.get("location"),
				}
			)
			positions_created += 1
	return {
		'frg_positions_created': positions_created
	}


@shared_task(bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
def get_process_summary(self, job_data, data_kwargs):
	new_jobs_created = 0
	for job in job_data:
		for k, v in job.items():
			new_jobs_created += v
	logger.info(f"New jobs created: {new_jobs_created}")
	return f"New jobs created: {new_jobs_created}"