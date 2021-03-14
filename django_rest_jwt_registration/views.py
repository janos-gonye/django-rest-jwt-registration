import smtplib

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_rest_jwt_registration.utils import import_elm_from_str
from django_rest_jwt_registration.token import encode_token, TokenTypes
from django_rest_jwt_registration.exceptions import InternalServerError


CreateUserSerializer = import_elm_from_str(settings.REST_JWT_REGISTRATION['CREATE_USER_SERIALIZER'])
REGISTRATION_TOKEN_LIFETIME = settings.REST_JWT_REGISTRATION['REGISTRATION_TOKEN_LIFETIME']
REGISTRATION_TOKEN_DELETE_LIFETIME = settings.REST_JWT_REGISTRATION['REGISTRATION_DELETE_TOKEN_LIFETIME']


class RegistrationAPIView(APIView):
    permission_classes = ()

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        token = encode_token(data, TokenTypes.REGISTRATION_TOKEN, lifetime=REGISTRATION_TOKEN_LIFETIME)
        confirm_url = self.build_confirm_url(token)
        try:
            mail.send_mail(
                subject=_('Confirm registration'),
                message=confirm_url,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[data['email']],
            )
            return Response({'detail': _('Confirmation email sent')})
        except smtplib.SMTPException as err:
            raise InternalServerError(_('Error when sending confirmation email')) from err

    def build_confirm_url(self, token):
        current_app = self.request.resolver_match.app_name
        registration_path = reverse('registration', current_app=current_app)
        registration_confirm_path = reverse('registration_confirm', current_app=current_app)
        uri = self.request.build_absolute_uri()
        return uri.replace(registration_path, registration_confirm_path) + f'?token={token}'


class RegistrationConfirmAPIView(APIView):
    permission_classes = ()

    def get(self, request):
        return Response({'hello': 'world!'})


class RegistrationDeleteAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get_object(self):
        return get_user_model().objects.get(pk=self.request.user.id)

    def post(self, request):
        return Response({'hello': 'world!'})


class RegistrationConfirmDeleteAPIView(APIView):
    permission_classes = ()

    def get(self, request):
        return Response({'hello': 'world!'})
