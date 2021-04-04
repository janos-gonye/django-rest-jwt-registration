import datetime

from django.conf import settings
from django.urls import path

from django_rest_jwt_registration.models import Token
from django_rest_jwt_registration import scheduler, views


urlpatterns = [
    path('registration/', views.RegistrationAPIView.as_view(), name='registration'),
    path('registration/confirm/', views.RegistrationConfirmView.as_view(), name='registration_confirm'),
    path('registration/delete/', views.RegistrationDeleteAPIView.as_view(), name='registration_delete'),
    path('registration/delete/confirm/', views.RegistrationConfirmDeleteView.as_view(), name='registration_delete_confirm'),
    path('reset-password/', views.ResetPasswordAPIView.as_view(), name='reset_password'),
    path('reset-password/confirm/', views.ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),
    path('change-password/', views.ChangePasswordAPIView.as_view(), name='change_password'),
]


def delete_expired_tokens():
    now = datetime.datetime.now().astimezone(datetime.timezone.utc)
    for token in Token.objects.all():
        if now > token.expires_at:
            if token.type == Token.REGISTRATION_TOKEN:
                token.user.delete()
            token.delete()


scheduler.interval(delete_expired_tokens, settings.REST_JWT_REGISTRATION['DELETE_EXPIRED_TOKENS_INTERVAL'])
