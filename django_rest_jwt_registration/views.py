from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_rest_jwt_registration.utils import import_elm_from_str, send_mail
from django_rest_jwt_registration import token as token_utils
from django_rest_jwt_registration.exceptions import BadRequestError


User = get_user_model()
CreateUserSerializer = import_elm_from_str(settings.REST_JWT_REGISTRATION['CREATE_USER_SERIALIZER'])
REGISTRATION_TOKEN_LIFETIME = settings.REST_JWT_REGISTRATION['REGISTRATION_TOKEN_LIFETIME']
REGISTRATION_DELETE_TOKEN_LIFETIME = settings.REST_JWT_REGISTRATION['REGISTRATION_DELETE_TOKEN_LIFETIME']


class RegistrationAPIView(APIView):
    permission_classes = ()

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        token = token_utils.encode_token(data, token_utils.REGISTRATION_TOKEN, lifetime=REGISTRATION_TOKEN_LIFETIME)
        confirm_url = self.build_confirm_url(token)
        send_mail(
            subject=_('Confirm registration'),
            message=confirm_url,
            recipient_list=[data['email']],
            err_msg=_('Sending confirmation email failed'),
        )
        return Response({'detail': _('Confirmation email sent')})

    def build_confirm_url(self, token):
        current_app = self.request.resolver_match.app_name
        registration_path = reverse('registration', current_app=current_app)
        registration_confirm_path = reverse('registration_confirm', current_app=current_app)
        uri = self.request.build_absolute_uri()
        return uri.replace(registration_path, registration_confirm_path) + f'?token={token}'


class RegistrationConfirmAPIView(APIView):
    permission_classes = ()

    def get(self, request):
        token = request.GET.get('token')
        if not token:
            raise BadRequestError(_('Token missing'))
        payload = token_utils.decode_token(token, token_utils.REGISTRATION_TOKEN)
        serializer = CreateUserSerializer(data=payload)
        # If another user registered meanwhile, the username might already exist.
        # TODO: Store the username and email pair candidates on the server-side, and validate them.
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        user = User.objects.create(**data)
        user.set_password(data['password'])
        user.save()
        send_mail(
            subject=_('Registration activated'),
            message='Registration activated',
            recipient_list=[user.email],
            err_msg=_('Sending email failed'),
        )
        return Response({'detail': _('Successfully registered')})


class RegistrationDeleteAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get_object(self):
        return User.objects.get(pk=self.request.user.id)

    def get(self, request):
        user = self.get_object()
        print(user)
        token = token_utils.encode_token({
            'user_id': user.id}, token_utils.REGISTRATION_DELETE_TOKEN, lifetime=REGISTRATION_DELETE_TOKEN_LIFETIME)
        confirm_url = self.build_confirm_url(token)
        send_mail(
            subject=_('Delete account'),
            message=confirm_url,
            recipient_list=[user.email],
            err_msg=_('Sending confirmation email failed'),
        )
        return Response({'detail': _('Confirmation email sent')})

    def build_confirm_url(self, token):
        current_app = self.request.resolver_match.app_name
        registration_delete_path = reverse('registration_delete', current_app=current_app)
        registration_delete_confirm_path = reverse('registration_delete_confirm', current_app=current_app)
        uri = self.request.build_absolute_uri()
        return uri.replace(registration_delete_path, registration_delete_confirm_path) + f'?token={token}'


class RegistrationConfirmDeleteAPIView(APIView):
    permission_classes = ()

    def get(self, request):
        token = request.GET.get('token')
        if not token:
            raise BadRequestError(_('Token missing'))
        payload = token_utils.decode_token(token, token_utils.REGISTRATION_DELETE_TOKEN)
        user = User.objects.get(pk=payload['user_id'])
        user.delete()
        send_mail(
            subject=_('Account deleted'),
            message=_('Account deleted'),
            recipient_list=[user.email],
            err_msg=_('Sending email failed'),
        )
        return Response({'detail': _('Successfully deleted')})


class PasswordChangeAPIView(APIView):
    permission_classes = ()

    def get(self, request):
        return Response({'hello': 'wordl!'})


class PasswordChangeConfirmAPIView(APIView):
    permission_classes = ()

    def get(self, request):
        return Response({'hello': 'world!'})
