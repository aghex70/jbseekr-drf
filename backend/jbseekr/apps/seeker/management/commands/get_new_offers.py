from django.core.management.base import BaseCommand

from jbseekr.apps.seeker import tasks


class Command(BaseCommand):
    help = "Scrape in order to obtain new offers"

    def handle(self, *args,  **options):
        tasks.generate_offers.apply_async(kwargs={}, countdown=0)
