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

from drjr import serializers, token as token_utils
from drjr.decorators import handle_token_decode_error
from drjr.models import Token
from drjr.utils import import_elm_from_str, send_mail


User = get_user_model()
try:
    CREATE_USER_SERIALIZER_PATH = settings.REST_JWT_REGISTRATION['CREATE_USER_SERIALIZER']
except KeyError:
    CREATE_USER_SERIALIZER_PATH = 'drjr.serializers.CreateUserSerializer'
CreateUserSerializer = import_elm_from_str(CREATE_USER_SERIALIZER_PATH)


class RegistrationAPIView(APIView):
    permission_classes = ()

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        token, token_db_instance = token_utils.encode_token({}, Token.REGISTRATION_TOKEN)
        user = User.objects.create(is_active=False, **data)
        user.set_password(data['password'])
        user.save()
        token_db_instance.user = user
        token_db_instance.save()
        send_mail(
            subject=_('Confirm registration'),
            recipient_list=[data['email']],
            err_msg=_('Sending confirmation email failed'),
            template_name='drjr_email_registration.html',
            context={
                'user': user,
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

    @handle_token_decode_error
    def get(self, request):
        token = request.GET.get('token')
        if not token:
            return HttpResponseBadRequest(_('Token missing'))
        __, token_db_instance = token_utils.decode_token(token, Token.REGISTRATION_TOKEN)
        user = token_db_instance.user
        user.is_active = True
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
        token, __ = token_utils.encode_token({'user_id': user.id}, Token.REGISTRATION_DELETE_TOKEN)
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

    @handle_token_decode_error
    def get(self, request):
        token = request.GET.get('token')
        if not token:
            return HttpResponseBadRequest(_('Token missing'))
        payload, __ = token_utils.decode_token(token, Token.REGISTRATION_DELETE_TOKEN)
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
        token, __ = token_utils.encode_token({'user_id': user.id}, Token.PASSWORD_CHANGE_TOKEN)
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

    @handle_token_decode_error
    def get(self, request):
        token = request.GET.get('token')
        if not token:
            return HttpResponseBadRequest(_('Token missing'))
        payload, __ = token_utils.decode_token(token, Token.PASSWORD_CHANGE_TOKEN)
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
        return Response({'detail': _('Password changed')})

    def put(self, request):
        return self._change_password(request)

    def patch(self, request):
        return self._change_password(request)


class ChangeEmailAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.ChangeEmailSerializer

    def get_object(self):
        return self.request.user

    def _change_email(self, request):
        user = self.get_object()
        serializer = self.serializer_class(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        token, __ = token_utils.encode_token({
            'user_id': user.id,
            'email': email,
        }, Token.EMAIL_CHANGE_TOKEN)
        send_mail(
            subject=_('Change email'),
            recipient_list=[email],
            err_msg=_('Sending confirmation email failed'),
            template_name='drjr_email_change_email.html',
            context={
                'user': user,
                'confirm_url': self.build_confirm_url(token),
            },
        )
        return Response({'detail': _('Confirmation email sent if given email exists')})

    def build_confirm_url(self, token):
        current_app = self.request.resolver_match.app_name
        change_email_path = reverse('change_email', current_app=current_app)
        change_email_confirm_path = reverse('change_email_confirm', current_app=current_app)
        uri = self.request.build_absolute_uri()
        return uri.replace(change_email_path, change_email_confirm_path) + f'?token={token}'

    def put(self, request):
        return self._change_email(request)

    def patch(self, request):
        return self._change_email(request)


class ChangeEmailConfirmView(View):
    permission_classes = ()

    @handle_token_decode_error
    def get(self, request):
        token = request.GET.get('token')
        if not token:
            return HttpResponseBadRequest(_('Token missing'))
        payload, __ = token_utils.decode_token(token, Token.EMAIL_CHANGE_TOKEN)
        user = User.objects.get(pk=payload['user_id'])
        new_email = payload['email']
        user.email = new_email
        user.save()
        send_mail(
            subject=_('Email changed'),
            recipient_list=[user.email],
            err_msg=_('Sending email failed'),
            template_name='drjr_email_change_email_confirm.html',
            context={
                'user': user,
                'new_email': new_email,
            },
        )
        return render(request, 'drjr_email_change_confirm.html', context={
            'user': user,
        })
