from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Skill
from accounts.permissions import IsCustomer
from accounts.serializers import SkillSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsCustomer])
def get_categories(request):
    categories = Skill.objects.filter(is_active=True).order_by("display_order")

    serializer = SkillSerializer(categories, many=True)

    return Response({"categories": serializer.data})
