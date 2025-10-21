# TODO: Add static_tags usage to docs.
from urllib import parse

from django.templatetags.static import StaticNode
from django import template

from wt_templatetags.settings import app_settings

register = template.Library()


# helper functions


def static_min(path):
    """
    Transform a static file path to use the minified version.

    Checks if the path ends with any extension in STATIC_EXTENSIONS,
    and if so, inserts STATIC_MIN_SUFFIX before the extension.

    Args:
        path (str): The static file path to transform (e.g., "/static/css/main.css")

    Returns:
        str: The transformed path with minified suffix inserted
             (e.g., "/static/css/main.min.css"), or the original path if
             no matching extension is found.

    Raises:
        ValueError: If no matching extension is found and
                    STATIC_MIN_FAIL_SILENT is False.
    """

    for ext in app_settings.STATIC_EXTENSIONS:
        if path.endswith(ext):
            path = path.replace(ext, f'.{app_settings.MIN_SUFFIX}{ext}')
            break
    else:
        if not app_settings.STATIC_MIN_FAIL_SILENT:
            raise ValueError(f"No matching extension for path '{path}' with "
                             f"extensions '{', '.join(app_settings.STATIC_EXTENSIONS)}")

    return path


def static_version(path):
    """
    Append a version query string to a static file path.

    Args:
        path (str): The static file path

    Returns:
        str: Path with version query string conditionally appended

    Raises:
        ValueError: If path is not a string
        AttributeError: If STATIC_VERSION not set and FAIL_SILENT is False
    """
    if not isinstance(path, str):
        raise ValueError(f"Expected string. Received type "
                         f"{type(path).__name__} instead.")

    if static_version_ := app_settings.STATIC_VERSION:
        return f"{path}?{parse.urlencode({'v' : static_version_})}"

    if app_settings.STATIC_VERSION_FAIL_SILENT:
        return path

    raise AttributeError(f"Required setting 'STATIC_VERSION' not set.")


# template tags


class StaticMinNode(StaticNode):
    """
    StaticNode subclass that transforms paths to use minified files.
    """

    @classmethod
    def handle_simple(cls, path):
        path = super().handle_simple(path)
        return static_min(path)


@register.tag('static_min')
def do_static_min(parser, token):
    """
    Extends Django 'static' template tag to transform path to use minified
       files (e.g., '.css' becomes '.min.css').

    Usage::

        {% static_min 'path/to/file.css' %}
        {% static_min variable_with_path %}
        {% static_min 'path/to/file.css' as versioned_css %}
        {% static_min variable_with_path as varname %}
    """
    return StaticMinNode.handle_token(parser, token)


class StaticVersionNode(StaticNode):
    """
    StaticNode subclass that appends version to path.
    """

    @classmethod
    def handle_simple(cls, path):
        path = super().handle_simple(path)
        return static_version(path)


@register.tag('static_version')
def do_static_version(parser, token):
    """
    Extends Django 'static' template tag to append a static version to the
       file path as a querystring to encourage browser refresh if
       versions change.

    Usage::

        {% static_version 'path/to/file.css' %}
        {% static_version variable_with_path %}
        {% static_version 'path/to/file.css' as versioned_css %}
        {% static_version variable_with_path as varname %}
    """
    return StaticVersionNode.handle_token(parser, token)


class SmartStaticNode(StaticNode):
    """
    Combines static_min and static_version with conditional logic for
       production vs development environments.
    """

    @classmethod
    def handle_simple(cls, path):
        # TODO: Add granular control w/ settings (SMART_STATIC_MINIFY,
        #  SMART_STATIC_VERSION) to allow independent control of minification
        #  and versioning
        path = super().handle_simple(path)
        if app_settings.SMART_STATIC_ACTIVE:
            return static_version(static_min(path))
        return path


@register.tag('smart_static')
def smart_static(parser, token):
    """
    Extends Django 'static' template tag and conditionally implements
       'static_min' and 'static_version' if setting 'SMART_STATIC_ACTIVE'
       is True.

    It's recommended this setting be established with an environment variable
       that indicates whether the environment is development or production.

    Usage::

        {% smart_static 'path/to/file.css' %}
        {% smart_static variable_with_path %}
        {% smart_static 'path/to/file.css' as versioned_css %}
        {% smart_static variable_with_path as varname %}
    """
    return SmartStaticNode.handle_token(parser, token)
