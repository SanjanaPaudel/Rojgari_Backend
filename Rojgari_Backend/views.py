from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse


def status_view(request):
    status = {
        "database": "unknown",
        "cache": "unknown",
    }

    # Test Database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        status["database"] = "healthy"
    except Exception as e:
        status["database"] = f"unhealthy: {str(e)}"

    # Test Cache (Valkey)
    try:
        cache.set("health_check_key", "ok", timeout=10)
        cache_val = cache.get("health_check_key")
        if cache_val == "ok":
            status["cache"] = "healthy"
        else:
            status["cache"] = f"unhealthy: unexpected value {cache_val}"
    except Exception as e:
        status["cache"] = f"unhealthy: {str(e)}"

    return JsonResponse(status)
