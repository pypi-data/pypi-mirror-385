from django.conf import settings
from django.test.signals import setting_changed

# TODO: Implement validation system checks

DEFAULTS = {
    # validate is sequence
    # validate items are string
    # validate char first position is dot
    'STATIC_EXTENSIONS': ['.css', '.js'],
    # validation is string
    'MIN_SUFFIX': 'min',
    # validate is bool
    'STATIC_MIN_FAIL_SILENT': True,
    # validate string
    'STATIC_VERSION': None,
    # validate bool
    'STATIC_VERSION_FAIL_SILENT': True,
    # validate bool
    'SMART_STATIC_ACTIVE': False
}


class AppSettings:
    """
    Settings for wt_django_templatetags are all namespaced in the
       WT_TEMPLATETAGS setting. This module provides the 'api_setting'
       object that's used to access app settings. User settings are checked
       and defaults are used as a fallback if user settings aren't found.

    """

    # The format of this settings object follows the drf approach.

    def __init__(self, defaults=None, user_settings=None):
        self.defaults = defaults or DEFAULTS
        if user_settings:
            self._user_settings = user_settings
        # for reload method
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'WT_TEMPLATETAGS', {})
        return self._user_settings

    def __getattr__(self, attr):
        # called when an AttributeError is raised

        if not attr in self.defaults:
            # check defaults first
            raise AttributeError(f"Invalid setting: {attr}.")

        try:
            # check first if there's a user setting
            val = self.user_settings[attr]
        except KeyError:
            # use defaults if not in user_settings
            val = self.defaults[attr]

        # remember cached attributes for reload
        self._cached_attrs.add(attr)
        # now cache the result
        setattr(self, attr, val)
        return val

    def reload(self):
        for attr in self._cached_attrs:
            # only remove attrs that have been cached
            delattr(self, attr)
        # now clear the set to start over
        self._cached_attrs.clear()

        if hasattr(self, '_user_settings'):
            delattr(self, '_user_settings')


app_settings = AppSettings(DEFAULTS, None)

def reload_app_settings(*_, **kwargs):
    if kwargs.get('setting') == 'WT_TEMPLATETAGS':  # pragma: no cover
        app_settings.reload()

# handle settings changes automatically
# if not implemented, tests will need to call reload() if any
#   settings are overriddden
setting_changed.connect(reload_app_settings)
