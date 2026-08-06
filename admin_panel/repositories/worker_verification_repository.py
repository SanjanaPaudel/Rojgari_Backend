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