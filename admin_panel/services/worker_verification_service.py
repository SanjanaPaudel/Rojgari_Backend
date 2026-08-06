from admin_panel.repositories.worker_verification_repository import (
    WorkerVerificationRepository,
)


class WorkerVerificationService:

    @staticmethod
    def get_pending_workers():

        workers = WorkerVerificationRepository.get_pending_workers()

        data = []

        for worker in workers:
            data.append(
                {
                    "id": worker.id,
                    "full_name": worker.user.full_name,
                    "phone_number": worker.user.phone_number,
                    "email": worker.user.email,
                    "profile_photo": (
                        worker.profile_photo.url
                        if worker.profile_photo
                        else None
                    ),
                    "skills": [
                        skill.name
                        for skill in worker.skills.all()
                    ],
                    "submitted_on": worker.user.date_joined,
                    "status": worker.verification_status,
                }
            )

        return data