from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models import Q


class NotificationManager(models.Manager):
	def get_notifications_for_profile(self, profile_id):
		return self.filter(receiver__id=profile_id)

	def send_notification(self, sender, receiver, category, content):
		notification = self.create(sender, receiver, category, content)
		async_to_sync(self.channel_layer.group_send)(
            f'notifs_{receiver.id}',
            {
                'type': 'send_notification',
                'notification': {
                    'id': str(notification.id),
                    'sender': notification.sender.alias,
                    'receiver': notification.receiver.alias,
					'category': notification.category,
                    'content': notification.content,
                    'created_at': notification.created_at.isoformat(),
                }
            }
        )

	def mark_notification_as_read(self, notif_id):
		notification = self.get(id=notif_id)
		notification.mark_as_read()