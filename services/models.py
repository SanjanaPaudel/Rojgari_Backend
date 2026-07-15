# Create your models here.
from django.db import models
from accounts.models import CustomerProfile

#Scheduled for later - Saved Address field from Profile
# class Address(models.Model):
#     customer = models.ForeignKey(
#         CustomerProfile,
#         on_delete = models.CASCADE,
#         related_name = "addresses",
#     )

#     label = models.CharField(max_length = 100)

#     address_text = models.TextFiled()

#     is_default = models.BooleanField(default = False)

#     def __str__(self):
#         return f"{self.label} ({self.customer.user.full_name})"