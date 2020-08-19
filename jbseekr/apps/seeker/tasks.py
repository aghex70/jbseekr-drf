from __future__ import absolute_import, unicode_literals
import logging
import time
import pytz
import re
from datetime import datetime

import celery
from celery import chord, group, chain, shared_task
from celery import exceptions as celery_exceptions

from .models import Position, Company
from .crawler import infojobs
from .scraper import linkedin, frg, jobfluent

tz = 'Europe/Madrid'
logger = logging.getLogger('msd')


class HandlerTask(celery.Task):

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		if self.request.retries != self.max_retries:
			countdown = self.default_retry_delay ** (self.request.retries + 1)
			logger.error(self.exc)
			logger.error(f"Error occurred in {self.name} task. Proceeding to retry in {countdown} seconds.")
			self.retry(countdown)
		else:
			logger.error(self.exc)
			logger.error(f"Error occurred in {self.name} task. Max retries reached.")


@shared_task(base=HandlerTask, bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
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
			generate_jobfluent_offers.s(**kwargs),
			generate_frg_offers.s(**kwargs)
		)
		chord(tasks_group)(get_process_summary.s(kwargs))

	except (celery_exceptions.ChordError, Exception) as exc:
		logger.error(f"[ERROR] on global task: {exc}")

	return "Launched job offers retrieval process"


@shared_task(base=HandlerTask, bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
def generate_infojobs_offers(self, positions_created=0, **kwargs):
	crawler = infojobs.InfojobsCrawler()
	crawler.execute()
	time.sleep(2)
	crawler.search_jobs(**kwargs)
	positions = crawler.retrieve_details()
	for position in positions:
		if not Position.objects.filter(link=position.get("url")).exists():
			new_position = Position.objects.create(
				role=position.get("role"),
				description=position.get("description"),
				link=position.get("url"),
				# location=position.get("location"),
				city=kwargs.get("location") if not position.get("city") else position.get("city"),
				address=position.get("address"),
				posted_date=pytz.timezone(tz).localize(position.get("posted_date")),
				modified_date=pytz.timezone(tz).localize(position.get("modified_date")),
				requirements=" - ".join(position.get("top_skills")),
				source=position.get("source"),
				salary=position.get("salary"),
				experience=position.get("experience"),
				responsibility=position.get("level"),
				staff_in_charge=position.get("staff_in_charge"),
				keywords=kwargs,
				contract_type=position.get("contract_type"),
				company=position.get("company"),
			)

			company, _ = Company.objects.get_or_create(
				name=position.get("company_name"),
				defaults={
					"description": position.get("company_description"),
					"web": position.get("company_url"),
					"workers": position.get("workers"),
				})
			new_position.company = company
			new_position.save()
			positions_created += 1
	return {
		'infojobs_positions_created': positions_created
	}


@shared_task(base=HandlerTask, bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
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
				role=details.get("title"),
				description=details.get("description"),
				link=cleansed_url,
				city=kwargs.get("location"),
				posted_date=details.get("datePosted"),
				source=scraper.source,
				experience=details.get("experienceRequirements"),
				keywords=kwargs,
				contract_type=details.get("employmentType"),

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


@shared_task(base=HandlerTask, bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
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
				role=position.get("role"),
				description=position.get("description"),
				link=position.get("url"),
				city=kwargs.get("location"),
				posted_date=posted_date,
				source=position.get("source"),
				keywords=kwargs
			)
			positions_created += 1
	return {
		'frg_positions_created': positions_created
	}


@shared_task(base=HandlerTask, bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
def generate_jobfluent_offers(self, positions_created=0, **kwargs):
	scraper = jobfluent.JobFluent()
	scraper.filter_positions(**kwargs)
	scraper.retrieve_positions()
	positions = scraper.retrieve_position_details()
	for position in positions:
		if not Position.objects.filter(link=position.get("link")).exists():
			new_position = Position.objects.create(
				role=position.get("role"),
				description=position.get("description"),
				link=position.get("link"),
				city=kwargs.get("location"),
				requirements=kwargs.get("requirements"),
				source=position.get("source"),
				salary=position.get("salary"),
				industry=position.get("industry"),
				keywords=kwargs
			)
			company, _ = Company.objects.get_or_create(
				name=position.get("company_name"),
				defaults={
					"description": position.get("company_description"),
					"web": position.get("company_web"),
					"workers": position.get("workers"),
					"type": scraper.company_type,
				})
			new_position.company = company
			new_position.save()
			positions_created += 1
	return {
		'jobfluent_positions_created': positions_created
	}


@shared_task(base=HandlerTask, bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
def get_process_summary(self, job_data, data_kwargs):
	new_jobs_created = 0
	for job in job_data:
		for k, v in job.items():
			new_jobs_created += v
	logger.info(f"New jobs created: {new_jobs_created}")
	return f"New jobs created: {new_jobs_created}"
