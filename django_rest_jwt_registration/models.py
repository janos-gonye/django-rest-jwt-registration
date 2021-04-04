import datetime
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


REGISTRATION_TOKEN_LIFETIME = settings.REST_JWT_REGISTRATION['REGISTRATION_TOKEN_LIFETIME']
REGISTRATION_DELETE_TOKEN_LIFETIME = settings.REST_JWT_REGISTRATION['REGISTRATION_DELETE_TOKEN_LIFETIME']
PASSWORD_CHANGE_TOKEN_LIFETIME = settings.REST_JWT_REGISTRATION['PASSWORD_CHANGE_TOKEN_LIFETIME']


class Token(models.Model):
    REGISTRATION_TOKEN = 'rt'
    REGISTRATION_DELETE_TOKEN = 'rd'
    PASSWORD_CHANGE_TOKEN = 'pc'
    TOKEN_TYPES = (
        (REGISTRATION_TOKEN, _('Registration token')),
        (REGISTRATION_DELETE_TOKEN, _('Registration Delete Token')),
        (PASSWORD_CHANGE_TOKEN, _('Password Change Token')),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(choices=TOKEN_TYPES, max_length=3, default=REGISTRATION_TOKEN)

    @property
    def lifetime(self):
        return {
            Token.REGISTRATION_TOKEN: REGISTRATION_TOKEN_LIFETIME,
            Token.REGISTRATION_DELETE_TOKEN: REGISTRATION_DELETE_TOKEN_LIFETIME,
            Token.PASSWORD_CHANGE_TOKEN: PASSWORD_CHANGE_TOKEN_LIFETIME,
        }[self.type]

    @property
    def expires_at(self):
        return self.created_at.astimezone(datetime.timezone.utc) + datetime.timedelta(seconds=self.lifetime)
