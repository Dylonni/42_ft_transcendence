from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import CustomUser

UserModel = get_user_model()


class CustomUserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email',)


class CustomUserPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('password',)


class CustomUserCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('code',)


class UserLoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username_or_email = attrs.get('username_or_email')
        password = attrs.get('password')
        
        if not username_or_email or not password:
            raise serializers.ValidationError(_('Must include username/email and password.'))
        
        try:
            user = UserModel.objects.get(username=username_or_email)
        except UserModel.DoesNotExist:
            try:
                user = UserModel.objects.get(email=username_or_email)
            except UserModel.DoesNotExist:
                raise serializers.ValidationError(_('Unable to log in with provided credentials.'))
        
        if not user.is_verified:
            raise serializers.ValidationError(_('Check your email and activate your account first.'))
        if not user.check_password(password):
            raise serializers.ValidationError(_('Unable to log in with provided credentials.'))
        if not user.is_active:
            raise serializers.ValidationError(_('Account is inactive.'))
        attrs['user'] = user
        return attrs


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')
        
        if not username or not email or not password:
            raise serializers.ValidationError(_('Must include username/email and password.'))
        
        user = UserModel.objects.filter(username=username, email=email).first()
        if not user:
            return attrs
        if user.has_verif_expired() or user.is_verified or user.is_active:
            raise serializers.ValidationError(_('Unable to register with provided credentials.'))
        user.delete()
        return attrs
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        self.user = UserModel.objects.filter(email=value).first()
        return value
    
    def get_user(self):
        return getattr(self, 'user', None)


class PasswordConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        return value


class UserUpdateEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    
    class Meta:
        model = UserModel
        fields = ('email',)
    
    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance