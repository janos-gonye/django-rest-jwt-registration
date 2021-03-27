import importlib
import smtplib

from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django_rest_jwt_registration.exceptions import InternalServerError


def import_elm_from_str(string):
    elements = string.split('.')
    module, elm = '.'.join(elements[:-1]), elements[-1]
    module = importlib.import_module(module)
    return getattr(module, elm)


def send_mail(subject, recipient_list, err_msg, template_name, context=None):
    context = context or {}
    try:
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        mail.send_mail(
            subject=subject,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipient_list,
            message=plain_message,
            html_message=html_message,
        )
    except smtplib.SMTPException as err:
        raise InternalServerError(err_msg) from err
