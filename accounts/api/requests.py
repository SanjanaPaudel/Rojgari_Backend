from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.security import django_auth

from accounts.api.schemas import ErrorSchema, ServiceRequestInput, ServiceRequestOut
from services.models import ServiceCategory, ServiceRequest

router = Router()


@router.post("", auth=django_auth, response={201: ServiceRequestOut, 400: ErrorSchema})
def create_service_request(request, data: ServiceRequestInput):
    """
    Post a new service request (Customer only).
    """
    if not hasattr(request.user, "customer_profile"):
        return 400, {"message": "Only customers can create service requests"}

    category = get_object_or_404(ServiceCategory, id=data.category_id)
    req = ServiceRequest.objects.create(
        customer=request.user.customer_profile,
        category=category,
        description=data.description,
        customer_lat=data.customer_lat,
        customer_lng=data.customer_lng,
        address=data.address,
        expires_at=data.expires_at,
    )
    return 201, req


@router.get("", auth=django_auth, response=list[ServiceRequestOut])
def list_service_requests(request):
    """
    List service requests. If Customer, show their requests. If Worker, show pending requests.
    """
    if hasattr(request.user, "customer_profile"):
        return list(
            ServiceRequest.objects.filter(customer=request.user.customer_profile)
        )
    elif hasattr(request.user, "worker_profile"):
        return list(ServiceRequest.objects.filter(status="pending"))
    return []
