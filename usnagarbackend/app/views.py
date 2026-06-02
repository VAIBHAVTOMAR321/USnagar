from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsITCellUser
from .serializers import (
    LoginSerializer,
    DepartmentCreateSerializer,
    RefreshTokenSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class LoginAPIView(APIView):

    permission_classes = []

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(
            username=username,
            password=password
        )

        if not user:
            return Response(
                {
                    "message": "Invalid Credentials"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role": user.role,
                "username": user.username
            }
        )

class RefreshTokenAPIView(APIView):

    permission_classes = []

    def post(self, request):

        serializer = RefreshTokenSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            refresh = RefreshToken(
                serializer.validated_data["refresh"]
            )

            return Response(
                {
                    "access": str(
                        refresh.access_token
                    )
                },
                status=status.HTTP_200_OK
            )

        except TokenError:

            return Response(
                {
                    "message": "Invalid or expired refresh token"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

class CreateDepartmentAPIView(APIView):

    permission_classes = [IsITCellUser]

    def post(self, request):

        serializer = DepartmentCreateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        department = serializer.save()

        return Response(
            {
                "message": "Department created successfully",
                "department": {
                    "id": department.id,
                    "name_en": department.name_en,
                    "name_hi": department.name_hi
                },
                "login": {
                    "username": department.user.username,
                    "role": department.user.role
                }
            },
            status=status.HTTP_201_CREATED
        )