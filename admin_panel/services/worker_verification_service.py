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
                        worker.profile_photo.url if worker.profile_photo else None
                    ),
                    "skills": [skill.name for skill in worker.skills.all()],
                    "submitted_on": worker.user.date_joined,
                    "status": worker.verification_status,
                }
            )

        return data

    @staticmethod
    def get_worker_details(worker_id):

        worker = WorkerVerificationRepository.get_worker(worker_id)

        if worker is None:
            return None

        return {
            "id": worker.id,
            "full_name": worker.user.full_name,
            "phone_number": worker.user.phone_number,
            "email": worker.user.email,
            "verification_status": worker.verification_status,
            "years_of_experience": worker.years_of_experience,
            "about_me": worker.about_me,
            "service_areas": worker.service_areas,
            "permanent_address": worker.permanent_address,
            "skills": [skill.name for skill in worker.skills.all()],
            "profile_photo": (
                worker.profile_photo.url if worker.profile_photo else None
            ),
            "citizenship_front": (
                worker.citizenship_front.url if worker.citizenship_front else None
            ),
            "citizenship_back": (
                worker.citizenship_back.url if worker.citizenship_back else None
            ),
            "experience_document": (
                worker.experience_document.url if worker.experience_document else None
            ),
            "submitted_on": worker.user.date_joined,
        }

    @staticmethod
    def approve_worker(worker_id):

        worker = WorkerVerificationRepository.get_worker(worker_id)

        if worker is None:
            return {
                "success": False,
                "message": "Worker not found.",
            }

        if worker.verification_status == "verified":
            return {
                "success": False,
                "message": "Worker is already verified.",
            }

        WorkerVerificationRepository.approve_worker(worker)

        return {
            "success": True,
            "message": "Worker verified successfully.",
        }

    @staticmethod
    def reject_worker(worker_id):

        worker = WorkerVerificationRepository.get_worker(worker_id)

        if worker is None:
            return {
                "success": False,
                "message": "Worker not found.",
            }

        if worker.verification_status == "rejected":
            return {
                "success": False,
                "message": "Worker is already rejected.",
            }

        WorkerVerificationRepository.reject_worker(worker)

        return {
            "success": True,
            "message": "Worker rejected successfully.",
        }

    @staticmethod
    def get_verified_workers():

        workers = WorkerVerificationRepository.get_verified_workers()

        data = []

        for worker in workers:
            data.append(
                {
                    "id": worker.id,
                    "full_name": worker.user.full_name,
                    "phone_number": worker.user.phone_number,
                    "email": worker.user.email,
                    "profile_photo": (
                        worker.profile_photo.url if worker.profile_photo else None
                    ),
                    "skills": [skill.name for skill in worker.skills.all()],
                    "verification_status": worker.verification_status,
                    "verified_on": worker.user.date_joined,
                }
            )

        return data


    @staticmethod
    def get_all_workers():

        workers = WorkerVerificationRepository.get_all_workers()

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
                    "verification_status": worker.verification_status,
                    "submitted_on": worker.user.date_joined,
                }
            )

        return data

    @staticmethod
    def get_worker_statistics():

        return WorkerVerificationRepository.get_worker_statistics()