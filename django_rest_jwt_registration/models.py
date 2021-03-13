from django.core.validators import EmailValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class AbstractEmailRequiredUser(AbstractUser):
    email = models.EmailField(_('email address'), validators=[EmailValidator])

    class Meta:
        abstract = True
