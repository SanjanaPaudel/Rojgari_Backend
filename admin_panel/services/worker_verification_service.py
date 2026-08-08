from admin_panel.repositories.worker_verification_repository import (
    WorkerVerificationRepository,
)
from notifications.notification_service import NotificationService


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

        history = worker.verification_history.select_related("admin").order_by(
            "-created_at"
        )

        skills = list(worker.skills.all())

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
            "jobs_completed": (
                WorkerVerificationRepository.get_completed_jobs_count(worker)
            ),
            "average_rating": worker.average_rating,
            "total_reviews": worker.total_reviews,
            "skills": [skill.name for skill in skills],
            "primary_skill": skills[0].name if skills else None,
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
            "verification_history": [
                {
                    "action": item.action,
                    "admin_name": (item.admin.full_name if item.admin else None),
                    "note": item.note,
                    "created_at": item.created_at,
                }
                for item in history
            ],
        }

    @staticmethod
    def approve_worker(worker_id, admin_user, note=""):
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

        WorkerVerificationRepository.approve_worker(
            worker,
            admin_user,
            note,
        )

        NotificationService.send_to_user(
            user=worker.user,
            title="Worker Verification Approved",
            body=(
                "Your worker verification has been approved."
                if not note
                else f"Your worker verification has been approved. Note: {note}"
            ),
            notification_type="worker_verification_approved",
            data={
                "type": "worker_verification_approved",
                "worker_id": str(worker.id),
            },
        )

        return {
            "success": True,
            "message": "Worker verified successfully.",
        }

    @staticmethod
    def reject_worker(worker, admin_user, note=""):
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

        WorkerVerificationRepository.reject_worker(
            worker,
            admin_user,
            note,
        )

        NotificationService.send_to_user(
            user=worker.user,
            title="Worker Verification Rejected",
            body=(
                "Your worker verification has been rejected."
                if not note
                else f"Your worker verification has been rejected. Note: {note}"
            ),
            notification_type="worker_verification_rejected",
            data={
                "type": "worker_verification_rejected",
                "worker_id": str(worker.id),
            },
        )

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
            skills = list(worker.skills.all())

            data.append(
                {
                    "id": worker.id,
                    "full_name": worker.user.full_name,
                    "phone_number": worker.user.phone_number,
                    "email": worker.user.email,
                    "profile_photo": (
                        worker.profile_photo.url if worker.profile_photo else None
                    ),
                    # Skills
                    "skills": [skill.name for skill in skills],
                    "primary_skill": (skills[0].name if skills else None),
                    # Professional information
                    "years_of_experience": worker.years_of_experience,
                    # Verification
                    "verification_status": worker.verification_status,
                    "submitted_on": worker.user.date_joined,
                    # Work statistics
                    "jobs_completed": (
                        WorkerVerificationRepository.get_completed_jobs_count(worker)
                    ),
                    "average_rating": worker.average_rating,
                    "total_reviews": worker.total_reviews,
                }
            )

        return data

    @staticmethod
    def get_worker_statistics():

        return WorkerVerificationRepository.get_worker_statistics()

    @staticmethod
    def request_resubmission(worker_id, admin_user, note=""):
        worker = WorkerVerificationRepository.get_worker(worker_id)

        if worker is None:
            return {
                "success": False,
                "message": "Worker not found.",
            }

        if worker.verification_status != "rejected":
            return {
                "success": False,
                "message": "Resubmission can only be requested for rejected workers.",
            }

        WorkerVerificationRepository.request_resubmission(
            worker,
            admin_user,
            note,
        )

        NotificationService.send_to_user(
            user=worker.user,
            title="Verification Resubmission Required",
            body=(
                "Please resubmit your verification documents."
                if not note
                else f"Please resubmit your verification documents. Note: {note}"
            ),
            notification_type="worker_verification_resubmission",
            data={
                "type": "worker_verification_resubmission",
                "worker_id": str(worker.id),
            },
        )

        return {
            "success": True,
            "message": "Resubmission requested successfully.",
        }
