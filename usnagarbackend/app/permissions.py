from rest_framework.permissions import BasePermission


class IsITCellUser(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role == "it_cell"
        )

class IsITCellOrDepartment(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["it_cell", "department", "admin"]
        )

class IsAdminOrITCell(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["admin", "it_cell"]
        )

class IsITCellOrOwnDepartment(BasePermission):

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        if request.user.role == "it_cell":
            return True
            
        return request.user.role == "department" and obj.user == request.user

class IsDivisionOwnerOrStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        if request.user.role in ["admin", "it_cell"]:
            return True
            
        return (request.user.role == "department" and 
                hasattr(request.user, 'department') and 
                obj.department == request.user.department)
    

class IsDepartmentOrITCell(
    BasePermission
):

    def has_permission(
        self,
        request,
        view
    ):

        return (
            request.user.is_authenticated
            and request.user.role in [
                "department",
                "it_cell",
                "admin"
            ]
        )