from rest_framework import serializers

from .models import Department, User


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField()

class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
class DepartmentCreateSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = Department
        fields = [
            "name_en",
            "name_hi",
            "password"
        ]

    def create(self, validated_data):

        password = validated_data.pop("password")

        if User.objects.filter(
            username=validated_data["name_en"]
        ).exists():
            raise serializers.ValidationError(
                {
                    "name_en": "Department already exists."
                }
            )

        user = User.objects.create_user(
            username=validated_data["name_en"],
            password=password,
            role="department"
        )

        department = Department.objects.create(
            user=user,
            **validated_data
        )

        return department