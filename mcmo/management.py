"""
Monkey-patching django.core.management functions
"""

import os
from collections import defaultdict
import warnings

from django.core import management as core_management
from django.core.management.base import AppCommand, LabelCommand, NoArgsCommand
from django.core.exceptions import ImproperlyConfigured
from django.utils import six
from django.core.management.color import color_style


class CommandWarning(Warning):
    pass


_commands = None


def get_commands():
    global _commands
    if _commands is None:
        _commands = defaultdict(lambda: [])
        for name in core_management.find_commands(core_management.__path__[0]):
            _commands[name].append('django.core')

        # Find the paths to the management modules
        paths = []
        try:
            # django 1.7
            from django.apps import apps
            for app_config in apps.get_app_configs():
                paths.append((app_config.name,
                              os.path.join(app_config.path, 'management')))

        except ImportError:
            # django 1.6
            from django.conf import settings
            try:
                apps = settings.INSTALLED_APPS
            except ImproperlyConfigured:
                # Still useful for commands that do not require functional
                # settings like startproject or help
                apps = []

            # Find and load the management module for each installed app.
            for app_name in apps:
                try:
                    paths.append((app_name, core_management
                                  .find_management_module(app_name)))
                except ImportError:
                    pass  # No management module - ignore this app

        for app_name, path in paths:
            for name in core_management.find_commands(path):
                _commands[name].append(app_name)

    core_management._commands = _commands
    return _commands

core_management.get_commands = get_commands


def load_command_class(app_names, name):
    bases = []
    option_list = []
    option_list_names = []
    for app in reversed(app_names):
        module = core_management.import_module('%s.management.commands.%s' % \
                                               (app, name))
        # original command class
        app_cmd_class = module.Command

        add_cmd_class = True
        replaces_base = False
        for b in reversed(bases):
            if issubclass(app_cmd_class, b):
                # remove any base class of app_cmd_class already in the list
                bases.remove(b)
                replaces_base = True
            elif issubclass(b, app_cmd_class):
                # do not add the app_cmd_class if one of its subclasses
                # is already in the list
                add_cmd_class = False

        if add_cmd_class:
            bases.append(app_cmd_class)

        for o in app_cmd_class.option_list:
            o_name = o.get_opt_string()
            if o_name not in option_list_names:
                option_list.append(o)
                option_list_names.append(o_name)
            elif add_cmd_class and not replaces_base:
                warnings.warn(
                    'django-mcmo: Option redefinition in app "%s" for command '
                    '"%s": %s, this may lead to unexpected behavior.'
                    % (app, name, o_name),
                    CommandWarning)

    # easy case => no unnecessary subclassing
    if len(bases) == 1:
        return bases[0]()

    # check that all bases are subclasses the same Command base class
    # (NoArgsCommand, LabelCommand or AppCommand)
    common_bases = list(bases[0].__mro__)
    for b in bases[1:]:
        for c in set(common_bases).difference(b.__mro__):
            common_bases.remove(c)
    if not any(issubclass(common_bases[0], c)
               for c in (AppCommand, LabelCommand, NoArgsCommand)):
        warnings.warn(
             'Command "%s": Possible command classes inheritance conflict in '
             'apps %s. All command classes do not derive from the same django '
             'base class (AppCommand, LabelCommand, NoArgsCommand). This is '
             'likely to cause inconsistencies.' % (name, repr(app_names)),
             CommandWarning)

    # create Command class
    return type('Command', tuple(bases), {'option_list': option_list})()

core_management.load_command_class = load_command_class


def main_help_text(self, commands_only=False):
    if commands_only:
        usage = sorted(get_commands().keys())
    else:
        usage = [
            "",
            "Type '%s help <subcommand>' for help on a specific subcommand." \
                % self.prog_name,
            "",
            "Available subcommands:",
        ]
        commands_dict = defaultdict(lambda: [])
        for name, apps in six.iteritems(get_commands()):
            for app in apps:
                if app == 'django.core':
                    app = 'django'
                else:
                    app = app.rpartition('.')[-1]
                commands_dict[app].append(name)
        style = color_style()
        for app in sorted(commands_dict.keys()):
            usage.append("")
            usage.append(style.NOTICE("[%s]" % app))
            for name in sorted(commands_dict[app]):
                usage.append("    %s" % name)
    return '\n'.join(usage)

core_management.ManagementUtility.main_help_text = main_help_text
