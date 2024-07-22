import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models import Q

logger = logging.getLogger('django')


class NotificationManager(models.Manager):
	def send_notification(self):
		notification = self.create(sender, receiver, content)