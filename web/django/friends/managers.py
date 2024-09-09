from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models import Max, OuterRef, Q, Subquery
from django.utils.translation import gettext_lazy as _
from notifs.consumers import NotifConsumer


class FriendshipManager(models.Manager):
    def get_friendship(self, profile1, profile2):
        return self.filter(
            Q(profile1=profile1, profile2=profile2) | 
            Q(profile1=profile2, profile2=profile1)
        ).first()
    
    def get_friendships(self, profile):
        latest_message_created_at_subquery = self.filter(
            id=OuterRef('pk')
        ).annotate(
            latest_created_at=Max('messages__created_at')
        ).values('latest_created_at')[:1]
        friendships = self.filter(
            Q(profile1=profile) | Q(profile2=profile),
            removed_by__isnull=True
        ).annotate(
            last_message_created_at=Subquery(latest_message_created_at_subquery)
        ).order_by('-last_message_created_at')
        return friendships
    
    def get_friendship_id(self, profile1, profile2):
        friendship = self.get_friendship(profile1, profile2)
        return friendship.id if friendship else None
    
    def get_other(self, friendship_id, profile):
        friendship = self.filter(id=friendship_id).first()
        if not friendship:
            raise ValueError(_('Friendship not found.'))
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
            raise ValueError(_('Cannot be friends with yourself.'))
        
        existing_friendship = self.get_friendship(requesting, requested)
        if existing_friendship:
            if existing_friendship.removed_by == requesting:
                existing_friendship.removed_by = None
                existing_friendship.save()
                return existing_friendship
            else:
                raise ValueError(_('These profiles are already friends.'))
        
        friendship = self.create(profile1=requesting, profile2=requested)
        # TODO: update sender friend list
        return friendship
    
    def create_friendship_from_request(self, friend_request):
        friendship = self.create_friendship(friend_request.sender, friend_request.receiver)
        consumer = NotifConsumer()
        async_to_sync(consumer.remove_notification)(
            category='Friend Request',
            object_id=friend_request.id,
        )
        friend_request.delete()
        return friendship
    
    def remove_friendship(self, friendship, removed_by):
        if removed_by != friendship.profile1 and removed_by != friendship.profile2:
            raise ValueError(_('Profile not part of this friendship.'))
        if friendship.removed_by:
            if removed_by == friendship.removed_by:
                raise ValueError(_('Friendship already removed.'))
            else:
                friendship.delete()
        else:
            friendship.removed_by = removed_by
            friendship.save()
    
    def search_by_alias(self, alias):
        return self.filter(
            Q(profile1__alias__istartswith=alias) |
            Q(profile2__alias__istartswith=alias)
        )
    
    def remove_all_for_profile(self, profile):
        friendships = self.filter(Q(profile1=profile) | Q(profile2=profile))
        friendships.delete()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('friends', {'type': 'update_friend_list'})


class FriendRequestManager(models.Manager):
    def get_pending_requests(self, profile):
        return self.filter(receiver=profile)
    
    def get_sent_requests(self, profile):
        return self.filter(sender=profile)
    
    def create_request(self, sender, receiver):
        if sender == receiver:
            raise ValueError(_('Cannot send a friend request to yourself.'))
        if self.filter(sender=sender, receiver=receiver).exists():
            raise ValueError(_('Friend request already sent.'))
        if self.filter(sender=receiver, receiver=sender).exists():
            raise ValueError(_('Friend request already received.'))
        
        friend_request = self.create(sender=sender, receiver=receiver)
        consumer = NotifConsumer()
        async_to_sync(consumer.notify_profile)(
            sender=friend_request.sender,
            receiver=friend_request.receiver,
            category='Friend Request',
            object_id=friend_request.id,
        )
        return friend_request
    
    def decline_request(self, friend_request):
        consumer = NotifConsumer()
        async_to_sync(consumer.remove_notification)(
            category='Friend Request',
            object_id=friend_request.id,
        )
        friend_request.delete()


class FriendMessageManager(models.Manager):
    def get_messages(self, friendship_id):
        return self.filter(friendship__id=friendship_id)
    
    def get_conversation(self, profile1, profile2):
        return self.filter(
            Q(sender=profile1, receiver=profile2) | Q(sender=profile2, receiver=profile1)
        )
    
    def get_conversation_by_friendship_id(self, friendship_id):
        return self.filter(friendship__id=friendship_id)
    
    def send_message(self, friendship, sender, content):
        receiver = friendship.get_other(sender)
        friend_message = self.create(friendship=friendship, sender=sender, receiver=receiver, content=content)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'friends_{friend_message.friendship.id}',
            {
                'type': 'broadcast',
                'message_id': str(friend_message.id),
            }
        )
        async_to_sync(channel_layer.group_send)('friends', {'type': 'update_friend_list'})
        return friend_message
    
    def mark_messages_as_read(self, sender, receiver):
        return self.filter(sender=sender, receiver=receiver, read=False).update(read=True)
    
    def remove_message(self, message_id):
        try:
            message = self.get(id=message_id)
            message.delete()
        except self.model.DoesNotExist:
            raise ValueError(_('Friend message not found.'))