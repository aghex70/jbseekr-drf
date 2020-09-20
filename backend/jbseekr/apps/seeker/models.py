from django.db import models
from django.utils import timezone

from django.db.models import JSONField

from .managers import HighlightedPositionManager, IgnoredPositionManager


class Company(models.Model):
	COMPANY_TYPE_CHOICES = (
		('Startup', 'Startup'),
		('Well_established_company', 'Well_established_company'),
		('Consulting_firm', 'Consulting_firm'),
	)

	name = models.CharField(blank=True, null=True, max_length=255)
	web = models.CharField(blank=True, null=True, max_length=255)
	description = models.TextField(blank=True, null=True)
	workers = models.CharField(null=True, max_length=30)
	market = models.CharField(null=True, max_length=20)
	type = models.CharField(choices=COMPANY_TYPE_CHOICES, null=True, max_length=25)

	def __str__(self):
		return self.name

class Position(models.Model):
	SOURCE_CHOICES = (
		('Linkedin', 'Linkedin'),
		('Infojobs', 'Infojobs'),
		('FRG', 'FRG'),
		('JobFluent', 'JobFluent'),
	)

	CONTRACT_CHOICES = (
		('Linkedin', 'Linkedin'),
		('Infojobs', 'Infojobs'),
		('FRG', 'FRG'),
		('JobFluent', 'JobFluent'),
		('Glassdoor', 'Glassdoor'),
	)

	role = models.CharField(blank=True, null=True, max_length=255)
	description = models.TextField(blank=True, null=True)
	link = models.TextField(blank=True, null=True)
	city = models.CharField(blank=True, null=True, max_length=50)
	address = models.TextField(blank=True, null=True)
	posted_date = models.DateTimeField(blank=True, null=True)
	modified_date = models.DateTimeField(blank=True, null=True)
	created_date = models.DateTimeField(blank=True, null=True)
	expiration_date = models.DateTimeField(blank=True, null=True)
	requirements = models.TextField(blank=True, null=True)
	source = models.CharField(choices=SOURCE_CHOICES, max_length=20)
	emphasized = models.BooleanField(default=False)
	user_rating = models.FloatField(blank=True, null=True)
	hidden = models.BooleanField(default=False)
	expired = models.BooleanField(blank=True, null=True)
	salary = models.CharField(blank=True, null=True, max_length=50)
	experience = models.CharField(blank=True, null=True, max_length=30)
	responsibility = models.CharField(blank=True, null=True, max_length=30)
	staff_in_charge = models.CharField(blank=True, null=True, max_length=5)
	keywords = JSONField(blank=True, null=True)
	contract_type = models.CharField(choices=CONTRACT_CHOICES, max_length=25)
	industry = models.CharField(blank=True, null=True, max_length=30)
	company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, blank=True, null=True)

	# Managers
	objects = models.Manager()
	highlighted = HighlightedPositionManager()
	ignored = IgnoredPositionManager()

	def __str__(self):
		return f"{self.role} - {self.city}"

	def save(self, *args, **kwargs):
		now = timezone.now()
		# Custom made save in order to have created_date editable in admin
		if not self.id:
			self.created_date = now

		if not self.posted_date:
			self.posted_date = now

		self.modified_date = now
		return super(Position, self).save(*args, **kwargs)


class Opinion(models.Model):
	rating = models.FloatField()
	company = models.ForeignKey(Company, on_delete=models.DO_NOTHING)
	url = models.TextField(blank=True, null=True)


