from PIL import Image as PILImage
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers
from .models import Profile, ProfileBlock


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
    
    def validate_alias(self, value):
        if Profile.objects.filter(alias=value).exists():
            raise ValidationError("Alias is already taken.")
        return value
    
    def validate_avatar(self, value):
        max_size_kb = 500
        max_width = 1024
        max_height = 1024
        if value.size > max_size_kb * 1024:
            raise ValidationError(f"Image size should not exceed {max_size_kb} KB.")
        img = PILImage.open(value)
        if img.width > max_width or img.height > max_height:
            raise ValidationError(f"Image dimensions should not exceed {max_width}x{max_height} pixels.")
        return value
    
    def update(self, instance, validated_data):
        avatar = validated_data.get('avatar', None)
        if avatar:
            ext = avatar.name.split('.')[-1]
            avatar.name = f'{instance.id}.{ext}'
            instance.avatar.save(avatar.name, avatar)
            instance.avatar_url = instance.avatar.url
        return super().update(instance, validated_data)


class ProfileBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileBlock
        fields = '__all__'