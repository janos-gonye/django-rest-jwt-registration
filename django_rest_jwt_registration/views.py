from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class RegistrationAPIView(APIView):
    permission_classes = ()

    def post(self, request):
        return Response({'hello': 'world!'})


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
