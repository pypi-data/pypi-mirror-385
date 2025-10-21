from django.apps import AppConfig


class WhiteboxPluginMapConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "whitebox_plugin_map"
    verbose_name = "Whitebox Plugin Map"

    def ready(self):
        pass
