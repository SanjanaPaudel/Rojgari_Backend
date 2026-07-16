from accounts.models import Skill, WorkerProfile


class WorkerService:
    @staticmethod
    def update_online_status(user, is_online):
        worker = WorkerProfile.objects.get(user=user)

        worker.is_online = is_online
        worker.save()

        return {
            "message": ("You are now online." if is_online else "You are now offline."),
            "is_online": worker.is_online,
        }

    @staticmethod
    def get_profile(user):
        profile = user.workerprofile

        return {
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "email": user.email,
            "about_me": profile.about_me,
            "service_areas": profile.service_areas,
            "profile_photo": (
                profile.profile_photo.url if profile.profile_photo else None
            ),
        }

    @staticmethod
    def update_profile(user, data):
        profile = user.workerprofile

        user_data = data.get("user", {})

        user.full_name = user_data.get(
            "full_name",
            user.full_name,
        )

        user.email = user_data.get(
            "email",
            user.email,
        )

        profile.about_me = data.get(
            "about_me",
            profile.about_me,
        )

        profile.service_areas = data.get(
            "service_areas",
            profile.service_areas,
        )

        user.save()
        profile.save()

        return WorkerService.get_profile(user)

    @staticmethod
    def upload_profile_photo(user, photo):
        profile = user.workerprofile

        profile.profile_photo = photo

        profile.save()

        return {
            "message": "Profile photo updated successfully.",
            "profile_photo": profile.profile_photo.url,
        }

    @staticmethod
    def upload_identity_documents(user, data):
        worker = user.workerprofile

        worker.citizenship_front = data["citizenship_front"]
        worker.citizenship_back = data["citizenship_back"]

        if data.get("experience_document"):
            worker.experience_document = data["experience_document"]

        # Documents uploaded.
        # Admin verification will happen later.
        worker.is_verified = False

        worker.save()

        return worker

    @staticmethod
    def update_skills(user, skill_ids):
        worker = user.workerprofile

        skills = Skill.objects.filter(
            id__in=skill_ids,
            is_active=True,
        )

        worker.skills.set(skills)

        return {
            "message": "Skills updated successfully.",
            "skills": [skill.name for skill in worker.skills.all()],
        }
