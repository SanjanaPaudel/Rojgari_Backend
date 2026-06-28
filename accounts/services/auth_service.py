from django.db import transaction

from accounts.models import (
    User,
    CustomerProfile,
    WorkerProfile,
)


class AuthService:

    @staticmethod
    @transaction.atomic
    def create_customer(validated_data):

        validated_data.pop("confirm_password")

        password = validated_data.pop("password")

        user = User.objects.create(
            role="customer",
            **validated_data,
        )

        user.set_password(password)
        user.save()

        CustomerProfile.objects.create(
            user=user
        )

        return user


    @staticmethod
    @transaction.atomic
    def create_worker(validated_data):

        validated_data.pop("confirm_password")

        citizenship = validated_data.pop("citizenship")

        password = validated_data.pop("password")

        user = User.objects.create(
            role="worker",
            **validated_data,
        )

        user.set_password(password)
        user.save()

        WorkerProfile.objects.create(
            user=user,
            citizenship=citizenship,
        )

        return user