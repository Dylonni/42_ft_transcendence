from rest_framework import serializers
from profiles.models import Profile
from .models import FriendMessage, FriendRequest, Friendship


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = '__all__'


class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = '__all__'


class FriendMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendMessage
        fields = '__all__'