from django.apps import AppConfig


class DiffresultsConfig(AppConfig):
    name = 'diffresults'

    def ready(self):
        import diffresults.signals  # noqa: F401
