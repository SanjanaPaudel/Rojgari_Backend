from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "accounts"

    def ready(self):
        # Import signal handlers to ensure they are registered when Django starts.
        # Importing here avoids app registry/circular import issues.
        try:
            import accounts.signals  # noqa: F401
        except Exception:
            # Avoid breaking startup if signals fail to import in some envs.
            pass
