from django.urls import path
from .views import CreateDepartmentAPIView, LoginAPIView, RefreshTokenAPIView

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
    path("token/refresh/", RefreshTokenAPIView.as_view()),
]