import django

try:
    # Django 1.7+ apps registry
    from django.apps.registry import apps
except ImportError:
    from django.db.models.loading import cache as apps
    apps.app_configs = True
    apps.set_installed_apps = lambda installed: None
    apps.unset_installed_apps = lambda: None


def cache_handled_init():
    return {} if django.VERSION < (1, 6) else set()
