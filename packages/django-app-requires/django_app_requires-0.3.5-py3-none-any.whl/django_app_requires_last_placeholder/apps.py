from zenutils.importutils import import_from_string

from django.apps import AppConfig


class DjangoAppRequiresLastPlaceholderConfig(AppConfig):
    name = "django_app_requires_last_placeholder"

    def ready(self):
        self.load_post_app_ready_callbacks()

    def load_post_app_ready_callbacks(self):
        from django.conf import settings

        for app in settings.INSTALLED_APPS:
            callback_paths_path = app + ".post_app_ready_callbacks"
            callback_paths = import_from_string(callback_paths_path)
            if callback_paths:
                for callback_path in callback_paths:
                    if callback_path:
                        callback = import_from_string(callback_path)
                        if callback:
                            callback()
