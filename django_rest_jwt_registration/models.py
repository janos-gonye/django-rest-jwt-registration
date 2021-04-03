import uuid

from django.core.validators import EmailValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class AbstractEmailRequiredUser(AbstractUser):
    email = models.EmailField(_('email address'), validators=[EmailValidator])

    class Meta:
        abstract = True


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
