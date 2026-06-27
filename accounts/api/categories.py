from django.core.cache import cache
from ninja import Router

from accounts.api.schemas import ServiceCategoryOut
from services.models import ServiceCategory

router = Router()


@router.get("", response=list[ServiceCategoryOut])
def list_categories(request):
    """
    Retrieve list of active service categories.
    Checks and populates Valkey cache to reduce database load.
    """
    cache_key = "active_service_categories"
    cached_data = cache.get(cache_key)

    if cached_data is not None:
        return cached_data

    categories = list(ServiceCategory.objects.filter(is_active=True))
    # Cache active categories for 1 hour (3600 seconds)
    cache.set(cache_key, categories, timeout=3600)

    return categories
