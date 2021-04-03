import datetime

import jwt
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django_rest_jwt_registration.exceptions import TokenDecodeError
from django_rest_jwt_registration.models import Token


def encode_token(payload, token_type):
     # Don't lose reference
    payload = dict(payload)
    token_db_instance = Token.objects.create(type=token_type)
    payload['__id__'] = str(token_db_instance.id)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def decode_token(token, token_type):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.PyJWTError as err:
        raise TokenDecodeError(_('Token invalid')) from err
    try:
        token = Token.objects.get(pk=payload['__id__'])
        token.delete()
    except Token.DoesNotExist as err:
        raise TokenDecodeError(_('Token invalid')) from err
    if token.type != token_type:
        raise TokenDecodeError(_('Token invalid'))
    if datetime.datetime.now().astimezone(datetime.timezone.utc) > token.expires_at:
        raise TokenDecodeError(_('Token expired'))
    del payload['__id__']
    return payload
