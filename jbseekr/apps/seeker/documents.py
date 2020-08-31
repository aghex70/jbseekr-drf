from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import (Company, Position, Opinion)

@registry.register_document
class CompanyDocument(Document):
	class Index:
		# Name of the Elasticsearch index
		name = 'companies'
		# See Elasticsearch Indices API reference for available settings
		settings = {'number_of_shards': 1,
					'number_of_replicas': 0}

	class Django:
		model = Company  # The model associated with this Document

		# The fields of the model you want to be indexed in Elasticsearch
		fields = [
			'name',
			'web',
			'description',
			'workers',
			'market',
			'type',
		]


@registry.register_document
class PositionDocument(Document):
	class Index:
		# Name of the Elasticsearch index
		name = 'positions'
		# See Elasticsearch Indices API reference for available settings
		settings = {'number_of_shards': 1,
					'number_of_replicas': 0}

	class Django:
		model = Position  # The model associated with this Document

		# The fields of the model you want to be indexed in Elasticsearch
		fields = [
			'role',
			'description',
			'link',
			'city',
			'address',
			'posted_date',
			'modified_date',
			'created_date',
			'expiration_date',
			'requirements',
			'source',
			'emphasized',
			'user_rating',
			'hidden',
			'expired',
			'salary',
			'experience',
			'responsibility',
			'staff_in_charge',
			'contract_type',
			'industry',
		]

	# Ignore auto updating of Elasticsearch when a model is saved
	# or deleted:
	# ignore_signals = True

	# Don't perform an index refresh after every update (overrides global setting):
	# auto_refresh = False

	# Paginate the django queryset used to populate the index with the specified size
	# (by default it uses the database driver's default setting)
	# queryset_pagination = 5000
