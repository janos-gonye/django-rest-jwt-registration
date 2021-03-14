from django.urls import path
from django_rest_jwt_registration import views


urlpatterns = [
    path('registration/', views.RegistrationAPIView.as_view(), name='registration'),
    path('registration/confirm/', views.RegistrationConfirmAPIView.as_view(), name='registration_confirm'),
    path('registration/delete/', views.RegistrationDeleteAPIView.as_view(), name='registration_delete'),
    path('registration/delete/confirm/', views.RegistrationConfirmDeleteAPIView.as_view(), name='registration_delete_confirm'),
]
