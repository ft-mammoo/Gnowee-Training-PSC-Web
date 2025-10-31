from django.db import models
from django.contrib.auth import get_user_model
from utility.models import BaseModel, SoftDeleteModel

User = get_user_model()

class Chat(SoftDeleteModel):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_chats')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    auditory = models.CharField(max_length=255)

    def __str__(self):
        return f"Chat {self.id} in Course {self.course_id} by User {self.sender_id}"
    
class ChatResponse(SoftDeleteModel):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name='responses')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_responses')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    auditory = models.CharField(max_length=255)
