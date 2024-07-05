from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

UserModel = get_user_model()


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
                user = UserModel.objects.get(email=username_or_email)
                user = authenticate(request=self.context.get('request'), username=user.username, password=password)
            except UserModel.DoesNotExist as e:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        self.user = UserModel.objects.filter(email=value).first()
        return value
    
    def get_user(self):
        return getattr(self, 'user', None)


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        # Add any custom password validation if necessary
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