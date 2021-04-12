import datetime

import jwt
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django_rest_jwt_registration.exceptions import TokenDecodeError
from django_rest_jwt_registration.models import Token


def encode_token(payload, token_type):
    # Lose reference
    payload = dict(payload)
    token_db_instance = Token.objects.create(type=token_type)
    payload['__id__'] = str(token_db_instance.id)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256'), token_db_instance


def decode_token(token, token_type):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.PyJWTError as err:
        raise TokenDecodeError(_('Token invalid')) from err
    try:
        token = Token.objects.get(pk=payload['__id__'])
    except Token.DoesNotExist as err:
        raise TokenDecodeError(_('Token invalid')) from err
    if token.type != token_type:
        raise TokenDecodeError(_('Token invalid'))
    if datetime.datetime.now().astimezone(datetime.timezone.utc) > token.expires_at:
        if token.type == Token.REGISTRATION_TOKEN:
            token.user.delete()
        token.delete()
        raise TokenDecodeError(_('Token expired'))
    token.delete()
    del payload['__id__']
    return payload, token
