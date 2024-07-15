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
    
    def search_by_alias(self, alias):
        return self.filter(alias__istartswith=alias)
    
    def block_profile(self, profile, profile_to_block):
        profile.blocked_profiles.add(profile_to_block)
    
    def unblock_profile(self, profile, profile_to_unblock):
        profile.blocked_profiles.remove(profile_to_unblock)
    
    def is_blocked(self, profile):
        return self.blocked_profiles.filter(pk=profile.pk).exists()
    
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