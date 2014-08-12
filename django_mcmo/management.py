"""
Monkey-patching django.core.management functions
"""

import collections
from warnings import warn

from django.core import management as core_management
from django.core.exceptions import ImproperlyConfigured
from django.utils import six
from django.core.management.color import color_style


_commands = None


def get_commands():
    global _commands
    if _commands is None:
        _commands = dict([(name, ['django.core']) for name in \
            core_management.find_commands(core_management.__path__[0])])

        # Find the installed apps
        from django.conf import settings
        try:
            apps = settings.INSTALLED_APPS
        except ImproperlyConfigured:
            # Still useful for commands that do not require functional settings
            # like startproject or help
            apps = []

        # Find and load the management module for each installed app.
        for app_name in apps:
            try:
                path = core_management.find_management_module(app_name)
                for name in core_management.find_commands(path):
                    if name in _commands:
                        _commands[name].append(app_name)
                    else:
                        _commands[name] = [app_name]
            except ImportError:
                pass  # No management module - ignore this app

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
        for b in reversed(bases):
            if issubclass(app_cmd_class, b):
                # remove any base class of app_cmd_class already in the list
                bases.remove(b)
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
            else:
                warn('django-mcmo: Option redefinition in command "%s": --%s, '
                     'this may lead to unexpected behavior.' % (name, o_name))

    # easy case => no unnecessary subclassing
    if len(bases) == 1:
        return bases[0]()

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
        commands_dict = collections.defaultdict(lambda: [])
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
