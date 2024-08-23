from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models import Q


class NotificationManager(models.Manager):
    def get_notifications_for_profile(self, profile):
        return self.filter(receiver=profile)

    def send_notification(self, sender, receiver, category, object_id):
        notification = self.create(sender=sender, receiver=receiver, category=category, object_id=object_id)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifs_{receiver.id}',
            {
                'type': 'send_notification',
                'notification': {
                    'id': str(notification.id),
                    'sender': notification.sender.alias,
                    'receiver': notification.receiver.alias,
                    'category': notification.category,
                    'object_id': notification.object_id,
                    'created_at': notification.created_at.isoformat(),
                }
            }
        )

    def mark_notification_as_read(self, notif_id):
        notification = self.get(id=notif_id)
        notification.mark_as_read()

    def mark_all_read_for_profile(self, profile):
        notifications = self.filter(receiver=profile, read=False)
        notifications.update(read=True)