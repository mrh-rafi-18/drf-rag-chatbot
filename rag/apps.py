from django.apps import AppConfig

class RagConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rag"

    def ready(self):
        from .tasks import start_scheduler
        start_scheduler()
