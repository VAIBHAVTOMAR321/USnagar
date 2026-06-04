from django.urls import path
from .views import (
    CreateDepartmentAPIView, 
    LoginAPIView, 
    RefreshTokenAPIView,
    DepartmentListAPIView,
    DepartmentDetailAPIView,
    DivisionListCreateAPIView,
    DivisionDetailAPIView,
    DivisionBulkUpdateHeadAPIView,
    DivisionByHeadListAPIView,
    WorkAPIView,
    WorkDetailAPIView,
    WorkImageAPIView,
)

urlpatterns = [
    path(
        'login/',
        LoginAPIView.as_view(),
        name='login'
    ),
     path(
        "departments/create/",
        CreateDepartmentAPIView.as_view()
    ),
    path(
        "departments/",
        DepartmentListAPIView.as_view()
    ),
    path(
        "departments/<int:pk>/",
        DepartmentDetailAPIView.as_view()
    ),
    path(
        "divisions/",
        DivisionListCreateAPIView.as_view()
    ),
    path(
        "divisions/<int:pk>/",
        DivisionDetailAPIView.as_view()
    ),
    path("divisions/bulk-update-head/", DivisionBulkUpdateHeadAPIView.as_view()),
    path("divisions/by-head/", DivisionByHeadListAPIView.as_view()),
    path("token/refresh/", RefreshTokenAPIView.as_view()),
    path(
    "work-details/",
    WorkDetailAPIView.as_view()
),

path(
    "work-images/",
    WorkImageAPIView.as_view()
),
    path(
    "works/",
    WorkAPIView.as_view()
),
]