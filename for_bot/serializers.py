from rest_framework import serializers
from .models import TelegramUser, TelegramMessageLog
from app.models import Group


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "group_id", "name"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramMessageLog
        fields = "__all__"
