from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework.serializers import ModelSerializer

from django_rest_jwt_registration.utils import import_elm_from_str


class DjangoRestJwtRegistrationConfig(AppConfig):
    name = 'django_rest_jwt_registration'

    def __init__(self, *args, **kwargs):
        self.app_settings = {}
        super().__init__(*args, **kwargs)

    def ready(self):
        self._check_settings()

    def _check_settings(self):
        self._validate_app_settings_object()
        self._validate_create_user_serializer()
        self._validate_registration_token_lifetime()
        self._validate_registration_delete_token_lifetime()
        self._validate_password_change_token_lifetime()
        self._validate_delete_expired_tokens_interval()

    def _validate_app_settings_object(self):
        try:
            self.app_settings = getattr(settings, 'REST_JWT_REGISTRATION')
        except AttributeError as err:
            raise ImproperlyConfigured("'REST_JWT_REGISTRATION' is not set") from err
        if not isinstance(self.app_settings, dict):
            raise ImproperlyConfigured(
                f"'REST_JWT_REGISTRATION' is expected to be of type {dict} or a subclass of {dict}")

    def _validate_create_user_serializer(self):
        try:
            user_serializer = self.app_settings['CREATE_USER_SERIALIZER']
        except KeyError as err:
            raise ImproperlyConfigured("'REST_JWT_REGISTRATION' is missing key 'CREATE_USER_SERIALIZER'") from err
        if not isinstance(user_serializer, str):
            raise ImproperlyConfigured(f"'CREATE_USER_SERIALIZER' is expected to be of type {str}")

        try:
            user_serializer = import_elm_from_str(user_serializer)
        except Exception as err:
            raise ImproperlyConfigured(
                "'REST_JWT_REGISTRATION.CREATE_USER_SERIALIZER' refers to an object that does not exist") from err

        try:
            if not issubclass(user_serializer, ModelSerializer):
                raise ValueError
        except ValueError as err:
            raise ImproperlyConfigured(
                "'REST_JWT_REGISTRATION.CREATE_USER_SERIALIZER' is "
                f"expected to be a subclass of {ModelSerializer}") from err

    def _validate_token_lifetime(self, name):
        try:
            value = self.app_settings[name]
        except KeyError as err:
            raise ImproperlyConfigured(
                f"'REST_JWT_REGISTRATION' is missing key '{name}'") from err
        if not isinstance(value, int):
            raise ImproperlyConfigured(
                f"'REST_JWT_REGISTRATION.{name}' is not of type {int}")

        if value < 0:
            raise ImproperlyConfigured(f"'{name}' must be greater than 0")

    def _validate_registration_token_lifetime(self):
        self._validate_token_lifetime(name='REGISTRATION_TOKEN_LIFETIME')

    def _validate_registration_delete_token_lifetime(self):
        self._validate_token_lifetime(name='REGISTRATION_DELETE_TOKEN_LIFETIME')

    def _validate_password_change_token_lifetime(self):
        self._validate_token_lifetime(name='PASSWORD_CHANGE_TOKEN_LIFETIME')

    def _validate_delete_expired_tokens_interval(self):
        try:
            value = self.app_settings['DELETE_EXPIRED_TOKENS_INTERVAL']
        except KeyError as err:
            raise ImproperlyConfigured(
                "'REST_JWT_REGISTRATION' is missing key 'DELETE_EXPIRED_TOKENS_INTERVAL'") from err
        if not isinstance(value, int):
            raise ImproperlyConfigured(
                f"'REST_JWT_REGISTRATION.DELETE_EXPIRED_TOKENS_INTERVAL' is not of type {int}")

        if value < 0:
            raise ImproperlyConfigured("'DELETE_EXPIRED_TOKENS_INTERVAL' must be greater than 0")
