from accounts.models import WorkerProfile


class WorkerDashboardService:
    @staticmethod
    def get_dashboard(user):
        worker = (
            WorkerProfile.objects.select_related("user")
            .prefetch_related("skills")
            .get(user=user)
        )

        skills = list(
            worker.skills.values_list(
                "name",
                flat=True,
            )
        )

        return {
            "worker": {
                "full_name": worker.user.full_name,
                "phone_number": worker.user.phone_number,
                "profile_photo": (
                    worker.profile_photo.url if worker.profile_photo else None
                ),
                "skills": skills,
                "years_of_experience": worker.years_of_experience,
                "verified": worker.is_verified,
                "is_online": worker.is_online,
                "stats": {
                    "jobs_done": 28,
                    "skills": len(skills),
                    "reviews": 12,
                    "rating": 4.8,
                },
            },
            "notifications": 3,
            "messages": 2,
            "incoming_request_count": 0,
        }
