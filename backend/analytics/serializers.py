from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Dataset

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']


class DatasetSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Dataset
        fields = ['id', 'file', 'uploaded_at', 'owner']
        read_only_fields = ['id', 'uploaded_at', 'owner']

    def get_owner(self, obj):
        if not obj.user:
            return None
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
        }
