from rest_framework.permissions import BasePermission


class IsWorker(BasePermission):
    """
    Allow access only to workers.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "worker"
