from django.contrib import admin

from .models import (Position, Company, Opinion)


# Register your models here.
class PositionAdmin(admin.ModelAdmin):
	list_display = (
		'role', 'salary', 'posted_date', 'created_date', 'source', 'hidden')


admin.site.register(Position, PositionAdmin)