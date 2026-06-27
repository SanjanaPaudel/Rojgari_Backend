from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.security import django_auth

from accounts.api.schemas import (
    ErrorSchema,
    WorkerDocumentInput,
    WorkerDocumentOut,
    WorkerJoinInput,
    WorkerOut,
    WorkerServiceInput,
    WorkerServiceOut,
)
from accounts.models import Worker, WorkerDocument
from services.models import ServiceCategory, WorkerService

router = Router()


@router.post("/join", auth=django_auth, response={200: WorkerOut, 400: ErrorSchema})
def join_as_worker(request, data: WorkerJoinInput):
    """
    Enable worker profile for an existing account.
    """
    user = request.user
    if hasattr(user, "worker_profile"):
        return 400, {"message": "Worker profile already exists"}

    user.role = "worker"
    user.save()

    worker = Worker.objects.create(
        user=user,
        bio=data.bio,
        bank_account=data.bank_account,
        wallet_number=data.wallet_number,
    )
    return 200, worker


@router.post(
    "/document", auth=django_auth, response={201: WorkerDocumentOut, 400: ErrorSchema}
)
def upload_document(request, data: WorkerDocumentInput):
    """
    Submit verification documents for a worker profile.
    """
    if not hasattr(request.user, "worker_profile"):
        return 400, {"message": "Authenticated user is not a worker"}

    doc = WorkerDocument.objects.create(
        worker=request.user.worker_profile,
        document_type=data.document_type,
        file_url=data.file_url,
    )
    return 201, doc


@router.get("/services", auth=django_auth, response=list[WorkerServiceOut])
def list_my_services(request):
    """
    Retrieve services offered by current authenticated worker.
    """
    if not hasattr(request.user, "worker_profile"):
        return 400, {"message": "Authenticated user is not a worker"}
    return list(request.user.worker_profile.offered_services.all())


@router.post(
    "/services", auth=django_auth, response={201: WorkerServiceOut, 400: ErrorSchema}
)
def add_worker_service(request, data: WorkerServiceInput):
    """
    Add a service offering for a worker.
    """
    if not hasattr(request.user, "worker_profile"):
        return 400, {"message": "Authenticated user is not a worker"}

    category = get_object_or_404(ServiceCategory, id=data.category_id)
    ws = WorkerService.objects.create(
        worker=request.user.worker_profile,
        category=category,
        years_experience=data.years_experience,
        skill_level=data.skill_level,
        hourly_rate=data.hourly_rate,
    )
    return 201, ws
