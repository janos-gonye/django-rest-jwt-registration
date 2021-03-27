import time
import uuid

import jwt
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django_rest_jwt_registration.exceptions import BadRequestError


REGISTRATION_TOKEN = 'registration'
REGISTRATION_DELETE_TOKEN = 'registration_delete'
PASSWORD_CHANGE_TOKEN = 'password_change'


def encode_token(payload, token_type, lifetime, from_=None):
     # Don't lose reference
    payload = dict(payload)
    if not from_:
        from_ = time.time()
    payload['__expires_at__'] = from_ + lifetime
    # Add some randomness to the token
    payload['__randomness__'] = str(uuid.uuid4())
    payload['__token_type__'] = token_type
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def decode_token(token, token_type):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.PyJWTError as err:
        raise BadRequestError(_('Token invalid')) from err
    if payload.get('__token_type__') != token_type:
        raise BadRequestError(_('Token invalid'))

    if time.time() > payload['__expires_at__']:
        raise BadRequestError(_('Token expired'))
    del payload['__expires_at__']
    del payload['__randomness__']
    del payload['__token_type__']
    return payload
