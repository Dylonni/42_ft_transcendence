from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models import Q


class FriendshipManager(models.Manager):
    def create_friendship(self, profile1, profile2):
        if profile1 == profile2:
            raise ValueError("Cannot be friends with yourself.")
        
        if self.are_friends(profile1, profile2):
            raise ValueError("These profiles are already friends.")
        
        friendship = self.create(profile1=profile1, profile2=profile2)
        return friendship
    
    def create_friendship_from_request(self, friend_request):
        return self.create_friendship(friend_request.sender, friend_request.receiver)
    
    def are_friends(self, profile1, profile2):
        return self.filter(
            Q(profile1=profile1, profile2=profile2) | 
            Q(profile1=profile2, profile2=profile1)
        ).exists()
    
    def remove_friendship(self, profile1, profile2):
        friendship = self.filter(
            Q(profile1=profile1, profile2=profile2) |
            Q(profile1=profile2, profile2=profile1)
        )
        if friendship.exists():
            friendship.delete()
    
    def friendships(self, profile):
        return self.filter(Q(profile1=profile) | Q(profile2=profile))
    
    def search_by_alias(self, alias):
        return self.filter(
            Q(profile1__alias__icontains=alias) | Q(profile2__alias__icontains=alias)
        )
    
    def get_id(self, profile1, profile2):
        friendship = self.filter(
            Q(profile1=profile1, profile2=profile2) | 
            Q(profile1=profile2, profile2=profile1)
        ).first()
        return friendship.id if friendship else None


class FriendRequestManager(models.Manager):
    def create_request(self, sender, receiver):
        if sender == receiver:
            raise ValueError("Cannot send a friend request to yourself.")
        if self.filter(sender=sender, receiver=receiver).exists():
            raise ValueError("Friend request already sent.")
        if self.filter(sender=receiver, receiver=sender).exists():
            raise ValueError("Friend request already received.")
        
        friend_request = self.create(sender=sender, receiver=receiver)
        return friend_request
    
    def remove_request(self, friend_request):
        friend_request.delete()
    
    def remove_request_by_id(self, request_id):
        friend_request = self.get(id=request_id)
        friend_request.delete()
    
    def pending_requests(self, profile):
        return self.filter(receiver=profile)
    
    def sent_requests(self, profile):
        return self.filter(sender=profile)


class FriendMessageManager(models.Manager):
    def send_message(self, sender, receiver, message, friendship_id):
        if sender == receiver:
            raise ValueError("Cannot send a message to yourself.")
        
        friend_message = self.create(sender=sender, receiver=receiver, message=message)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{friendship_id}',
            {
                'type': 'chat_message',
                'message': {
                    'id': str(friend_message.id),
                    'sender': friend_message.sender.alias,
                    'receiver': friend_message.receiver.alias,
                    'message': friend_message.message,
                    'created_at': friend_message.created_at.isoformat(),
                }
            }
        )
        return friend_message
    
    def get_conversation(self, user1, user2):
        return self.filter(
            Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1)
        ).order_by('created_at')