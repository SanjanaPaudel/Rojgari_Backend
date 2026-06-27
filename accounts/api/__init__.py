from ninja import NinjaAPI

from accounts.api.auth import router as auth_router
from accounts.api.bookings import router as bookings_router
from accounts.api.categories import router as categories_router
from accounts.api.notifications import router as notifications_router
from accounts.api.payments import router as payments_router
from accounts.api.requests import router as requests_router
from accounts.api.reviews import router as reviews_router
from accounts.api.workers import router as worker_router

api = NinjaAPI(
    title="Rojgari API",
    version="2.0.0",
    description="Modularized REST API for managing customers, workers, requests, bookings, payments, and reviews.",
)

api.add_router("/auth", auth_router)
api.add_router("/categories", categories_router)
api.add_router("/workers", worker_router)
api.add_router("/requests", requests_router)
api.add_router("/bookings", bookings_router)
api.add_router("/payments", payments_router)
api.add_router("/reviews", reviews_router)
api.add_router("/notifications", notifications_router)
