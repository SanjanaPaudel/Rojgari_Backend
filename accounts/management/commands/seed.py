import random

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.factories import (
    BookingFactory,
    CustomerFactory,
    NotificationFactory,
    PaymentFactory,
    ReviewFactory,
    ServiceCategoryFactory,
    ServiceRequestFactory,
    UserFactory,
    WorkerDocumentFactory,
    WorkerFactory,
    WorkerLocationHistoryFactory,
    WorkerServiceFactory,
)
from accounts.models import Customer, User, Worker, WorkerDocument
from bookings.models import Booking, Review, WorkerLocationHistory
from notifications.models import Notification
from payments.models import Payment
from services.models import ServiceCategory, ServiceRequest, WorkerService


class Command(BaseCommand):
    help = "Seed database with mock users, customer profiles, worker profiles, services, requests, bookings, and payments."

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=15,
            help="Number of users (workers + customers) to create",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Deleting existing Rojgari data...")
        WorkerLocationHistory.objects.all().delete()
        Notification.objects.all().delete()
        Review.objects.all().delete()
        Payment.objects.all().delete()
        Booking.objects.all().delete()
        ServiceRequest.objects.all().delete()
        WorkerService.objects.all().delete()
        WorkerDocument.objects.all().delete()
        Worker.objects.all().delete()
        Customer.objects.all().delete()
        ServiceCategory.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        num_users = options["users"]
        self.stdout.write(f"Seeding service categories and {num_users} users...")

        # 1. Seed Service Categories
        categories_data = [
            (
                "Plumbing",
                "Fix leaks, pipes, and install toilets",
                "https://img.icons8.com/color/96/plumbing.png",
            ),
            (
                "Electrical",
                "Wiring, switchboard fixes, and lighting installation",
                "https://img.icons8.com/color/96/electricity.png",
            ),
            (
                "House Cleaning",
                "Deep cleaning, dusting, and vacuuming services",
                "https://img.icons8.com/color/96/broom.png",
            ),
            (
                "Painting",
                "Interior, exterior wall painting and finishing",
                "https://img.icons8.com/color/96/paint-roller.png",
            ),
            (
                "Carpentry",
                "Furniture repair, wood works, and custom assemblies",
                "https://img.icons8.com/color/96/saw.png",
            ),
        ]
        categories = []
        for name, desc, icon in categories_data:
            cat = ServiceCategoryFactory(name=name, description=desc, icon_url=icon)
            categories.append(cat)

        # 2. Seed Customers & Workers
        customers = []
        workers = []

        half_users = num_users // 2
        for i in range(half_users):
            # Seed Customer
            customer_user = UserFactory(
                username=f"customer_{i}", role="customer", is_verified=True
            )
            customer = CustomerFactory(user=customer_user)
            customers.append(customer)

            # Seed Worker
            worker_user = UserFactory(
                username=f"worker_{i}",
                role="worker",
                is_verified=random.choice([True, False]),
            )
            worker = WorkerFactory(user=worker_user)
            workers.append(worker)

            # Seed Worker Documents (1 to 2 documents per worker)
            for _ in range(random.randint(1, 2)):
                WorkerDocumentFactory(worker=worker)

            # Map services to workers (1 to 3 categories per worker)
            worker_cats = random.sample(categories, random.randint(1, 3))
            for cat in worker_cats:
                WorkerServiceFactory(worker=worker, category=cat)

        # 3. Seed Service Requests
        requests = []
        for i, customer in enumerate(customers):
            # 1 to 2 requests per customer
            for _ in range(random.randint(1, 2)):
                category = random.choice(categories)
                req = ServiceRequestFactory(
                    customer=customer,
                    category=category,
                    status=random.choice(
                        ["pending", "accepted", "completed", "cancelled"]
                    ),
                )
                requests.append(req)

        # 4. Seed Bookings, Payments, Reviews & Locations
        for req in requests:
            if req.status in ["accepted", "completed", "cancelled"]:
                # Select a worker who offers the requested service category
                matching_services = WorkerService.objects.filter(category=req.category)
                if not matching_services.exists():
                    continue
                worker = random.choice(matching_services).worker

                # Create Booking
                status = (
                    "completed"
                    if req.status == "completed"
                    else ("cancelled" if req.status == "cancelled" else "accepted")
                )
                booking = BookingFactory(request=req, worker=worker, status=status)

                # Create Payment
                payment_status = (
                    "completed"
                    if status == "completed"
                    else random.choice(["pending", "failed"])
                )
                PaymentFactory(
                    booking=booking, amount=booking.agreed_price, status=payment_status
                )

                # Create Reviews (if completed)
                if status == "completed":
                    # Customer reviews worker
                    ReviewFactory(
                        booking=booking,
                        reviewer=req.customer.user,
                        reviewee=worker.user,
                        rating=random.randint(3, 5),
                    )
                    # Worker reviews customer (optional)
                    if random.choice([True, False]):
                        ReviewFactory(
                            booking=booking,
                            reviewer=worker.user,
                            reviewee=req.customer.user,
                            rating=random.randint(4, 5),
                        )

        # 5. Seed some location histories for workers
        for worker in workers:
            for _ in range(random.randint(2, 5)):
                WorkerLocationHistoryFactory(worker=worker)

        # 6. Seed Notifications for users
        all_users = list(User.objects.all())
        for user in all_users:
            for _ in range(random.randint(1, 3)):
                NotificationFactory(user=user)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded:\n"
                f" - {len(categories)} Categories\n"
                f" - {len(customers)} Customers\n"
                f" - {len(workers)} Workers\n"
                f" - {ServiceRequest.objects.count()} Service Requests\n"
                f" - {Booking.objects.count()} Bookings\n"
                f" - {Payment.objects.count()} Payments\n"
                f" - {Review.objects.count()} Reviews\n"
                f" - {Notification.objects.count()} Notifications\n"
                f" - {WorkerLocationHistory.objects.count()} Worker Locations"
            )
        )
