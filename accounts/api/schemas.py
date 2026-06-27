from datetime import datetime
from uuid import UUID

from ninja import Schema


class ErrorSchema(Schema):
    message: str


class RegisterInput(Schema):
    username: str
    email: str
    password: str
    full_name: str | None = ""
    phone_number: str | None = None
    role: str  # 'customer' or 'worker'


class LoginInput(Schema):
    username: str
    password: str


class UserOut(Schema):
    id: UUID
    username: str
    email: str
    full_name: str
    phone_number: str | None = None
    role: str | None = None
    profile_photo_url: str | None = None
    is_verified: bool


class CustomerOut(Schema):
    id: UUID
    address: str | None = None
    default_lat: float | None = None
    default_lng: float | None = None


class WorkerOut(Schema):
    id: UUID
    bio: str | None = None
    avg_rating: float
    total_jobs: int
    is_available: bool
    is_approved: bool
    current_lat: float | None = None
    current_lng: float | None = None


class WorkerJoinInput(Schema):
    bio: str | None = ""
    bank_account: str | None = ""
    wallet_number: str | None = ""


class WorkerDocumentInput(Schema):
    document_type: str
    file_url: str


class WorkerDocumentOut(Schema):
    id: UUID
    document_type: str
    file_url: str
    verification_status: str
    rejection_reason: str | None = None
    submitted_at: datetime


class ServiceCategoryOut(Schema):
    id: UUID
    name: str
    description: str | None = None
    icon_url: str | None = None
    is_active: bool


class WorkerServiceInput(Schema):
    category_id: UUID
    years_experience: int
    skill_level: str
    hourly_rate: float


class WorkerServiceOut(Schema):
    id: UUID
    category: ServiceCategoryOut
    years_experience: int
    skill_level: str | None = None
    hourly_rate: float


class ServiceRequestInput(Schema):
    category_id: UUID
    description: str
    customer_lat: float
    customer_lng: float
    address: str
    expires_at: datetime | None = None


class ServiceRequestOut(Schema):
    id: UUID
    category: ServiceCategoryOut
    description: str
    status: str
    customer_lat: float
    customer_lng: float
    address: str
    requested_at: datetime
    expires_at: datetime | None = None


class BookingOut(Schema):
    id: UUID
    request: ServiceRequestOut
    worker: WorkerOut
    status: str
    agreed_price: float
    accepted_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None


class BookingStatusUpdateInput(Schema):
    status: str  # 'started', 'completed', 'cancelled'
    cancellation_reason: str | None = None


class PaymentInput(Schema):
    booking_id: UUID
    amount: float
    method: str
    transaction_ref: str


class PaymentOut(Schema):
    id: UUID
    booking_id: UUID
    amount: float
    method: str
    status: str
    transaction_ref: str
    paid_at: datetime | None = None


class ReviewInput(Schema):
    booking_id: UUID
    rating: int
    comment: str | None = None


class ReviewOut(Schema):
    id: UUID
    booking_id: UUID
    reviewer_id: UUID
    reviewee_id: UUID
    rating: int
    comment: str | None = None
    created_at: datetime


class NotificationOut(Schema):
    id: UUID
    title: str
    body: str
    type: str
    is_read: bool
    reference_id: UUID | None = None
    reference_type: str | None = None
    created_at: datetime
