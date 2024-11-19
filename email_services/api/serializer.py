from rest_framework import serializers
from email_services.models import EmailVerification

class EmailSerializer(serializers.Serializer):
    recipient_email = serializers.EmailField()