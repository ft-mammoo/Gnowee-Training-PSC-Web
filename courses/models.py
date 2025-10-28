from django.db import models
from utility.models import BaseModel

class Course(BaseModel):
    STATUS_CHOICES = (
        ('d', 'Draft'),
        ('p', 'Published'),
        ('a', 'Archived'),
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='d'
    )

    def __str__(self):
        return f"{self.id} - {self.title}"
