from datetime import UTC

import factory
from django.db.models.signals import post_save

from accounts.models import Customer, User, Worker, WorkerDocument
from bookings.models import Booking, Review, WorkerLocationHistory
from notifications.models import Notification
from payments.models import Payment
from services.models import ServiceCategory, ServiceRequest, WorkerService


@factory.django.mute_signals(post_save)
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    full_name = factory.LazyAttribute(lambda o: f"{o.first_name} {o.last_name}")
    phone_number = factory.Faker("phone_number")
    role = factory.Iterator(["customer", "worker"])
    is_active = True
    is_verified = factory.Faker("boolean", chance_of_getting_true=75)

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted or "password123")
        if create:
            self.save()


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    user = factory.SubFactory(UserFactory, role="customer")
    address = factory.Faker("address")
    default_lat = factory.Faker("latitude")
    default_lng = factory.Faker("longitude")


class WorkerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Worker

    user = factory.SubFactory(UserFactory, role="worker")
    bio = factory.Faker("text", max_nb_chars=200)
    avg_rating = factory.Faker(
        "pyfloat", left_digits=1, right_digits=1, min_value=1.0, max_value=5.0
    )
    total_jobs = factory.Faker("random_int", min=0, max=100)
    is_available = factory.Faker("boolean", chance_of_getting_true=80)
    is_approved = factory.Faker("boolean", chance_of_getting_true=75)
    current_lat = factory.Faker("latitude")
    current_lng = factory.Faker("longitude")
    current_location = factory.LazyAttribute(
        lambda o: f"POINT({o.current_lng} {o.current_lat})"
    )
    bank_account = factory.Faker("iban")
    wallet_number = factory.Faker("phone_number")
    approved_at = factory.Faker("date_time_this_year", tzinfo=UTC)


class WorkerDocumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WorkerDocument

    worker = factory.SubFactory(WorkerFactory)
    document_type = factory.Iterator(["citizenship", "driving_license", "pan_card"])
    file_url = factory.Faker("url")
    verification_status = factory.Iterator(["pending", "approved", "rejected"])
    rejection_reason = factory.Maybe(
        factory.LazyAttribute(lambda o: o.verification_status == "rejected"),
        yes_declaration=factory.Faker("sentence"),
        no_declaration=None,
    )


class ServiceCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ServiceCategory
        django_get_or_create = ("name",)

    name = factory.Iterator(
        ["Plumbing", "Electrical", "House Cleaning", "Painting", "Carpentry"]
    )
    description = factory.Faker("sentence")
    icon_url = factory.Faker("url")
    is_active = True


class WorkerServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WorkerService

    worker = factory.SubFactory(WorkerFactory)
    category = factory.SubFactory(ServiceCategoryFactory)
    years_experience = factory.Faker("random_int", min=1, max=15)
    skill_level = factory.Iterator(["Beginner", "Intermediate", "Expert"])
    hourly_rate = factory.Faker(
        "pydecimal", left_digits=3, right_digits=2, min_value=10, max_value=100
    )


class ServiceRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ServiceRequest

    customer = factory.SubFactory(CustomerFactory)
    category = factory.SubFactory(ServiceCategoryFactory)
    description = factory.Faker("paragraph")
    status = factory.Iterator(["pending", "accepted", "completed", "cancelled"])
    customer_lat = factory.Faker("latitude")
    customer_lng = factory.Faker("longitude")
    customer_location = factory.LazyAttribute(
        lambda o: f"POINT({o.customer_lng} {o.customer_lat})"
    )
    address = factory.Faker("address")
    expires_at = factory.Faker("date_time_this_month", tzinfo=UTC)


class BookingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Booking

    request = factory.SubFactory(ServiceRequestFactory)
    worker = factory.SubFactory(WorkerFactory)
    status = factory.Iterator(["accepted", "started", "completed", "cancelled"])
    agreed_price = factory.Faker(
        "pydecimal", left_digits=3, right_digits=2, min_value=20, max_value=200
    )
    started_at = factory.Faker("date_time_this_month", tzinfo=UTC)
    completed_at = factory.Maybe(
        factory.LazyAttribute(lambda o: o.status == "completed"),
        yes_declaration=factory.Faker("date_time_this_month", tzinfo=UTC),
        no_declaration=None,
    )
    cancelled_at = factory.Maybe(
        factory.LazyAttribute(lambda o: o.status == "cancelled"),
        yes_declaration=factory.Faker("date_time_this_month", tzinfo=UTC),
        no_declaration=None,
    )
    cancellation_reason = factory.Maybe(
        factory.LazyAttribute(lambda o: o.status == "cancelled"),
        yes_declaration=factory.Faker("sentence"),
        no_declaration=None,
    )


class PaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payment

    booking = factory.SubFactory(BookingFactory)
    amount = factory.SelfAttribute("booking.agreed_price")
    method = factory.Iterator(["esewa", "khalti", "cod"])
    status = factory.Iterator(["pending", "completed", "failed"])
    transaction_ref = factory.Faker("uuid4")
    paid_at = factory.Maybe(
        factory.LazyAttribute(lambda o: o.status == "completed"),
        yes_declaration=factory.Faker("date_time_this_month", tzinfo=UTC),
        no_declaration=None,
    )


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    booking = factory.SubFactory(BookingFactory)
    reviewer = factory.SubFactory(UserFactory)
    reviewee = factory.SubFactory(UserFactory)
    rating = factory.Faker("random_int", min=1, max=5)
    comment = factory.Faker("sentence")


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    user = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence")
    body = factory.Faker("paragraph")
    type = factory.Iterator(["booking_update", "payment_success", "new_request"])
    is_read = factory.Faker("boolean", chance_of_getting_true=30)
    reference_id = factory.Faker("uuid4")
    reference_type = factory.Iterator(["Booking", "Payment"])


class WorkerLocationHistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WorkerLocationHistory

    worker = factory.SubFactory(WorkerFactory)
    lat = factory.Faker("latitude")
    lng = factory.Faker("longitude")
    location = factory.LazyAttribute(lambda o: f"POINT({o.lng} {o.lat})")
