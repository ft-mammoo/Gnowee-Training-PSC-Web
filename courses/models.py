from django.db import models
from utility.models import BaseModel, SoftDeleteModel

class Course(SoftDeleteModel):
    STATUS_CHOICES = (
        ('d', 'Draft'),
        ('p', 'Published'),
        ('a', 'Archived'),
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='d')

    def __str__(self):
        return f"{self.id} - {self.title}"

class CourseTeachers(SoftDeleteModel):
    STATUS_CHOICES = (
        ('a', 'Active'),
        ('i', 'Inactive'),
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_teachers')
    teacher = models.ForeignKey('staffs.Teacher', on_delete=models.CASCADE, related_name='teacher_courses')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='a')

    def __str__(self):
        return f"Course {self.course_id} - Teacher {self.teacher_id}"

class Material(SoftDeleteModel):
    TYPE_CHOICES = (
        ('d', 'Document'),
        ('v', 'Video'),
        ('l', 'Link'),
        ('s', 'Slides'),
    )
    STATUS_CHOICES = (
        ('a', 'Active'),
        ('i', 'Inactive'),
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    teacher = models.ForeignKey('staffs.Teacher', on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    file_url = models.CharField(max_length=255)
    uploaded_at = models.DateField(auto_now_add=True)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='a')

    def __str__(self):
        return f"Material {self.id} - {self.title}"
