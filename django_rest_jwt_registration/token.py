import enum
import time
import uuid

import jwt
from django.conf import settings


class TokenTypes(enum.Enum):
    REGISTRATION_TOKEN = 0
    REGISTRATION_DELETE_TOKEN = 1


def encode_token(payload, token_type, lifetime, from_=None):
    if not from_:
        from_ = time.time()
    payload['__expires_at__'] = from_ + lifetime
    # Add some randomness to the token
    payload['__randomness__'] = str(uuid.uuid4())
    payload[token_type] = True
    return jwt.encode(payload, settings.SECRET_KEY)


def decode_token(token, token_type):
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
    except jwt.PyJWTError as err:
        raise ValueError() from err
    if payload.get(token_type) is not True:
        return ValueError()
    if time.time() > payload['__expires_at__']:
        raise ValueError()
    del payload['__expires_at__']
    del payload['__randomness__']
    return payload
