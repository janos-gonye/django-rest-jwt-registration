from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db.models.fields import EmailField
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers


User = get_user_model()


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        read_only_fields = ('id', 'last_login', 'date_joined')


class ChangeEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if self.instance.email == value:
            raise serializers.ValidationError(_('Current email provided.'))
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_('user with given email address exist.'))
        return value


class ResetPasswordSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', )


class ChangePasswordSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_current_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError(
                _('Current password wrong'))
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def save(self, **kwargs):
        password = self.validated_data['new_password']
        self.instance.set_password(password)
        self.instance.save()
        return self.instance

    class Meta:
        model = get_user_model()
        fields = ('current_password', 'new_password')
