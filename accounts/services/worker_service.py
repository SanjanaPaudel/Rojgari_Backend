from accounts.models import WorkerProfile


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
                profile.profile_photo.url
                if profile.profile_photo
                else None
            ),
        }

    @staticmethod
    def update_profile(user, data):
        profile = user.workerprofile

        user.full_name = data.get(
            "full_name",
            user.full_name,
        )

        user.email = data.get(
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