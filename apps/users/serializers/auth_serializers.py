import re

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field, OpenApiTypes
from rest_framework import serializers

from apps.users.serializers.general_serializers import UserSerializer

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        help_text=_('Password must be at least 8 characters long'),
    )
    password_confirmation = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        help_text=_('Password must be at least 8 characters long'),
    )

    def validate_password_confirmation(self, value):
        password = self.get_initial().get('password')
        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#^()\-_=+{};:,<.>])[A-Za-z\d@$!%*?&#^()\-_=+{};:,<.>]{8,16}$'
        if not re.match(password_regex, password):
            raise serializers.ValidationError(
                _('Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character'),
            )
        if password != value:
            raise serializers.ValidationError(
                _('Passwords do not match')
            )
        return value

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password', 'password_confirmation']

    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email_or_username = serializers.CharField(
        required=True, write_only=True,
        help_text=_('Enter your email or username')
    )
    password = serializers.CharField(
        required=True, write_only=True,
        help_text=_('Enter your password')
    )


class LoginResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    expires_in = serializers.SerializerMethodField()
    user = UserSerializer()

    @extend_schema_field(
        OpenApiTypes.STR,
    )
    def get_expires_in(self, obj):
        return obj.get('expires_in')


class PassWordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmationSerializer(serializers.Serializer):
    otp = serializers.CharField()
    password = serializers.CharField(
        max_length=128,
        min_length=8
    )
    password_confirmation = serializers.CharField()

    def validate_password_confirmation(self, value):
        password = self.get_initial().get('password')
        if password != value:
            raise serializers.ValidationError(_('Passwords do not match'))
        return value
