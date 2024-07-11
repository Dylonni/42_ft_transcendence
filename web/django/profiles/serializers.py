from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'alias', 'avatar', 'status', 'blocked_profiles']


class ProfileAliasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['alias']


class ProfileAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['avatar']


class ProfileStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['status']