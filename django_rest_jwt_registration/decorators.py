from functools import wraps

from django.http import HttpResponseBadRequest

from django_rest_jwt_registration.exceptions import TokenDecodeError


def handle_token_decode_error(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        try:
            return view_function(*args, **kwargs)
        except TokenDecodeError as err:
            return HttpResponseBadRequest(str(err))
    return wrapper
