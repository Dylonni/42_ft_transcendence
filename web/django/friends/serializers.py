from rest_framework import serializers
from .models import FriendMessage, FriendRequest, Friendship


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'created_at']


class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ['id', 'profile1', 'profile2', 'created_at']


class FriendMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendMessage
        fields = ['id', 'sender', 'receiver', 'message', 'created_at']