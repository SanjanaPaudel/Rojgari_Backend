from django.core.exceptions import ObjectDoesNotExist

from accounts.models import WorkerProfile
from admin_panel.models import WorkerVerificationHistory
from services.models import Booking


class WorkerVerificationRepository:
    @staticmethod
    def get_pending_workers():
        return (
            WorkerProfile.objects.select_related("user")
            .prefetch_related("skills")
            .filter(verification_status="pending")
            .order_by("-id")
        )

    @staticmethod
    def get_worker(worker_id):
        try:
            return (
                WorkerProfile.objects.select_related("user")
                .prefetch_related("skills")
                .get(id=worker_id)
            )
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def reject_worker(worker, admin_user, note=""):
        worker.verification_status = "rejected"
        worker.save(update_fields=["verification_status"])

        WorkerVerificationHistory.objects.create(
            worker=worker,
            admin=admin_user,
            action="rejected",
            note=note,
        )

        return worker

    @staticmethod
    def get_all_workers():
        return (
            WorkerProfile.objects.select_related("user")
            .prefetch_related("skills")
            .order_by("-id")
        )

    @staticmethod
    def get_worker_statistics():
        return {
            "all": WorkerProfile.objects.count(),
            "pending": WorkerProfile.objects.filter(
                verification_status="pending"
            ).count(),
            "verified": WorkerProfile.objects.filter(
                verification_status="verified"
            ).count(),
            "rejected": WorkerProfile.objects.filter(
                verification_status="rejected"
            ).count(),
            "available_now": WorkerProfile.objects.filter(is_online=True).count(),
        }

    @staticmethod
    def approve_worker(worker, admin_user, note=""):
        worker.verification_status = "verified"
        worker.save(update_fields=["verification_status"])

        WorkerVerificationHistory.objects.create(
            worker=worker,
            admin=admin_user,
            action="approved",
            note=note,
        )

        return worker

    @staticmethod
    def request_resubmission(worker, admin_user, note=""):
        worker.verification_status = "pending"
        worker.save(update_fields=["verification_status"])

        WorkerVerificationHistory.objects.create(
            worker=worker,
            admin=admin_user,
            action="resubmission_requested",
            note=note,
        )

        return worker

    @staticmethod
    def get_completed_jobs_count(worker):
        return Booking.objects.filter(
            worker=worker,
            status="completed",
        ).count()
