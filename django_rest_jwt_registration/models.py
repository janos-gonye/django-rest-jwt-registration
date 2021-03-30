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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
