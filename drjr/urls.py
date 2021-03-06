from django.urls import path

from drjr import scheduler, views
from drjr.apps import DjangoRestJwtRegistrationConfig
from drjr.models import Token

DELETE_EXPIRED_TOKENS_INTERVAL = DjangoRestJwtRegistrationConfig.settings['DELETE_EXPIRED_TOKENS_INTERVAL']


urlpatterns = [
    path('registration/', views.RegistrationAPIView.as_view(), name='registration'),
    path('registration/confirm/', views.RegistrationConfirmView.as_view(), name='registration_confirm'),
    path('registration/delete/', views.RegistrationDeleteAPIView.as_view(), name='registration_delete'),
    path('registration/delete/confirm/', views.RegistrationConfirmDeleteView.as_view(), name='registration_delete_confirm'),
    path('reset-password/', views.ResetPasswordAPIView.as_view(), name='reset_password'),
    path('reset-password/confirm/', views.ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),
    path('change-password/', views.ChangePasswordAPIView.as_view(), name='change_password'),
    path('change-email/', views.ChangeEmailAPIView.as_view(), name='change_email'),
    path('change-email/confirm/', views.ChangeEmailConfirmView.as_view(), name='change_email_confirm'),
]


scheduler.interval(Token.objects.delete_expired_tokens, DELETE_EXPIRED_TOKENS_INTERVAL)
