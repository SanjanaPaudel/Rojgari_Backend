from accounts.models import WorkerProfile


class WorkerService:

    @staticmethod
    def update_online_status(user, is_online):
        worker = WorkerProfile.objects.get(user=user)

        worker.is_online = is_online
        worker.save()

        return {
            "message": (
                "You are now online."
                if is_online
                else "You are now offline."
            ),
            "is_online": worker.is_online,
        }