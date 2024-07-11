from django.db import models


class ProfileManager(models.Manager):
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
        return self.filter(alias__icontains=alias)
    
    def block_profile(self, profile, profile_to_block):
        profile.blocked_profiles.add(profile_to_block)
    
    def unblock_profile(self, profile, profile_to_unblock):
        profile.blocked_profiles.remove(profile_to_unblock)
    
    def is_blocked(self, profile):
        return self.blocked_profiles.filter(pk=profile.pk).exists()