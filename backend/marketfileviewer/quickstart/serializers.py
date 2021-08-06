from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class FileProcessSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True)
    update_count = serializers.IntegerField(write_only=True)
    pt = serializers.CharField(read_only=True)  # publish time
    mc = serializers.ListField(read_only=True)  # market updates
