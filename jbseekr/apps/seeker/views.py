# from django.shortcuts import render

# Create your views here.
from models import Position, Company


crawler = InfojobsCrawler(source="Infojobs")
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
	crawled_positions = crawled_positions[0
	]
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

		#Opinion.objects.get_or_create()