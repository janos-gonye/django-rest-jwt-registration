import datetime
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from drjr.managers import TokenManager

User = get_user_model()


class Token(models.Model):
    objects = TokenManager()
    REGISTRATION_TOKEN = 'rt'
    REGISTRATION_DELETE_TOKEN = 'rd'
    PASSWORD_CHANGE_TOKEN = 'pc'
    EMAIL_CHANGE_TOKEN = 'ec'
    TOKEN_TYPES = (
        (REGISTRATION_TOKEN, _('Registration token')),
        (REGISTRATION_DELETE_TOKEN, _('Registration Delete Token')),
        (PASSWORD_CHANGE_TOKEN, _('Password Change Token')),
        (EMAIL_CHANGE_TOKEN, _('Change Email Token')),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    token = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(choices=TOKEN_TYPES, max_length=3, default=REGISTRATION_TOKEN)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, default=None)

    @property
    def lifetime(self):
        from drjr.apps import DjangoRestJwtRegistrationConfig
        app_settings = DjangoRestJwtRegistrationConfig.settings
        return {
            Token.REGISTRATION_TOKEN: app_settings['REGISTRATION_TOKEN_LIFETIME'],
            Token.REGISTRATION_DELETE_TOKEN: app_settings['REGISTRATION_DELETE_TOKEN_LIFETIME'],
            Token.PASSWORD_CHANGE_TOKEN: app_settings['PASSWORD_CHANGE_TOKEN_LIFETIME'],
            Token.EMAIL_CHANGE_TOKEN: app_settings['EMAIL_CHANGE_TOKEN_LIFETIME'],
        }[self.type]

    @property
    def expires_at(self):
        return self.created_at.astimezone(datetime.timezone.utc) + datetime.timedelta(seconds=self.lifetime)
