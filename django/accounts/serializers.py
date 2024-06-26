from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

CustomUser = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username_or_email = attrs.get('username_or_email')
        password = attrs.get('password')
        
        if not username_or_email or not password:
            msg = _('Must include "username/email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')
        
        user = authenticate(request=self.context.get('request'), username=username_or_email, password=password)
        if not user:
            try:
                user = CustomUser.objects.get(email=username_or_email)
                user = authenticate(request=self.context.get('request'), username=user.username, password=password)
            except CustomUser.DoesNotExist as e:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs

class UserUpdateEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    
    class Meta:
        model = CustomUser
        fields = ('email',)
    
    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance