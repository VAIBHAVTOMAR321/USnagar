from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)


class UserManager(BaseUserManager):

    def create_user(self, username, password=None, role="department"):

        user = self.model(
            username=username,
            role=role
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password):

        user = self.create_user(
            username=username,
            password=password,
            role="admin"
        )

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("it_cell", "IT Cell"),
        ("department", "Department"),
    )

    username = models.CharField(
        max_length=100,
        unique=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    USERNAME_FIELD = "username"

    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.username


class Department(models.Model):

    name_en = models.CharField(
        max_length=100,
        unique=True,blank=True,null=True
    )

    name_hi = models.CharField(
        max_length=200,blank=True,null=True
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name_en

class Division(models.Model):
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        related_name='divisions'
    )
    name_en = models.CharField(max_length=100)
    name_hi = models.CharField(max_length=200, blank=True, null=True)
    head_name = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name_en} ({self.department.name_en if self.department else 'N/A'})"