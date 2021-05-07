from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework import serializers

from drjr.utils import import_elm_from_str


class AppSettingsSerializer(serializers.Serializer):
    CREATE_USER_SERIALIZER = serializers.CharField(required=False)
    REGISTRATION_TOKEN_LIFETIME = serializers.IntegerField(required=False, min_value=1, default=3600)
    REGISTRATION_DELETE_TOKEN_LIFETIME = serializers.IntegerField(required=False, min_value=1, default=3600)
    PASSWORD_CHANGE_TOKEN_LIFETIME = serializers.IntegerField(required=False, min_value=1, default=3600)
    EMAIL_CHANGE_TOKEN_LIFETIME = serializers.IntegerField(required=False, min_value=1, default=3600)
    DELETE_EXPIRED_TOKENS_INTERVAL = serializers.IntegerField(required=False, min_value=1, default=3600)

    def validate_CREATE_USER_SERIALIZER(self, value):
        try:
            user_serializer = import_elm_from_str(value)
            if not issubclass(user_serializer, serializers.ModelSerializer):
                raise serializers.ValidationError(
                    "'REST_JWT_REGISTRATION.CREATE_USER_SERIALIZER' is "
                    f"expected to be a subclass of {serializers.ModelSerializer}")
        except Exception as err:
            raise serializers.ValidationError(
                "'REST_JWT_REGISTRATION.CREATE_USER_SERIALIZER' refers "
                "to an object that does not exist") from err
        return value


class DjangoRestJwtRegistrationConfig(AppConfig):
    name = 'drjr'

    def ready(self):
        try:
            app_settings = getattr(settings, 'REST_JWT_REGISTRATION')
            if not isinstance(app_settings, dict):
                raise ImproperlyConfigured(
                    f"'REST_JWT_REGISTRATION' is expected to be of type {dict} "
                    f"or a subclass of {dict}")
            serializer = AppSettingsSerializer(data=app_settings)
            serializer.is_valid(raise_exception=True)
        except AttributeError as err:
            raise ImproperlyConfigured("'REST_JWT_REGISTRATION' is not set") from err
        except serializers.ValidationError as err:
            raise ImproperlyConfigured(str(err)) from err
