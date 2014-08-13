django-mcmo
===========

|copyright| 2014 Thomas Khyn

MCMO stands for 'Management Command Multiple Override'
Allows multiple apps to override the same management command in Django

Compatible with Django 1.4 to 1.6 and matching Python 2 and 3 versions.

Usage
-----

1. Install using your prefered method
2. replace the line::

    from django.core import management

by::

    from django_mcmo import management

in your manage.py file

3. You can now use applications that concurrently define overrides for
   django.core management commands. Both commands will be called.


Alternative usage
-----------------

If your manage.py is automatically generated (e.g. if you are using buildout
and djangorecipe), simply make sure that the statement::

    import django_mcmo

is executed before calling django.management.execute_from_command_line.

Importing the package patches the django.core.management module, which
functions are then multiple-override enabled.


Limitations
-----------

The same-name overrides must derive from the same Command class, or at least
from the same Command base class (AppCommand, LabelCommand or NoArgsCommand).

In practice, same-name command will only be met when two apps override a
core django management command. They will therefore derive from the same
Command class, and cause no issue (except if the same options are defined in
the two commands).

.. |copyright| unicode:: 0xA9
