from django.db import transaction
from django.utils import timezone

from accounts.models import Skill, WorkerProfile
from services.models import Booking


class DashboardRepository:
    @staticmethod
    def get_worker_statistics():
        return {
            "total": WorkerProfile.objects.count(),
            "verified": WorkerProfile.objects.filter(
                verification_status="verified"
            ).count(),
            "pending": WorkerProfile.objects.filter(
                verification_status="pending"
            ).count(),
            "rejected": WorkerProfile.objects.filter(
                verification_status="rejected"
            ).count(),
        }

    @staticmethod
    def get_booking_statistics():

        today = timezone.now().date()

        return {
            "today": Booking.objects.filter(created_at__date=today).count(),
            "completed_today": Booking.objects.filter(
                created_at__date=today,
                status="completed",
            ).count(),
            "working_today": Booking.objects.filter(
                created_at__date=today,
                status="working",
            ).count(),
            "total": Booking.objects.count(),
            "completed": Booking.objects.filter(
                status="completed",
            ).count(),
        }

    @staticmethod
    def get_skill_statistics():

        return {
            "total": Skill.objects.count(),
        }


class CategoryRepository:
    @staticmethod
    def get_all_categories():
        return Skill.objects.all().order_by("display_order", "id")

    @staticmethod
    def get_category(category_id):
        try:
            return Skill.objects.get(id=category_id)
        except Skill.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def create_category(data):
        display_order = data.pop("display_order", None)

        category = Skill.objects.create(
            **data,
            display_order=display_order or 1,
        )

        categories = list(
            Skill.objects.all().order_by(
                "display_order",
                "id",
            )
        )

        # Move the newly created category to the requested position.
        categories.remove(category)

        target_position = (
            display_order if display_order is not None else len(categories) + 1
        )

        target_position = max(
            1,
            min(target_position, len(categories) + 1),
        )

        categories.insert(
            target_position - 1,
            category,
        )

        for index, skill in enumerate(categories, start=1):
            if skill.display_order != index:
                skill.display_order = index
                skill.save(
                    update_fields=["display_order"],
                )

        return category

    @staticmethod
    @transaction.atomic
    def update_category(category, data):
        old_display_order = category.display_order

        new_display_order = data.get(
            "display_order",
            old_display_order,
        )

        # Update all fields except display_order first.
        for field, value in data.items():
            if field != "display_order":
                setattr(category, field, value)

        # If display_order did not change, simply save.
        if new_display_order == old_display_order:
            category.save()
            return category

        # Get all other categories in their current order.
        others = list(
            Skill.objects.exclude(
                pk=category.pk,
            ).order_by(
                "display_order",
                "id",
            )
        )

        # Keep the requested position inside a valid range.
        target_position = max(
            1,
            min(
                new_display_order,
                len(others) + 1,
            ),
        )

        # Insert the category at the requested position.
        others.insert(
            target_position - 1,
            category,
        )

        # Re-number everything from 1...N.
        for index, skill in enumerate(
            others,
            start=1,
        ):
            skill.display_order = index

            if skill.pk == category.pk:
                # Category has not been saved yet.
                continue

            skill.save(
                update_fields=["display_order"],
            )

        category.display_order = target_position
        category.save()

        return category

    @staticmethod
    def delete_category(category):
        category.is_active = False
        category.save(update_fields=["is_active"])
        return category
