from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework.serializers import ModelSerializer

from django_rest_jwt_registration.helpers import import_elm_from_str


class DjangoRestJwtRegistrationConfig(AppConfig):
    name = 'django_rest_jwt_registration'

    def ready(self):
        self.check_settings()

    def check_settings(self):
        try:
            app_settings = getattr(settings, 'REST_JWT_REGISTRATION')
        except AttributeError as err:
            raise ImproperlyConfigured('REST_JWT_REGISTRATION is not set') from err
        if not isinstance(app_settings, dict):
            raise ImproperlyConfigured(
                f'REST_JWT_REGISTRATION is expected to be of type {dict} or a subclass of {dict}')
        try:
            user_serializer = app_settings['CREATE_USER_SERIALIZER']
        except KeyError as err:
            raise ImproperlyConfigured("REST_JWT_REGISTRATION is missing key 'CREATE_USER_SERIALIZER'") from err
        if not isinstance(user_serializer, str):
            raise ImproperlyConfigured(f'CREATE_USER_SERIALIZER is expected to be of type {str}')

        try:
            user_serializer = import_elm_from_str(user_serializer)
        except Exception as err:
            raise ImproperlyConfigured(
                "REST_JWT_REGISTRATION.CREATE_USER_SERIALIZER refers to an object that does not exist") from err

        try:
            if not issubclass(user_serializer, ModelSerializer):
                raise ValueError
        except ValueError as err:
            raise ImproperlyConfigured(
                "REST_JWT_REGISTRATION.CREATE_USER_SERIALIZER is "
                f"expected to be a subclass of {ModelSerializer}") from err
