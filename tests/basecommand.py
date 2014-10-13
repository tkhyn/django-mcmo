"""
Tests the behavior for commands originally inherited from 'BaseCommand'
Typical example: the 'test' command
"""

import warnings

from mcmo.management import CommandWarning

from .base import TestCase


class DummyBaseTests(TestCase):

    apps = ('app1', 'app2')

    def call_command(self, *args):
        # the command should not raise any warning
        warnings.filterwarnings('error', category=CommandWarning)
        try:
            super(DummyBaseTests, self).call_command(*args)
        finally:
            warnings.resetwarnings()

    def test_call_base_command(self):
        self.call_command('dummy_base')