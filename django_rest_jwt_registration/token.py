import datetime

import jwt
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django_rest_jwt_registration.exceptions import TokenDecodeError
from django_rest_jwt_registration.models import Token


REGISTRATION_TOKEN = 'registration'
REGISTRATION_DELETE_TOKEN = 'registration_delete'
PASSWORD_CHANGE_TOKEN = 'password_change'
REGISTRATION_TOKEN_LIFETIME = settings.REST_JWT_REGISTRATION['REGISTRATION_TOKEN_LIFETIME']
REGISTRATION_DELETE_TOKEN_LIFETIME = settings.REST_JWT_REGISTRATION['REGISTRATION_DELETE_TOKEN_LIFETIME']
PASSWORD_CHANGE_TOKEN_LIFETIME = settings.REST_JWT_REGISTRATION['PASSWORD_CHANGE_TOKEN_LIFETIME']


def encode_token(payload, token_type):
     # Don't lose reference
    payload = dict(payload)
    token_db_instance = Token.objects.create()
    payload['__id__'] = str(token_db_instance.id)
    payload['__token_type__'] = token_type
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def _get_lifetime_by_token_type(token_type):
    try:
        return {
            REGISTRATION_TOKEN: REGISTRATION_TOKEN_LIFETIME,
            REGISTRATION_DELETE_TOKEN: REGISTRATION_DELETE_TOKEN_LIFETIME,
            PASSWORD_CHANGE_TOKEN: PASSWORD_CHANGE_TOKEN_LIFETIME,
        }[token_type]
    except KeyError as err:
        raise NotImplementedError(
            f"Token type '{token_type}' not registered in '_get_lifetime_by_token_type'") from err


def decode_token(token, token_type):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.PyJWTError as err:
        raise TokenDecodeError(_('Token invalid')) from err
    if payload.get('__token_type__') != token_type:
        raise TokenDecodeError(_('Token invalid'))
    try:
        token = Token.objects.get(pk=payload['__id__'])
        token.delete()
    except Token.DoesNotExist as err:
        raise TokenDecodeError(_('Token invalid')) from err
    lifetime = _get_lifetime_by_token_type(token_type)
    now = datetime.datetime.now().astimezone(datetime.timezone.utc)
    expired_at = token.created_at.astimezone(datetime.timezone.utc) + datetime.timedelta(seconds=lifetime)
    if now > expired_at:
        raise TokenDecodeError(_('Token expired'))
    del payload['__id__']
    del payload['__token_type__']
    return payload
