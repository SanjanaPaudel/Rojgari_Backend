from django.core.exceptions import ObjectDoesNotExist

from accounts.models import WorkerProfile


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
    def approve_worker(worker):

        worker.verification_status = "verified"
        worker.save(update_fields=["verification_status"])

        return worker

    @staticmethod
    def reject_worker(worker):

        worker.verification_status = "rejected"
        worker.save(update_fields=["verification_status"])

        return worker

    @staticmethod
    def get_verified_workers():
        return (
            WorkerProfile.objects.select_related("user")
            .prefetch_related("skills")
            .filter(verification_status="verified")
            .order_by("-id")
        )
