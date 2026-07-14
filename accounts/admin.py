from django.contrib import admin
from .models import Skill

admin.site.register(Skill)

from .models import CustomerProfile, Skill, User, WorkerProfile


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active")
    search_fields = ("name",)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone_number", "role")


admin.site.register(CustomerProfile)
admin.site.register(WorkerProfile)
