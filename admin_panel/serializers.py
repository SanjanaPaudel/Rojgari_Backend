from rest_framework import serializers


class AdminLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()