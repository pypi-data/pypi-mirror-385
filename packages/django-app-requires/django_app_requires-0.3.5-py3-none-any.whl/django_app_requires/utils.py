import inspect

from zenutils import listutils
from zenutils.importutils import import_from_string


def get_app_name(app):
    # we guess all AppConfigs are in the app's apps.py file
    if ".apps." in app:
        pos = app.find(".apps.")
        return app[:pos]
    return app


def load_app_requires(apps):
    apps = _load_app_requires(apps)
    apps = (
        [
            "django_app_requires_first_placeholder",
        ]
        + apps
        + [
            "django_app_requires_last_placeholder",
        ]
    )
    return apps


def _load_app_requires(apps, all_apps=None):
    all_apps = all_apps or set()
    applists = []
    for app in apps:
        if app in all_apps:
            continue
        all_apps.add(app)
        app = get_app_name(app)
        deps_path = app + ".app_requires"
        app_new_requires = import_from_string(deps_path)
        if app_new_requires:
            applists += _load_app_requires(app_new_requires, all_apps)
        applists.append(app)
    return listutils.unique(applists)


def load_app_middleware_requires(apps, middlewares):
    middlewares_lists = [] + middlewares
    for app in apps:
        app = get_app_name(app)
        middlewares_requires_path = app + ".app_middleware_requires"
        middlewares_requires = import_from_string(middlewares_requires_path)
        if middlewares_requires:
            middlewares_lists += middlewares_requires
    return listutils.unique(middlewares_lists)


def load_app_setting_defaults(apps):
    defaults = {}
    for app in apps:
        app = get_app_name(app)
        setting_defaults_path = app + ".app_setting_defaults"
        setting_defaults = import_from_string(setting_defaults_path)
        if setting_defaults:
            defaults.update(setting_defaults)
    return defaults


def load_app_setting_callbacks(apps, globals):
    """load app setting callbacks.

    The same path of setting callback will be only load once.
    """
    setting_callbacks_paths = []
    for app in apps:
        app = get_app_name(app)
        setting_callbacks_path = app + ".app_setting_callbacks"
        setting_callbacks = import_from_string(setting_callbacks_path)
        if setting_callbacks:
            for setting_callback_path in setting_callbacks:
                if not setting_callback_path in setting_callbacks_paths:
                    setting_callbacks_paths.append(setting_callback_path)
    for setting_callbacks_path in setting_callbacks_paths:
        callback = import_from_string(setting_callbacks_path)
        if callback:
            callback(globals)


def patch_all():
    """Do all patches for pro/settings.py. Call me only at pro/settings.py."""
    frame = inspect.currentframe()
    globals = frame.f_back.f_globals
    globals["INSTALLED_APPS"] = load_app_requires(globals["INSTALLED_APPS"])
    globals["MIDDLEWARE"] = load_app_middleware_requires(
        globals["INSTALLED_APPS"], globals["MIDDLEWARE"]
    )
    defaults = load_app_setting_defaults(globals["INSTALLED_APPS"])
    for key, value in defaults.items():
        if not key in globals:
            globals[key] = value
    load_app_setting_callbacks(globals["INSTALLED_APPS"], globals)


add_requires = load_app_requires
