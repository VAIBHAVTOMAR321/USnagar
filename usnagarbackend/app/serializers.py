from rest_framework import serializers
from .models import Department, User, Division, Work, WorkDetail, WorkImage


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField()

class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class DepartmentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False
    )

    class Meta:
        model = Department
        fields = [
            "id",
            "name_en",
            "name_hi",
            "hod_name",
            "designation",
            "password"
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        if User.objects.filter(username=validated_data["name_en"]).exists():
            raise serializers.ValidationError({"name_en": "Department already exists."})
            
        user = User.objects.create_user(
            username=validated_data["name_en"],
            password=password,
            role="department"
        )
        return Department.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        name_en = validated_data.get("name_en")
        
        user = instance.user
        if name_en and name_en != instance.name_en:
            if User.objects.filter(username=name_en).exclude(id=user.id).exists():
                raise serializers.ValidationError({"name_en": "This name is already taken."})
            user.username = name_en
        
        if password:
            user.set_password(password)
        
        user.save()
        return super().update(instance, validated_data)

class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = [
            "id", "department", "name_en", 
            "name_hi", "head_name", "created_at"
        ]
        read_only_fields = ["id", "created_at", "head_name"]

class WorkSerializer(serializers.ModelSerializer):

    department_name_en = serializers.CharField(
        source="department.name_en",
        read_only=True
    )

    department_name_hi = serializers.CharField(
        source="department.name_hi",
        read_only=True
    )

    division_name_en = serializers.CharField(
        source="division.name_en",
        read_only=True
    )

    division_name_hi = serializers.CharField(
        source="division.name_hi",
        read_only=True
    )

    class Meta:

        model = Work

        fields = [
            "id",
            "work_id",

            "department",
            "department_name_en",
            "department_name_hi",

            "division",
            "division_name_en",
            "division_name_hi",

            "vidhan_sabha",
            "project_name",
            "village_name",
            "head_name",
            "component",
            "scheme_type",
            "work_name",

            "created_at",
            "updated_at"
        ]

        read_only_fields = [
            "id",
            "work_id",
            "created_at",
            "updated_at",
            "department_name_en",
            "department_name_hi",
            "division_name_en",
            "division_name_hi"
        ]

class WorkDetailSerializer(serializers.ModelSerializer):
    # This maps the 'work' relationship to the 'work_id' string field on the Work model
    work_id = serializers.SlugRelatedField(
        source="work",
        slug_field="work_id",
        queryset=Work.objects.all()
    )

    class Meta:
        model = WorkDetail
        # Exclude internal 'work' field and show 'work_id' instead
        exclude = ["work"]

class WorkImageSerializer(serializers.ModelSerializer):
    # Same approach for images: link by work_id string
    work_id = serializers.SlugRelatedField(
        source="work",
        slug_field="work_id",
        queryset=Work.objects.all()
    )

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = WorkImage
        fields = [
            "id",
            "work_id",
            "phase_number",
            "image",
            "image_url",
            "uploaded_at"
        ]

    def get_image_url(
        self,
        obj
    ):

        request = self.context.get(
            "request"
        )

        if obj.image:

            return request.build_absolute_uri(
                obj.image.url
            )

        return None