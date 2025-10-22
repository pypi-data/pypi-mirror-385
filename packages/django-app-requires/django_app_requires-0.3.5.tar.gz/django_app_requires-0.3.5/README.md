# django-app-requires

A simple tool that allows you to specify app dependencies and middleware dependencies in your application, and also allow you to add default values for your additional configurations, after then load all your application settings into your project's settings.


## Install

```
pip install django-app-requires
```

## Usage

**your_app/\_\_init\_\_.py**

```
app_requires = [
    "your",
    "required",
    "apps",
]

app_middleware_requires = [
    "your",
    "required",
    "middlewares",
]

# Django's setting key must be in upper case.
# default values will be overrided by items in pro/settings.py.

app_setting_defaults = {
    "HELLO": "WORLD",
}

app_setting_callbacks = {
    "your_app.setting_callbacks.callback1",
}
```

**your_app/setting_callbacks.py**

```
def callback1(globals):
    globals["EXTRA_ITEM"] = "EXTRA_VALUE"
```

**pro/settings**

```
INSTALLED_APPS = [
    ...
    'your_app',
    ...
]

#
# at the bottom of settings.py
#
from django_app_requires import patch_all
patch_all()

# so the final INSTALLED_APPS = [
#     "your",
#     "required",
#     "apps",
#     "your_app",
#     "django_app_requires",
# ]

# so the final MIDDLEWARE = [
#    ...
#    "your",
#    "required",
#    "middlewares",
#    ...
# ]

# so the final you got a new setting item:
# HELLO = "WORLD"

## so the final you got a new setting item which provided by callback1:
# EXTRA_ITEM = "EXTRA_VALUE"
```


## Releases

### v0.1.0

- First release.

### v0.1.1

- Add fastutils & magic-import in requirements.txt.
- Fix problems of recursive required.

### v0.2.0

- Add collect_requirements function. **Removed**

### v0.2.1

- Don't scan all app, exclude third-part apps.
- Suggest to use collect_requirements command before doing project package.

### v0.2.2

- Output sorting.

### v0.2.3

- Remove collect_requirements command.
- Test with Django 3.2.

### v0.2.4

- We are not care about Django's version and fastutils' version, so let the end user to choose the version.

### v0.2.5

- Fix bdist_wheel problem that including useless files.


### v0.3.0

- Rename add_app_requires to load_app_requires.
- Add load_app_middleware_requires.
- Add load_app_setting_defaults.
- Add load_app_setting_callbacks.
- Add patch_all to load_app_requires, load_app_middleware_requires, load_app_setting_defaults and load_app_setting_callbacks.

### v0.3.1

- Fix app_setting_callbacks duplicate load problem.

### v0.3.2

- Doc update.
- Use zenutils.

### v0.3.3

- Doc update.

### v0.3.4

- Fix unit tests.

### v0.3.5

- Doc update.
