import random
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _


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
            profile.set_status(status)
        except self.model.DoesNotExist:
            raise ValueError(_('No profile found to set status.'))
    
    def set_user_lang(self, user, lang):
        profile = self.filter(user=user).first()
        if profile:
            profile.default_lang = lang
            profile.save()
    
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
        unique_elo_scores = (
            self.annotate(
                total_games=Count('player1_rounds', distinct=True) + Count('player2_rounds', distinct=True)
            )
            .filter(total_games__gt=0)
            .order_by('-elo')
            .values_list('elo', flat=True)
            .distinct()[:100]
        )
        profiles = self.annotate(
            total_games=Count('player1_rounds', distinct=True) + Count('player2_rounds', distinct=True)
        ).filter(total_games__gt=0, elo__in=unique_elo_scores).order_by('-elo')
        return profiles
    
    def get_available_friends(self, profile):
        friends_as_profile1 = profile.friendships_as_profile1.filter(
            removed_by__isnull=True,
            profile2__status=profile.StatusChoices.ONLINE,
        ).values_list('profile2', flat=True)
        friends_as_profile2 = profile.friendships_as_profile2.filter(
            removed_by__isnull=True,
            profile1__status=profile.StatusChoices.ONLINE,
        ).values_list('profile1', flat=True)
        friend_ids = friends_as_profile1.union(friends_as_profile2)
        return self.filter(id__in=friend_ids)


class ProfileBlockManager(models.Manager):
    def get_blocked_profiles(self, blocker):
        return self.filter(blocker=blocker)
    
    def create_block(self, blocker, blocked):
        if self.filter(blocker=blocker, blocked=blocked).exists():
            raise ValueError(_('Profile is already blocked.'))
        return self.create(blocker=blocker, blocked=blocked)