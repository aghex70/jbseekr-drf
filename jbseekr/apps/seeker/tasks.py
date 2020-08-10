from __future__ import absolute_import, unicode_literals

import logging

from celery import task, shared_task, chord, group, chain
from celery import exceptions as celery_exceptions
from ...celery import app

from datetime import datetime, timedelta

from django.db.models.signals import post_save
from .models import Position, Company
from .crawler import infojobs
from .scraper import linkedin
import time


logger = logging.getLogger('msd')


@app.task(bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
def generate_offers(self, **kwargs):
	try:
		tasks_group = group(
			generate_infojobs_offers.s(
				ecommerce_operation='get_issued_invoices',
				mapper_operation='ecommerce_issued_invoices',
				**kwargs),
			generate_linkedin_offers.s(
				crm_operation='get_issued_invoices',
				mapper_operation='crm_issued_invoices',
				**kwargs)
		)
		chord(tasks_group)(generate_file.s(
			generator_import='sap',
			generator_class='SapIssuedGenerator', **kwargs)
		)
	except (celery_exceptions.ChordError, Exception) as exc:
		logger.error(f"[ERROR] on global task: {exc}")

	return {
		'success': True
	}

@app.task(bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
def generate_infojobs_offers(self, **kwargs):
	crawler = infojobs.InfojobsCrawler(source="Infojobs")
	crawler.execute()
	time.sleep(2)
	kwargs = {
		"role": "Python",
		"location": "Madrid",
	}
	crawler.search_jobs(role="python", location="madrid")
	final_positions = crawler.wrap_positions()
	wrapped_details = crawler.retrieve_details()
	crawled_positions = crawler.retrieve_position_details()
	crawled_positions = crawled_positions[0]
	if not Position.objects.filter(
			url=crawled_positions.get("url"),
			description=crawled_positions.get("description"),
			minimum_salary=crawled_positions.get("minimum_salary"),
			maximum_salary=crawled_positions.get("maximum_salary")).exists():

		new_position = Position.objects.create(
			url=crawled_positions.get("url"),
			role=crawled_positions.get("role"),
			posted_date=crawled_positions.get("posted_date"),
			maximum_salary=crawled_positions.get("maximum_salary"),
			minimum_salary=crawled_positions.get("minimum_salary"),
			city=crawled_positions.get("city"),
			location=crawled_positions.get("location"),
			description=crawled_positions.get("description"),
			address=crawled_positions.get("address"),
			modified_date=crawled_positions.get("modified_date"),
			top_skills=crawled_positions.get("top_skills"),
			source=crawled_positions.get("source"),
			company=crawled_positions.get("company"),
			keywords=kwargs,
			closed=crawled_positions.get("closed"),
			experience=crawled_positions.get("experience"),
			level=crawled_positions.get("level"),
			staff_in_charge=crawled_positions.get("staff_in_charge"),
			contract_type=crawled_positions.get("contract_type")
		)

		company, _ = Company.objects.get_or_create(
			name=crawled_positions.get("company_name"),
			description=crawled_positions.get("company_description"),
			url=crawled_positions.get("company_url"),
			workers=crawled_positions.get("workers"),
		)
		new_position.company = company
		new_position.save()

@app.task(bind=True, max_retries=3, default_retry_delay=20, queue='seeker')
def generate_linkedin_offers(self, **kwargs):
	pass