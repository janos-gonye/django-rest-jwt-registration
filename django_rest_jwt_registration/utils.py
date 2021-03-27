import importlib
import smtplib
import urllib.parse

from django.conf import settings
from django.core import mail

from django_rest_jwt_registration.exceptions import InternalServerError


def import_elm_from_str(string):
    elements = string.split('.')
    module, elm = '.'.join(elements[:-1]), elements[-1]
    module = importlib.import_module(module)
    return getattr(module, elm)


def get_full_template_name(name):
    return urllib.parse.urljoin('drjr', name)
  

def send_mail(subject, message, recipient_list, err_msg):
    try:
        mail.send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipient_list,
        )
    except smtplib.SMTPException as err:
        raise InternalServerError(err_msg) from err
