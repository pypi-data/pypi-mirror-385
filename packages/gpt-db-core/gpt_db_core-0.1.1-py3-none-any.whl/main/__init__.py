"""
Main — A self-contained GPT database engine built with Django + Torch.
Auto-configures SQLite, runs migrations, and provides a GPT interface.
"""

from .apps import MainConfig

__all__ = ["GPT", "MainConfig", "setup"]


def setup(sqlite_path: str = "gptdb.sqlite3", auto_migrate: bool = True):
    """
    Allow running without a Django project (standalone mode).

    Args:
        sqlite_path (str): Path to the SQLite database file.
        auto_migrate (bool): Automatically run migrations if True.
    """
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "main",
            ],
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": sqlite_path,
                }
            },
            USE_TZ=True,
            TIME_ZONE="UTC",
            SECRET_KEY="gptdb-standalone",
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        )

        import django
        django.setup()

        if auto_migrate:
            from django.core.management import call_command
            call_command("migrate", interactive=False, run_syncdb=True, verbosity=0)

    print(f"✅ GPT-DB setup complete (SQLite: {sqlite_path})")

    # Lazy import to ensure Django is ready
    global GPT
    from .nn_mini import MiniGPT as GPT


# Auto-load if already in a Django project
try:
    from django.conf import settings
    if settings.configured:
        from .nn_mini import MiniGPT as GPT
except Exception:
    pass
