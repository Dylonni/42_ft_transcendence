import logging
from rest_framework import serializers
from .models import Profile, ProfileBlock

logger = logging.getLogger('django')

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class ProfileBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileBlock
        fields = '__all__'