import random
from django.db import models


class ProfileManager(models.Manager):
    def create_from_user(self, user, avatar_url=None):
        profile = self.create(
            user=user,
            alias=self._generate_unique_alias(),
            avatar_url=avatar_url if avatar_url else self._get_random_default_avatar(),
        )
        return profile
    
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
            raise ValueError('No profile found to set status.')
    
    def search_by_alias(self, alias):
        return self.filter(alias__istartswith=alias)
    
    def _generate_unique_alias(self):
        while True:
            number = random.randint(100000, 999999)
            alias = f'Player_{number}'
            if not self.filter(alias=alias).exists():
                return alias
    
    def _get_random_default_avatar(self):
        number = random.randint(1, 4)
        avatar = f'/media/defaults/avatar{number}.webp'
        return avatar
    
    def get_rank(self, profile):
        higher_elo_count = self.filter(elo__gt=profile.elo).count()
        rank = higher_elo_count + 1
        return rank
    
    def get_ranked_profiles(self):
        return self.order_by('-elo')


class ProfileBlockManager(models.Manager):
    def get_blocked_profiles(self, blocker):
        return self.filter(blocker=blocker)
    
    def is_blocked(self, blocker, blocked):
        return self.filter(blocker=blocker, blocked=blocked).exists()
    
    def create_block(self, blocker, blocked):
        if self.is_blocked(blocker, blocked):
            raise ValueError('Profile is already blocked.')
        return self.create(blocker=blocker, blocked=blocked)