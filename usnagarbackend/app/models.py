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
        unique=True,
        blank=True,
        null=True
    )

    name_hi = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    hod_name = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    designation = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    hod_img = models.ImageField(
        upload_to="department_hod/",
        blank=True,
        null=True
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
    

class Work(models.Model):

    work_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="works",
        null=True,
        blank=True
    )

    division = models.ForeignKey(
        Division,
        on_delete=models.CASCADE,
        related_name="works"
    )

    vidhan_sabha = models.CharField(
        max_length=200
    )

    project_name = models.CharField(
        max_length=300
    )

    village_name = models.CharField(
        max_length=300
    )

    head_name = models.CharField(
        max_length=200
    )

    component = models.CharField(
        max_length=200
    )

    scheme_type = models.CharField(
        max_length=200
    )

    work_name = models.TextField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )
    def save(self, *args, **kwargs):

        if not self.work_id:

            last_work = Work.objects.order_by(
                "-id"
            ).first()

            if last_work and last_work.work_id:

                last_number = int(
                    last_work.work_id.split("-")[1]
                )

                new_number = last_number + 1

            else:

                new_number = 1

            self.work_id = (
                f"WORK-{new_number:04d}"
            )

        super().save(*args, **kwargs)

class WorkDetail(models.Model):

    work = models.OneToOneField(
        Work,
        on_delete=models.CASCADE,
        related_name="details",
        to_field="work_id"
    )

    sanction_date = models.DateField(
        null=True,
        blank=True
    )

    estimated_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    approved_outlay = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    dm_level_funds = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    released_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    balance_as_on_date = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    surrendered_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    work_start_date = models.DateField(
        null=True,
        blank=True
    )

    physical_target = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    unit = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    latitude = models.DecimalField(
        max_digits=12,
        decimal_places=8,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=12,
        decimal_places=8,
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.work.work_id


class WorkImage(models.Model):

    work = models.ForeignKey(
        Work,
        on_delete=models.CASCADE,
        related_name="images",
        to_field="work_id"
    )

    phase_number = models.PositiveIntegerField()

    image = models.ImageField(
        upload_to="work_images/"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.work.work_id} - Phase {self.phase_number}"