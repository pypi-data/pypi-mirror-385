# wt-django-templatetags
[![Pytest](https://github.com/ian-wt/wt-django-templatetags/actions/workflows/pytest.yaml/badge.svg)](https://github.com/ian-wt/wt-django-templatetags/actions/workflows/pytest.yaml)
[![codecov](https://codecov.io/gh/ian-wt/wt-django-templatetags/graph/badge.svg?token=9MHTDPGG1N)](https://codecov.io/gh/ian-wt/wt-django-templatetags)

Useful templatetags for Django projects.

## Installation
Install from PyPI:
```shell
pip install wt-django-templatetags
```

Install from GitHub:

To install the development branch from GitHub:
```shell
pip install "wt-django-templatetags @ git+https://github.com/ian-wt/wt-django-templatetags.git"
```

Once installed, add `wt_templatetags` to `INSTALLED_APPS` in your settings module.

```python
INSTALLED_APPS = [
    # other packages
    'wt_templatetags',
]
```

Alternatively, you could register a particular module of templatetags directly in your
`TEMPLATES` setting.

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                ...
            ],
            'libraries': {
                'pagination_tags': 'wt_templatetags.templatetags.pagination_tags',
            }
        },
    },
]
```
This is most useful when you're only interested in using a limited set
of modules from the broader project and that's unlikely to change. 
For simplicity, I recommend using the `INSTALLED_APPS` approach rather 
than selectively registering modules.

## Use
### Pagination Tags
To use the `pagination_tags` templatetags library in your project,
first load the tags with `{% load pagination_tags %}`.

To use the `relative_url` tag, you need to pass to the tag a page index.
This could be a number or the string `'last'` if the index is in the final
position of the paginated `QuerySet`. The tag additionally accepts optional
arguments for `field_name` and `urlencode`.

Most often, you'll leave the `field_name` parameter alone since the default
value of `'page'` is fairly semantic as it is. However, this value can be
overridden in your views so make sure your views and the `field_name` 
are consistent.

Last, the `urlencode` parameter is used when a query string may be present.
If your view won't ever handle a query string, then you can leave the default
value of `None` alone.

#### Example
```html
{% extends 'base.html' %}
{% load pagination_tags %}
<h1>Hello World!</h1>
<a href="{% relative_url page_obj.next_page_number %}">Next Page</a>
```
To extend this example further we can supply values to override the defaults:
```html
{% extends 'base.html' %}
{% load pagination_tags %}
<h1>Hello World!</h1>
<a href="{% relative_url page_obj.next_page_number 'page' request.GET.urlencode %}">Next Page</a>
```

### Static Tags
To use the static_tags template tags library in your project, first load the tags with {% load static_tags %}

#### static_min
Use the `static_min` tag to update a static file's path with a suffix indicating a minimized file is being used.

The path `main.css` becomes `main.min.css` with `{% static_min 'main.css %}'`.

The types of static files affect can be overridded by providing a list or tuple
of extension types as strings in the form of '.<ext>' and has a default value of `['.css', '.js']`.

The value for 'min' can be overridded with the setting `MIN_SUFFIX`.

By default, the tag returns the path unaffected if no extensions match. If you
prefer an exception be raised (not recommended in production), use setting `STATIC_MIN_FAIL_SILENT=False`.

#### static_version
Browsers like to cache static files. This can be inconvenience when we're 
pushing updates to resources like style sheets and javascript. We can often
force a refresh by appending a query string to trick the browser into thinking
the file has changed. This tag does that.

Use the `static_version` tag to append a query string containing a version
established with the setting `STATIC_VERSION`. Ideally, this value is set with
an environment variable.

The path `main.css` becomes `main.css?v=1.2.3` with `{% static_version 'main.css' %}`
and the setting `STATIC_VERSION=1.2.3`.

If a version isn't provided to settings, the tag will return the original path
unmodified. If you prefer an exception be raised (not recommended in production),
use setting `STATIC_VERSION_FAIL_SILENT=True`.

#### smart_static
Use the `smart_static` tag to conditionally apply the tags `static_min` and `static_version`
for different environments. For example, you probably only want minified files and versioning
in a production environment.

To apply the conditional logic, set the value for setting `SMART_STATIC_ACTIVE` to `True`
for production and `False` for development. The value defaults to `False` so you
only need to set this in production.

#### Example Settings

```python
# settings.py
import os

IS_PRODUCTION = os.getenv('IS_PRODUCTION', False)

WT_TEMPLATETAGS = {
    'SMART_STATIC_ACTIVE': IS_PRODUCTION,
}
```
