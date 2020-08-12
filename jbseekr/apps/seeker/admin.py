from django.contrib import admin

from .models import (Position, Company, Opinion)


# Register your models here.
class PositionAdmin(admin.ModelAdmin):
	list_display = (
		'role', 'minimum_salary', 'maximum_salary', 'posted_date', 'created_date')


admin.site.register(Position, PositionAdmin)