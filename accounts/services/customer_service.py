from accounts.models import CustomerProfile


class CustomerService:

    @staticmethod
    def get_profile(user):
        customer = CustomerProfile.objects.select_related("user").get(user=user)

        return {
            "id": customer.id,
            "full_name": customer.user.full_name,
            "phone_number": customer.user.phone_number,
            "email": customer.user.email,
            "profile_photo": (
                customer.profile_photo.url
                if customer.profile_photo
                else None
            ),
            "is_verified": True,
        }
    
    @staticmethod
    def update_profile(
        user,
        full_name=None,
        phone_number=None,
    ):
        customer = CustomerProfile.objects.select_related("user").get(
            user=user
        )

        if full_name:
            customer.user.full_name = full_name

        if phone_number:
            customer.user.phone_number = phone_number

        customer.user.save()

        return {
            "message": "Profile updated successfully.",
            "customer": {
                "id": customer.id,
                "full_name": customer.user.full_name,
                "phone_number": customer.user.phone_number,
                "email": customer.user.email,
                "profile_photo": (
                    customer.profile_photo.url
                    if customer.profile_photo
                    else None
                ),
                "is_verified": True,
            },
        }
    
    @staticmethod
    def update_profile_photo(user, profile_photo):
        customer = CustomerProfile.objects.get(user=user)

        customer.profile_photo = profile_photo
        customer.save()

        return {
            "message": "Profile photo updated successfully.",
            "profile_photo": (
                customer.profile_photo.url
                if customer.profile_photo
                else None
            ),
        }