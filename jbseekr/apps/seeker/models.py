from django.db import models
from django.utils import timezone


class Company(models.Model):
	name = models.CharField(blank=True, null=True)
	description = models.TextField(blank=True, null=True)
	web = models.CharField(blank=True, null=True)
	workers = models.IntegerField(blank=True, null=True)


class Position(models.Model):
	SOURCE_CHOICES = (
		('Linkedin', 'Linkedin'),
		('Infojobs', 'Infojobs'),
	)

	role = models.CharField(blank=True, null=True)
	city = models.CharField(blank=True, null=True)
	location = models.CharField(blank=True, null=True)
	description = models.TextField(blank=True, null=True)
	address = models.TextField(blank=True, null=True)
	posted_date = models.DateTimeField(blank=True, null=True)
	modified_date = models.DateTimeField(blank=True, null=True)
	created_date = models.DateTimeField(blank=True, null=True)
	top_skills = models.CharField(blank=True, null=True)
	source = models.CharField(choices=SOURCE_CHOICES)
	company = models.ForeignKey(Company, on_delete=models.DO_NOTHING)
	url = models.CharField(blank=True, null=True)
	keywords = models.JSONField(blank=True, null=True)
	highlighted = models.BooleanField(default=False)
	consulting_firm = models.NullBooleanField()
	closed = models.BooleanField()
	maximum_salary = models.CharField(blank=True, null=True)
	minimum_salary = models.CharField(blank=True, null=True)
	experience = models.CharField(blank=True, null=True)
	level = models.CharField(blank=True, null=True)
	staff_in_charge = models.CharField(blank=True, null=True)
	contract_type = models.CharField(blank=True, null=True)


	def __str__(self):
		return f"{self.keyword.role} - {self.title}"

	def save(self, *args, **kwargs):
		# Custom made save in order to have created_date editable in admin
		if not self.id:
			self.created_date = timezone.now()
		self.modified_date = timezone.now()
		return super(Position, self).save(*args, **kwargs)


class Opinion(models.Model):
	rating = models.FloatField()
	company = models.ForeignKey(Company, on_delete=models.DO_NOTHING)
	url = models.CharField(blank=True, null=True)