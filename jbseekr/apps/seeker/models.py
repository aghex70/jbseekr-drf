from django.db import models
from django.utils import timezone

from django.db.models import JSONField


class Company(models.Model):
	name = models.CharField(blank=True, null=True, max_length=255)
	description = models.TextField(blank=True, null=True)
	web = models.CharField(blank=True, null=True, max_length=255)
	workers = models.IntegerField(blank=True, null=True)


class Position(models.Model):
	SOURCE_CHOICES = (
		('Linkedin', 'Linkedin'),
		('Infojobs', 'Infojobs'),
	)

	role = models.CharField(blank=True, null=True, max_length=255)
	city = models.CharField(blank=True, null=True, max_length=255)
	location = models.CharField(blank=True, null=True, max_length=255)
	description = models.TextField(blank=True, null=True)
	address = models.TextField(blank=True, null=True)
	posted_date = models.DateTimeField(blank=True, null=True)
	modified_date = models.DateTimeField(blank=True, null=True)
	created_date = models.DateTimeField(blank=True, null=True)
	top_skills = models.TextField(blank=True, null=True)
	source = models.CharField(choices=SOURCE_CHOICES, max_length=255)
	company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, blank=True, null=True)
	url = models.CharField(blank=True, null=True, max_length=255)
	link = models.CharField(blank=True, null=True, max_length=255)
	keywords = JSONField(blank=True, null=True)
	highlighted = models.BooleanField(default=False)
	hidden = models.BooleanField(default=False)
	user_rating = models.FloatField(blank=True, null=True)
	consulting_firm = models.BooleanField(blank=True, null=True)
	closed = models.BooleanField(blank=True, null=True)
	maximum_salary = models.CharField(blank=True, null=True, max_length=255)
	minimum_salary = models.CharField(blank=True, null=True, max_length=255)
	experience = models.CharField(blank=True, null=True, max_length=255)
	level = models.CharField(blank=True, null=True, max_length=255)
	staff_in_charge = models.CharField(blank=True, null=True, max_length=255)
	contract_type = models.CharField(blank=True, null=True, max_length=255)

	def __str__(self):
		return f"{self.role} - {self.city}"

	def save(self, *args, **kwargs):
		# Custom made save in order to have created_date editable in admin
		if not self.id:
			self.created_date = timezone.now()
		self.modified_date = timezone.now()
		return super(Position, self).save(*args, **kwargs)


class Opinion(models.Model):
	rating = models.FloatField()
	company = models.ForeignKey(Company, on_delete=models.DO_NOTHING)
	url = models.CharField(blank=True, null=True, max_length=255)
