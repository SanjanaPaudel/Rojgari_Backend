from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(
        self,
        phone_number,
        password=None,
        **extra_fields,
    ):
        if not phone_number:
            raise ValueError("Phone number is required.")

        user = self.model(
            phone_number=phone_number,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)

        # Auto-create associated profile based on role so tests and
        # upstream logic can assume profile objects exist immediately.
        try:
            from accounts.models import CustomerProfile, WorkerProfile

            if getattr(user, "role", None) == "customer":
                CustomerProfile.objects.get_or_create(user=user)

            elif getattr(user, "role", None) == "worker":
                WorkerProfile.objects.get_or_create(user=user)
        except Exception:
            # Avoid failing user creation if profiles cannot be created here.
            pass

        return user

    def create_superuser(
        self,
        phone_number,
        password,
        **extra_fields,
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(
            phone_number,
            password,
            **extra_fields,
        )
