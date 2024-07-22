import logging
import random
from django.db import models

logger = logging.getLogger('django')


class ProfileManager(models.Manager):
    def create_from_user(self, user):
        profile = self.create(
            user=user,
            alias=self._generate_unique_alias(),
            avatar=self._get_random_default_avatar(),
        )
        logger.info(f'Profile created for user {user.username}. Profile ID: {profile.id}')
    
    def get_by_user(self, user):
        try:
            return self.get(user=user)
        except self.model.DoesNotExist:
            return None
    
    def get_by_alias(self, alias):
        try:
            return self.get(alias=alias)
        except self.model.DoesNotExist:
            return None
    
    def set_user_status(self, user, status):
        try:
            profile = self.get(user=user)
            profile.status = status
            profile.save()
        except self.model.DoesNotExist:
            logger.info(f'No profile found to set status')
    
    def search_by_alias(self, alias):
        return self.filter(alias__istartswith=alias)
    
    def _generate_unique_alias(self):
        while True:
            number = random.randint(100000, 999999)
            alias = f'Player_{number}'
            if not self.filter(alias=alias).exists():
                return alias
    
    def _get_random_default_avatar(self):
        number = random.randint(1, 6)
        avatar = f'defaults/avatar{number}.webp'
        return avatar


class ProfileBlockManager(models.Manager):
    def get_blocked_profiles(self, blocker):
        return self.filter(blocker=blocker)
    
    def is_blocked(self, blocker, blocked):
        return self.filter(blocker=blocker, blocked=blocked).exists()
    
    def create_block(self, blocker, blocked):
        if self.is_blocked(blocker, blocked):
            raise ValueError('Profile is already blocked.')
        return self.create(blocker=blocker, blocked=blocked)