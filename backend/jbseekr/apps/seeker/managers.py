from django.db import models


class IgnoredPositionManager(models.Manager):
	def get_queryset(self):
		return super(IgnoredPositionManager, self).get_queryset().filter(expired=True, hidden=True)


class HighlightedPositionManager(models.Manager):
	def get_queryset(self):
		return super(HighlightedPositionManager, self).get_queryset().filter(emphasized=True)
