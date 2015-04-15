import django
from django import test
from django.conf import settings
from django.utils.datastructures import SortedDict
from django.core import management as management_core
from django.utils import six

from mcmo import management as management_mcmo

from ._compat import apps, cache_handled_init


# nose should not look for tests in this module
__test__ = False
__unittest = True


NO_SETTING = ('!', None)


class TestSettingsManager(object):
    """
    A class which can modify some Django settings temporarily for a
    test and then revert them to their original values later.

    Automatically handles resyncing the DB if INSTALLED_APPS is
    modified.
    """

    def __init__(self):
        self._original_settings = {}

    def set(self, **kwargs):
        if not apps.app_configs:
            apps.populate(settings.INSTALLED_APPS)

        for k, v in six.iteritems(kwargs):
            self._original_settings.setdefault(k, getattr(settings,
                                                          k, NO_SETTING))
            setattr(settings, k, v)

        if 'INSTALLED_APPS' in kwargs:
            management_mcmo._commands = None
            apps.set_installed_apps(kwargs['INSTALLED_APPS'])
            self.syncdb()

    def syncdb(self):
        apps.loaded = False
        apps.app_labels = {}
        apps.app_store = SortedDict()
        apps.handled = cache_handled_init()
        apps.postponed = []
        apps.nesting_level = 0
        apps._get_models_cache = {}
        apps.available_apps = None

        management_core.call_command('syncdb', verbosity=0)

    def revert(self):
        for k, v in six.iteritems(self._original_settings):
            if v == NO_SETTING:
                delattr(settings, k)
            else:
                setattr(settings, k, v)

        if 'INSTALLED_APPS' in self._original_settings:
            apps.unset_installed_apps()
            self.syncdb()

        self._original_settings = {}


class TestCase(test.TestCase):
    """
    A subclass of the Django TestCase with a settings_manager
    attribute which is an instance of TestSettingsManager.

    Comes with a tearDown() method that calls
    self.settings_manager.revert().
    """

    apps = ()

    @classmethod
    def setUpClass(cls):
        apps = ['tests.%s' % a for a in cls.apps + ('app0',)]
        if django.VERSION < (1, 7):
            apps.reverse()
        cls._apps = apps
        cls.settings_manager = TestSettingsManager()
        cls.settings_manager.set(
            INSTALLED_APPS=settings.INSTALLED_APPS + cls._apps)

    @classmethod
    def tearDownClass(cls):
        cls.settings_manager.revert()

    @classmethod
    def is_in_options(cls, command, option):
        cmd_class = management_core.load_command_class(cls._apps, command)
        return option in [o.get_opt_string() for o in cmd_class.option_list]

    @staticmethod
    def call_command(command, *args, **options):
        management_core.call_command(command, *args, **options)

    def assertInOptions(self, command, option, msg=None):
        if not self.is_in_options(command, option):
            standardMsg = 'Option "%s" does not exist for command %s' \
                          % (option, command)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertNotInOptions(self, command, option, msg=None):
        if self.is_in_options(command, option):
            standardMsg = 'Option "%s" unexpectedly exists for command %s' \
                          % (option, command)
            self.fail(self._formatMessage(msg, standardMsg))
