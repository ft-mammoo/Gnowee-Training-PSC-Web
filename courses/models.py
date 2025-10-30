from django.db import models
from utility.models import BaseModel
from django.dispatch import receiver

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

@receiver(models.signals.pre_save, sender=Course)
def course_pre_save_reciever(sender, instance, **kwargs):
    print("Course Pre-Save Signal Triggered")
    instance.description = "Signal Description Update"

@receiver(models.signals.post_save, sender=Course)
def course_post_save_reciever(sender, instance, created, **kwargs):
    if created:
        print("Course Post-Save Signal Triggered - New Course Created")
    else:
        print("Course Post-Save Signal Triggered - Course Updated")
