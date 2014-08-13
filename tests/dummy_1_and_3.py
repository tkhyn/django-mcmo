"""
Running dummy command defined in app1 (subclass of NoArgsCommand) and app3
(subclass of LabelCommand), demonstrating incompatibilities

Calling the 'dummy' command without args should fail when app1 is first in
INSTALLED_APPS. app1 command's handle method is indeed not called because
of MRO (the command class' bases are (app3.Command, app1.Command))

Calling the 'dummy' command with args should fail when app3 is first in
INSTALLED_APPS. app3 command's handle method is indeed not called because of
MRO (the final command class' bases are (app1.Command, app3.Command))

This behavior should be changed in future versions. Overriding a command with
different base classes should not be possible (and actually should never
happen).
"""

import warnings

from django.core.management import CommandError

from django_mcmo.management import CommandWarning

from .base import TestCase

# CommandWarning is converted to a catchable Exception
# this enables the use of assertRaises, and enables the warning to be
# raised multiple times (as the same warning cannot be raised twice, and
# erasing the warnings registry is not possible)
warnings.filterwarnings('error', category=CommandWarning)


class DummyOverrideTests(TestCase):

    __test__ = False

    def check_warning(self, w):
        self.assertEqual(len(w), 1)
        self.assertTrue('Possible command classes inheritance conflict'
                        in str(w[0].message))

    def call_command(self, *args):
        with self.assertRaises(CommandWarning):
            try:
                super(DummyOverrideTests, self).call_command(*args)
            except CommandError:
                # ignore subsequent command errors
                pass

    def test_called_without_args(self):
        self.call_command('dummy')

    def test_called_with_arg(self):
        self.call_command('dummy', 'app')


class DummyOverrideTests13(DummyOverrideTests):
    __test__ = True
    apps = ('app1', 'app3')


class DummyOverrideTests31(DummyOverrideTests):
    __test__ = True
    apps = ('app3', 'app1')
