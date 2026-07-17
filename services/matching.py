import math
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from accounts.models import WorkerProfile

def _distance_km(lat1, lon1, lat2, lon2):
    """
    Haversine formula - straight-line dsitance between two coordinates, in km.
    """

    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])

    r = 6371 # Earth's radius in KM

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return r * c

def _distance_score(distance_km):
    if distance_km < 2:
        return 4
    elif distance_km < 5:
        return 3
    elif distance_km < 10:
        return 2
    else: 
        return 1

def _rating_score(average_rating):
    return (Decimal(average_rating) / Decimal(5)) * Decimal(3)

def _completed_jobs_score(completed_jobs):
    if completed_jobs == 0:
        return 0
    elif completed_jobs <= 5:
        return 1
    elif completed_jobs <= 15:
        return 2
    else:
        return 3

def get_eligible_workers(booking):
    """
    Return WorkerProfiles eligible to be offered this booking, 
    filtered by Category, online status, and location freshness.
    """

    stale_cutoff = timezone.now() - timedelta(minutes=3)

    return WorkerProfile.objects.filter(
        skills=booking.category,
        is_online=True,
        is_verified=True,
        last_location_update__gte=stale_cutoff,
        current_latitude__isnull=False,
        current_longitude__isnull=False,
    )

def score_worker(booking, worker):
    distance = _distance_km(
        booking.latitude,
        booking.longitude,
        worker.current_latitude,
        worker.current_longitude,
    )

    total = (
        _distance_score(distance)
        + _rating_score(worker.average_rating)
        + _completed_jobs_score(worker.completed_jobs)
    )

    return round(Decimal(total), 2)

def rank_candidates(booking, exclude_worker_ids=None):
    """
    Returns eligible workers for this booking, scored and sorted
    best-first, excluding any worker IDs already offered.
    """

    exclude_worker_ids = exclude_worker_ids or []

    candidates = get_eligible_workers(booking).exclude(id__in=exclude_worker_ids)

    scored = [(worker, score_worker(booking, worker)) for worker in candidates]

    scored.sort(key=lambda pair: pair[1], reverse=True)

    return scored
