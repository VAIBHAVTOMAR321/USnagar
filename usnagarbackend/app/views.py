from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .permissions import (
    IsITCellUser, 
    IsITCellOrOwnDepartment, 
    IsAdminOrITCell, 
    IsDivisionOwnerOrStaff,
    IsITCellOrDepartment,
    IsDepartmentOrITCell
)
from .serializers import (
    LoginSerializer,
    RefreshTokenSerializer,
    DepartmentSerializer,
    DivisionSerializer,
    WorkSerializer
)
from .models import Department, Division, Work
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

        response_data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": user.role,
            "username": user.username
        }

        # Include department_id only for department users
        if user.role == "department" and hasattr(user, "department"):
            response_data["department_id"] = user.department.id

        return Response(response_data)

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

        serializer = DepartmentSerializer(
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

class DepartmentListAPIView(APIView):

    permission_classes = []

    def get(self, request):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)

class DepartmentDetailAPIView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        if self.request.method == 'DELETE':
            return [IsITCellUser()]
        return [IsAuthenticated(), IsITCellOrOwnDepartment()]

    def get(self, request, pk):
        department = get_object_or_404(Department, pk=pk)
        serializer = DepartmentSerializer(department)
        return Response(serializer.data)

    def put(self, request, pk):
        department = get_object_or_404(Department, pk=pk)
        self.check_object_permissions(request, department)
        
        serializer = DepartmentSerializer(
            department, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Department updated successfully",
                    "department": serializer.data
                }
            )
            
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        department = get_object_or_404(Department, pk=pk)
        self.check_object_permissions(request, department)
        
        # Delete the user which will cascade delete the department
        department.user.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class DivisionListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role in ["admin", "it_cell"]:
            divisions = Division.objects.all()
        else:
            divisions = Division.objects.filter(department__user=user)
            
        serializer = DivisionSerializer(divisions, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()

        # For department role, auto-assign their department profile
        if request.user.role == "department":
            if not hasattr(request.user, 'department'):
                return Response({"error": "User has no department profile."}, status=status.HTTP_400_BAD_REQUEST)
            data['department'] = request.user.department.id
            
        serializer = DivisionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
            
        return Response(
            {
                "message": "Division created successfully",
                "division": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

class DivisionDetailAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsDivisionOwnerOrStaff()]
        return [IsITCellUser()]

    def get(self, request, pk):
        division = get_object_or_404(Division, pk=pk)
        self.check_object_permissions(request, division)
        serializer = DivisionSerializer(division)
        return Response(serializer.data)

    def put(self, request, pk):
        division = get_object_or_404(Division, pk=pk)
        self.check_object_permissions(request, division)
        
        serializer = DivisionSerializer(division, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Division updated successfully",
                    "division": serializer.data
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        division = get_object_or_404(Division, pk=pk)
        self.check_object_permissions(request, division)
        division.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DivisionBulkUpdateHeadAPIView(APIView):
    """
    Allows IT Cell or the owning Department to assign multiple divisions to one head member.
    Expected data: {"division_ids": [1, 2], "head_name": "Name"}
    """
    permission_classes = [IsITCellOrDepartment]

    def put(self, request):
        division_ids = request.data.get("division_ids", [])
        head_name = request.data.get("head_name")

        if not division_ids or not head_name:
            return Response(
                {"error": "division_ids and head_name are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        divisions = Division.objects.filter(id__in=division_ids)

        # If the user is a department, they can only update their own divisions
        if request.user.role == "department":
            if not hasattr(request.user, 'department'):
                return Response({"error": "User has no department profile."}, status=status.HTTP_400_BAD_REQUEST)
            divisions = divisions.filter(department=request.user.department)

        updated_count = divisions.update(head_name=head_name)

        return Response(
            {
                "message": f"Successfully updated {updated_count} divisions.",
                "head_name": head_name,
                "updated_ids": division_ids
            },
            status=status.HTTP_200_OK
        )

class DivisionByHeadListAPIView(APIView):
    """
    Returns divisions grouped by their assigned head member.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role in ["admin", "it_cell"]:
            divisions = Division.objects.all()
        else:
            divisions = Division.objects.filter(department__user=user)

        # Grouping logic
        grouped_data = {}
        for div in divisions:
            head = div.head_name or "Unassigned"
            if head not in grouped_data:
                grouped_data[head] = []
            
            grouped_data[head].append({
                "id": div.id,
                "name_en": div.name_en,
                "name_hi": div.name_hi,
                "department_name": div.department.name_en if div.department else None
            })

        formatted_response = [
            {"head_name": head, "divisions": divs}
            for head, divs in grouped_data.items()
        ]

        return Response(formatted_response)
    
class WorkAPIView(APIView):

    def get_permissions(self):

        if self.request.method in [
            "POST",
            "PUT",
            "DELETE"
        ]:
            return [
                IsDepartmentOrITCell()
            ]

        return []

    def get(self, request):

        work_id = request.query_params.get(
            "id"
        )

        if work_id:

            work = get_object_or_404(
                Work,
                id=work_id
            )

            serializer = WorkSerializer(
                work
            )

            return Response(
                serializer.data
            )

        works = Work.objects.all().order_by(
            "-created_at"
        )

        serializer = WorkSerializer(
            works,
            many=True
        )

        return Response(
            serializer.data
        )

    def post(self, request):

        serializer = WorkSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        work = serializer.save(
            created_by=request.user
        )

        return Response(
            {
                "message":
                "Work created successfully",
                "work_id":
                work.work_id,
                "data":
                WorkSerializer(
                    work
                ).data
            },
            status=status.HTTP_201_CREATED
        )

    def put(self, request):

        work_id = request.data.get(
            "id"
        )

        if not work_id:

            return Response(
                {
                    "message":
                    "id is required"
                },
                status=400
            )

        work = get_object_or_404(
            Work,
            id=work_id
        )

        serializer = WorkSerializer(
            work,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "message":
                "Work updated successfully",
                "data":
                serializer.data
            }
        )

    def delete(self, request):

        work_id = request.data.get(
            "id"
        )

        if not work_id:

            return Response(
                {
                    "message":
                    "id is required"
                },
                status=400
            )

        work = get_object_or_404(
            Work,
            id=work_id
        )

        work.delete()

        return Response(
            {
                "message":
                "Work deleted successfully"
            }
        )