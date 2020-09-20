from django.apps import AppConfig


class SeekerConfig(AppConfig):
    name = 'jbseekr.apps.seeker'

    def ready(self):
        super(SeekerConfig, self).ready()

        # noinspection PyUnresolvedReferences
        from . import receivers
