django-mcmo
===========

(c) 2014 Thomas Khyn

MCMO stands for 'Management Command Multiple Override'
Allows multiple apps to override the same management command in Django


Usage
-----

1. Install using your prefered method
2. replace the line::

	from django.core import management

by::

	from multiple_mngt_cmd_override import management

in your manage.py file

3. You can now use applications that concurrently define overrides for
   django.core management commands. Both commands will be called.


Alternative usage
-----------------

If your manage.py is automatically generated (e.g. if you are using buildout
and djangorecipe), simply make sure that the statement::

	import multiple_mngt_cmd_override

is executed before calling django.management.execute_from_command_line.

Importing the package patches the django.core.management module, which
functions are then multiple-override enabled.


Limitations
-----------

The same-name overrides must derive from the same Command class, or at least
from the same Command base class (AppCommand, LabelCommand or NoArgsCommand).

For example, if appA introduces a cmd management command with cmd.Command
deriving from AppCommand and appB introduces a cmd management command with
cmd.Command deriving from NoArgsCommand, appB's cmd.Command.handle_no_args will
never be called, as appA's cmd.Command.handle will be prioritary over
NoArgsCommand.handle.
