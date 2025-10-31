from django.db import models
from django.contrib.auth import get_user_model
from utility.models import BaseModel, SoftDeleteModel

User = get_user_model()

class Teacher(SoftDeleteModel):
    GENDER_CHOICES = (
        ("m", "Male"),
        ("f", "Female"),
        ("o", "Other"),
    )
    STATUS_CHOICES = (
        ("a", "Active"),
        ("i", "Inactive"),
        ("l", "On Leave"),
        ("r", "Resigned"),
        ("t", "Retired"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    employee_code = models.CharField(max_length=50, unique=True)
    experience_years = models.PositiveIntegerField(default=0)
    contact_number = models.CharField(max_length=10, null=True, blank=True)
    emergency_contact_number = models.CharField(max_length=10, null=True, blank=True)
    email_institutional = models.CharField(max_length=150, unique=True) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    profile_picture = models.CharField(max_length=255, blank=True, null=True)
    date_joined = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - ({self.employee_code})"

class Qualification(SoftDeleteModel):
    STATUS_CHOICES = (
        ("a", "Active"),
        ("i", "Inactive"),
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="a")

    def __str__(self):
        return f"{self.name}"

class UserQualification(SoftDeleteModel):
    STATUS_CHOICES = (
        ("a", "Active"),
        ("i", "Inactive"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    qualification = models.ForeignKey(Qualification, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="a")

    def __str__(self):
        return f"User {self.user} - Qualification {self.qualification}"

class Specialization(SoftDeleteModel):
    STATUS_CHOICES = (
        ("a", "Active"),
        ("i", "Inactive"),
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="a")

    def __str__(self):
        return f"{self.name}"

class UserSpecialization(SoftDeleteModel):
    STATUS_CHOICES = (
        ("a", "Active"),
        ("i", "Inactive"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="a")

    def __str__(self):
        return f"User {self.user} - Specialization {self.specialization}"

class Department(SoftDeleteModel):
    STATUS_CHOICES = (
        ("a", "Active"),
        ("i", "Inactive"),
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="a")

    def __str__(self):
        return f"{self.name}"

class UserDepartment(SoftDeleteModel):
    STATUS_CHOICES = (
        ("a", "Active"),
        ("i", "Inactive"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="a")

    def __str__(self):
        return f"User {self.user} - Department {self.department}"

class Designation(SoftDeleteModel):
    STATUS_CHOICES = (
        ("a", "Active"),
        ("i", "Inactive"),
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="a")

    def __str__(self):
        return f"{self.name}"

class UserDesignation(SoftDeleteModel):
    STATUS_CHOICES = (
        ("a", "Active"),
        ("i", "Inactive"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="a")

    def __str__(self):
        return f"User {self.user} - Designation {self.designation}"
