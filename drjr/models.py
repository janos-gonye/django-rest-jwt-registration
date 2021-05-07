import datetime
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from drjr.managers import TokenManager


REGISTRATION_TOKEN_LIFETIME = settings.DJANGO_REST_JWT_REGISTRATION['REGISTRATION_TOKEN_LIFETIME']
REGISTRATION_DELETE_TOKEN_LIFETIME = settings.DJANGO_REST_JWT_REGISTRATION['REGISTRATION_DELETE_TOKEN_LIFETIME']
PASSWORD_CHANGE_TOKEN_LIFETIME = settings.DJANGO_REST_JWT_REGISTRATION['PASSWORD_CHANGE_TOKEN_LIFETIME']
EMAIL_CHANGE_TOKEN_LIFETIME = settings.DJANGO_REST_JWT_REGISTRATION['EMAIL_CHANGE_TOKEN_LIFETIME']
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
        return {
            Token.REGISTRATION_TOKEN: REGISTRATION_TOKEN_LIFETIME,
            Token.REGISTRATION_DELETE_TOKEN: REGISTRATION_DELETE_TOKEN_LIFETIME,
            Token.PASSWORD_CHANGE_TOKEN: PASSWORD_CHANGE_TOKEN_LIFETIME,
            Token.EMAIL_CHANGE_TOKEN: EMAIL_CHANGE_TOKEN_LIFETIME,
        }[self.type]

    @property
    def expires_at(self):
        return self.created_at.astimezone(datetime.timezone.utc) + datetime.timedelta(seconds=self.lifetime)
