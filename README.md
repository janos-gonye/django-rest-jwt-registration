# Django REST JWT Registration

JSON web token-based user registration REST API on the top of Django REST Framework.

Perfect choice to combine with `djangorestframework`
and `djangorestframework-simplejwt`.

## Requirements:
- Django (2.0+, 3.0+) and Django-REST-Framework (3.3+)
- PyJWT (tested on 2.0+)

## Features
- registration (sign-up)
- change password
- change email
- reset (forgotton) password (new password sent in email)
- delete registration

All with automatic confirmation email.

## Installation and Configuration

Install the app using pip.

```sh
pip install django-rest-jwt-registration @ git+https://github.com/janos-gonye/django-rest-jwt-registration.git@main
```

Then, you need to add `drjr` to `INSTALLED_APPS`.

```py
INSTALLED_APPS = [
    '...,'

    'rest_registration',

    '...,'
]
```

After that, you can use the new urls in your `urls.py` file.

```py
urlpatterns = [
    '...',

    path('account/', include('drjr.urls'),

    '...',
]
```

Add configs to `settings.py`.

```py
# Expiration time in seconds
DJANGO_REST_JWT_REGISTRATION = {
    # Optional
    'CREATE_USER_SERIALIZER': 'core.serializers.CreateUserSerializer',
    # Optional
    'REGISTRATION_TOKEN_LIFETIME': int(os.getenv('REGISTRATION_TOKEN_LIFETIME', '3600')),
    # Optional
    'REGISTRATION_DELETE_TOKEN_LIFETIME': int(os.getenv('REGISTRATION_DELETE_TOKEN_LIFETIME', '3600')),
    # Optional
    'PASSWORD_CHANGE_TOKEN_LIFETIME': int(os.getenv('PASSWORD_CHANGE_TOKEN_LIFETIME', '3600')),
    # Optional
    'EMAIL_CHANGE_TOKEN_LIFETIME': int(os.getenv('EMAIL_CHANGE_TOKEN_LIFETIME', '3600')),
    # Optional
    'DELETE_EXPIRED_TOKENS_INTERVAL': int(os.getenv('DELETE_EXPIRED_TOKENS_INTERVAL', '60')),
    # Optional
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = int(os.getenv('EMAIL_PORT'))
EMAIL_USE_TLS = bool(int(os.getenv('EMAIL_USE_TLS')))
EMAIL_USE_SSL = bool(int(os.getenv('EMAIL_USE_SSL')))
```

> Note
`DELETE_EXPIRED_TOKEN_INTERVAL` specifies the frequency to delete expired
tokens and the corresponding users that have not yet been activated
(User.is_active == False). Note, not all inactive users get deleted, but only
those whose registration is not confirmed.
(Users who do not confirm their email addresses.)

The email field of Django's default user model is not unique. If you don't want
to let your users register multiple accounts with the same email, you better override it.

```py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
```

And set as your user model in `settings.py`.

```py
AUTH_USER_MODEL = "your_app.User"
```

If `CREATE_USER_SERIALIZER` is not provided, a default gets applied.
Supplied by the `drjr` package. Shown below.

```py
from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        read_only_fields = ('id', 'last_login', 'date_joined')
```

> Warning!<br>
Be careful and do not allow `is_staff` or` is_superuser` fields to be writable.
By allowing them to be writable, you would create a serious vulnerability,
and clever but malicious users could take control over your site in the worst case.

## Customizing Default Email Templates

The default templates are very bare with no styling or whatsoever.
But no worries, you can override any or all of the templates as you please.

These are the existing template files:

- `drjr_email_change_confirm.html`
- `drjr_email_change_email_confirm.html`
- `drjr_email_change_email.html`
- `drjr_email_change_password.html`
- `drjr_email_registration_confirm.html`
- `drjr_email_registration_delete_confirm.html`
- `drjr_email_registration_delete.html`
- `drjr_email_registration.html`
- `drjr_email_reset_password_confirm.html`
- `drjr_email_reset_password.html`
- `drjr_registration_confirm.html`
- `drjr_registration_delete_confirm.html`
- `drjr_reset_password_confirm.html`

Or you may be better off creating a folder named `drjr` inside your
`templates` directory to keep files organized.

```
mkdir ./templates/drjr
```

And add it to the template directories in `settings.py`.

```py
import os.path


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'templates',
            os.path.join('templates', 'drjr'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

> Note<br>
The actual `User` model instance created, deleted, or modified as a context variable is available in every template named as `user`.

E.g., in `drjr_email_reset_password_confirm.html`.

```html
<h3>Default Template Overridden</h3>
<p>
Dear <strong>{{ user.username }}</strong>,<br>
<br>
Your email address has been changed as requested.<br>
<br>

Sincerely Yours,<br>
Your developer
</em>
</p>
```
