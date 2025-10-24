from django.db import models
from django.core.validators import MinLengthValidator

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=(
        ('M', 'Male'),('F', 'Female'),('O', 'Other')
    ))
    contact_number = models.CharField(max_length=10, validators=[MinLengthValidator(10)])
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_number = models.CharField(max_length=10, validators=[MinLengthValidator(10)])
    status = models.CharField(max_length=1, choices=(
        ('a', 'Active'), ('s', 'Suspended'), ('g', 'Graduated'), ('w', 'Withdrawn')
    ), default='active')
    profile_picture = models.CharField(max_length=255, blank=True, null=True)
    date_joined = models.DateField()
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
