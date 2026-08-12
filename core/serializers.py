from rest_framework import serializers
from .models import DocumentationItem, Notification

class DocumentationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentationItem
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
