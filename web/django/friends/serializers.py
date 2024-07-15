from rest_framework import serializers
from profiles.models import Profile
from .models import FriendMessage, FriendRequest, Friendship


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'created_at']

class FriendRequestCreateSerializer(serializers.ModelSerializer):
    sender_id = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all(), source='sender.id')
    receiver_id = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all(), source='receiver.id')
    
    class Meta:
        model = FriendRequest
        fields = ['sender_id', 'receiver_id']
    
    def create(self, validated_data):
        sender = validated_data['sender']
        receiver = validated_data['receiver']
        return FriendRequest.objects.create_request(sender=sender, receiver=receiver)


class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ['id', 'profile1', 'profile2', 'created_at']


class FriendMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendMessage
        fields = ['id', 'sender', 'receiver', 'message', 'created_at']