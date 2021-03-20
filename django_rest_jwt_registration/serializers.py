from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers


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
