"""
A command class inheriting from Command instead of BaseCommand
(similar to some of django's core commands like 'test')
"""

from optparse import make_option

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    option_list = (make_option('--dummy_base-zero', action='store_true',
                               help="App0 dummy command option"),)

    def handle(self, *args, **options):
        pass
