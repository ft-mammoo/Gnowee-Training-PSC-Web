from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth import get_user_model
from utility.models import BaseModel

User = get_user_model()

class Student(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
    ), default='a')
    profile_picture = models.CharField(max_length=255, blank=True, null=True)
    date_joined = models.DateField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Enrollment(BaseModel):
    STATUS_CHOICES = (
        ('a', 'Active'),
        ('c', 'Completed'),
        ('d', 'Dropped'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='a'
    )

    def __str__(self):
        return f"Enrollment {self.id}: Student {self.student_id} in Course {self.course_id}"
