from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "blog"
    verbose_name = "Blog"

    def ready(self):
        # Import signals here to ensure they are loaded
        try:
            import blog.signals
        except ImportError:
            pass
