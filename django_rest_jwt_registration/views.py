from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import View
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_rest_jwt_registration.utils import import_elm_from_str, send_mail
from django_rest_jwt_registration import serializers, token as token_utils


User = get_user_model()
CreateUserSerializer = import_elm_from_str(settings.REST_JWT_REGISTRATION['CREATE_USER_SERIALIZER'])
REGISTRATION_TOKEN_LIFETIME = settings.REST_JWT_REGISTRATION['REGISTRATION_TOKEN_LIFETIME']
REGISTRATION_DELETE_TOKEN_LIFETIME = settings.REST_JWT_REGISTRATION['REGISTRATION_DELETE_TOKEN_LIFETIME']
PASSWORD_CHANGE_TOKEN_LIFETIME = settings.REST_JWT_REGISTRATION['PASSWORD_CHANGE_TOKEN_LIFETIME']


class RegistrationAPIView(APIView):
    permission_classes = ()

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        token = token_utils.encode_token(data, token_utils.REGISTRATION_TOKEN, lifetime=REGISTRATION_TOKEN_LIFETIME)
        send_mail(
            subject=_('Confirm registration'),
            recipient_list=[data['email']],
            err_msg=_('Sending confirmation email failed'),
            template_name='drjr_email_registration.html',
            context={
                'user': User(**data),
                'confirm_url': self.build_confirm_url(token),
            },
        )
        return Response({'detail': _('Confirmation email sent')})

    def build_confirm_url(self, token):
        current_app = self.request.resolver_match.app_name
        registration_path = reverse('registration', current_app=current_app)
        registration_confirm_path = reverse('registration_confirm', current_app=current_app)
        uri = self.request.build_absolute_uri()
        return uri.replace(registration_path, registration_confirm_path) + f'?token={token}'


class RegistrationConfirmView(View):
    permission_classes = ()

    def get(self, request):
        token = request.GET.get('token')
        if not token:
            return HttpResponseBadRequest(_('Token missing'))
        payload = token_utils.decode_token(token, token_utils.REGISTRATION_TOKEN)
        serializer = CreateUserSerializer(data=payload)
        # If another user registered meanwhile, the username might already exist.
        # TODO: Store the username and email pair candidates on the server-side, and validate them.
        if not serializer.is_valid():
            return HttpResponseBadRequest(_('Token invalid'))
        data = dict(serializer.validated_data)
        user = User.objects.create(**data)
        user.set_password(data['password'])
        user.save()
        send_mail(
            subject=_('Registration activated'),
            recipient_list=[user.email],
            err_msg=_('Sending email failed'),
            template_name='drjr_email_registration_confirm.html',
            context={
                'user': user,
            },
        )
        return render(request, 'drjr_registration_confirm.html', context={
            'user': user,
        })


class RegistrationDeleteAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get_object(self):
        return User.objects.get(pk=self.request.user.id)

    def delete(self, request):
        user = self.get_object()
        print(user)
        token = token_utils.encode_token({
            'user_id': user.id}, token_utils.REGISTRATION_DELETE_TOKEN, lifetime=REGISTRATION_DELETE_TOKEN_LIFETIME)
        send_mail(
            subject=_('Delete account'),
            recipient_list=[user.email],
            err_msg=_('Sending confirmation email failed'),
            template_name='drjr_email_registration_delete.html',
            context={
                'user': user,
                'confirm_url': self.build_confirm_url(token),
            },
        )
        return Response({'detail': _('Confirmation email sent')})

    def build_confirm_url(self, token):
        current_app = self.request.resolver_match.app_name
        registration_delete_path = reverse('registration_delete', current_app=current_app)
        registration_delete_confirm_path = reverse('registration_delete_confirm', current_app=current_app)
        uri = self.request.build_absolute_uri()
        return uri.replace(registration_delete_path, registration_delete_confirm_path) + f'?token={token}'


class RegistrationConfirmDeleteView(View):
    permission_classes = ()

    def get(self, request):
        token = request.GET.get('token')
        if not token:
            return HttpResponseBadRequest(_('Token missing'))
        payload = token_utils.decode_token(token, token_utils.REGISTRATION_DELETE_TOKEN)
        user = User.objects.get(pk=payload['user_id'])
        user.delete()
        send_mail(
            subject=_('Account deleted'),
            recipient_list=[user.email],
            err_msg=_('Sending email failed'),
            template_name='drjr_email_registration_delete_confirm.html',
            context={
                'user': user,
            },
        )
        return render(request, 'drjr_registration_delete_confirm.html', context={
            'user': user,
        })


class ResetPasswordAPIView(APIView):
    permission_classes = ()
    serializer_class = serializers.ResetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.validated_data.get('email'))
        except User.DoesNotExist:
            return Response({'detail': _('Confirmation email sent if a user with given email address exists')})
        token = token_utils.encode_token({
            'user_id': user.id}, token_utils.PASSWORD_CHANGE_TOKEN, PASSWORD_CHANGE_TOKEN_LIFETIME)
        send_mail(
            subject=_('Reset password'),
            recipient_list=[user.email],
            err_msg=_('Sending confirmation email failed'),
            template_name='drjr_email_reset_password.html',
            context={
                'user': user,
                'confirm_url': self.build_confirm_url(token),
            },
        )
        return Response({'detail': _('Confirmation email sent if a user with given email address exists')})

    def build_confirm_url(self, token):
        current_app = self.request.resolver_match.app_name
        reset_password_path = reverse('reset_password', current_app=current_app)
        reset_password_confirm_path = reverse('reset_password_confirm', current_app=current_app)
        uri = self.request.build_absolute_uri()
        return uri.replace(reset_password_path, reset_password_confirm_path) + f'?token={token}'


class ResetPasswordConfirmView(View):
    permission_classes = ()

    def get(self, request):
        token = request.GET.get('token')
        if not token:
            return HttpResponseBadRequest(_('Token missing'))
        payload = token_utils.decode_token(token, token_utils.PASSWORD_CHANGE_TOKEN)
        user = User.objects.get(pk=payload['user_id'])
        new_password = User.objects.make_random_password()
        user.set_password(new_password)
        user.save()
        send_mail(
            subject=_('Reset password'),
            recipient_list=[user.email],
            err_msg=_('Sending email failed'),
            template_name='drjr_email_reset_password_confirm.html',
            context={
                'user': user,
                'new_password': new_password,
            },
        )
        return render(request, 'drjr_reset_password_confirm.html', context={
            'user': user,
        })


class ChangePasswordAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def _change_password(self, request):
        user = self.get_object()
        serializer = self.serializer_class(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_mail(
            subject=_('Password changed'),
            recipient_list=[user.email],
            err_msg=_('Sending email failed'),
            template_name='drjr_email_change_password.html',
            context={
                'user': user,
            },
        )
        # TODO: Update auth token
        return Response({'detail': _('Password changed')})

    def put(self, request):
        return self._change_password(request)

    def patch(self, request):
        return self._change_password(request)
