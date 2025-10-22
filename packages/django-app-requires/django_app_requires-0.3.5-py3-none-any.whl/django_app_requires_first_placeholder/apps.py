from zenutils.importutils import import_from_string
from django.apps import AppConfig


class DjangoAppRequiresFirstPlaceholderConfig(AppConfig):
    name = "django_app_requires_first_placeholder"

    def ready(self):
        self.install_admin_autodiscover_hooks()
        self.load_pre_app_ready_callbacks()

    def install_admin_autodiscover_hooks(self):
        def load_pre_admin_autodiscover_callbacks():
            from django.conf import settings

            for app in settings.INSTALLED_APPS:
                callback_paths_path = app + ".pre_admin_autodiscover_callbacks"
                callback_paths = import_from_string(callback_paths_path)
                if callback_paths:
                    for callback_path in callback_paths:
                        if callback_path:
                            callback = import_from_string(callback_path)
                            if callback:
                                callback()

        def load_post_admin_autodiscover_callbacks():
            from django.conf import settings

            for app in settings.INSTALLED_APPS:
                callback_paths_path = app + ".post_admin_autodiscover_callbacks"
                callback_paths = import_from_string(callback_paths_path)
                if callback_paths:
                    for callback_path in callback_paths:
                        if callback_path:
                            callback = import_from_string(callback_path)
                            if callback:
                                callback()

        from django.contrib import admin

        admin_old_autodiscover = admin.autodiscover

        def admin_new_autodiscover():
            load_pre_admin_autodiscover_callbacks()
            admin_old_autodiscover()
            load_post_admin_autodiscover_callbacks()

        admin.autodiscover = admin_new_autodiscover

    def load_pre_app_ready_callbacks(self):
        from django.conf import settings

        for app in settings.INSTALLED_APPS:
            callback_paths_path = app + ".pre_app_ready_callbacks"
            callback_paths = import_from_string(callback_paths_path)
            if callback_paths:
                for callback_path in callback_paths:
                    if callback_path:
                        callback = import_from_string(callback_path)
                        if callback:
                            callback()
