from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models import Q
from notifs.consumers import NotifConsumer


class FriendshipManager(models.Manager):
    def get_friendship(self, profile1, profile2):
        return self.filter(
            Q(profile1=profile1, profile2=profile2) | 
            Q(profile1=profile2, profile2=profile1)
        ).first()
    
    def get_friendships(self, profile):
        return self.filter(Q(profile1=profile) | Q(profile2=profile))
    
    def get_friendship_id(self, profile1, profile2):
        friendship = self.get_friendship(profile1, profile2)
        return friendship.id if friendship else None
    
    def get_other(self, friendship_id, profile):
        friendship = self.filter(id=friendship_id).first()
        if not friendship:
            raise ValueError(f'Friendship {friendship_id} not found.')
        if friendship.profile1 == profile:
            return friendship.profile2
        return friendship.profile1
    
    def get_friendships_ids(self, profile):
        qs1 = self.filter(profile1=profile).exclude(removed_by=profile).values_list('profile2', flat=True)
        qs2 = self.filter(profile2=profile).exclude(removed_by=profile).values_list('profile1', flat=True)
        friend_ids = set(qs1) | set(qs2)
        return friend_ids
    
    def are_friends(self, profile1, profile2):
        return self.get_friendship(profile1, profile2) is not None
    
    def create_friendship(self, requesting, requested):
        if requesting == requested:
            raise ValueError('Cannot be friends with yourself.')
        
        existing_friendship = self.get_friendship(requesting, requested)
        if existing_friendship:
            if existing_friendship.removed_by == requesting:
                existing_friendship.removed_by = None
                existing_friendship.save()
                return existing_friendship
            else:
                raise ValueError('These profiles are already friends.')
        
        friendship = self.create(profile1=requesting, profile2=requested)
        return friendship
    
    def create_friendship_from_request(self, friend_request):
        return self.create_friendship(friend_request.sender, friend_request.receiver)
    
    def remove_friendship(self, removed_by, to_remove):
        friendship = self.get_friendship(removed_by, to_remove)
        if friendship:
            friendship.removed_by = removed_by
            friendship.save()
            return True
        return False
    
    def search_by_alias(self, alias):
        return self.filter(
            Q(profile1__alias__istartswith=alias) |
            Q(profile2__alias__istartswith=alias)
        )


class FriendRequestManager(models.Manager):
    def get_pending_requests(self, profile):
        return self.filter(receiver=profile)
    
    def get_sent_requests(self, profile):
        return self.filter(sender=profile)
    
    def create_request(self, sender, receiver):
        if sender == receiver:
            raise ValueError('Cannot send a friend request to yourself.')
        if self.filter(sender=sender, receiver=receiver).exists():
            raise ValueError('Friend request already sent.')
        if self.filter(sender=receiver, receiver=sender).exists():
            raise ValueError('Friend request already received.')
        
        friend_request = self.create(sender=sender, receiver=receiver)
        self.send_friend_request_notif(friend_request)
        return friend_request
    
    def remove_request(self, friend_request):
        friend_request.delete()
    
    def send_friend_request_notif(self, friend_request):
        consumer = NotifConsumer()
        async_to_sync(consumer.notify_profile)(
            sender=friend_request.sender,
            receiver=friend_request.receiver,
            category='Friend Request',
            content=f'{friend_request.sender} would like to be your friend.',
        )


class FriendMessageManager(models.Manager):
    def get_messages(self, friendship_id):
        return self.filter(friendship__id=friendship_id)
    
    def get_conversation(self, profile1, profile2):
        return self.filter(
            Q(sender=profile1, receiver=profile2) | Q(sender=profile2, receiver=profile1)
        )
    
    def get_conversation_by_friendship_id(self, friendship_id):
        return self.filter(friendship__id=friendship_id)
    
    def send_message(self, sender, receiver, content, friendship):
        friend_message = self.create(friendship=friendship, sender=sender, receiver=receiver, content=content)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{friend_message.friendship.id}',
            {
                'type': 'chat_message',
                'message': {
                    'id': str(friend_message.id),
                    'sender': friend_message.sender.alias,
                    'receiver': friend_message.receiver.alias,
                    'content': friend_message.content,
                    'created_at': friend_message.created_at.isoformat(),
                }
            }
        )
        return friend_message
    
    def mark_messages_as_read(self, sender, receiver):
        return self.filter(sender=sender, receiver=receiver, read=False).update(read=True)
    
    def remove_message(self, message_id):
        try:
            message = self.get(id=message_id)
            message.delete()
        except self.model.DoesNotExist:
            raise ValueError(f'Friend message {message_id} not found.')