from django.test import TestCase
from communication import models, serializer
from courses.models import Course
from datetime import date
from django.contrib.auth import get_user_model
from django.test.utils import CaptureQueriesContext
from django.db import connection

User = get_user_model()

class ChatTest(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(
            username='testuser1',
            password='1234',
        )
        self.c1 = Course.objects.create(
            title ='Test Course',
            description='Test Description',
        )
        self.chat1 = models.Chat.objects.create(
            course=self.c1,
            sender=self.u1,
            message='Hello, this is a test message.',
            auditory='General',
        )

    def test_chat_serializer(self):
        se = serializer.chatSerializer(self.chat1)
        print(se.data)
        self.assertEqual(se.data['message'], 'Hello, this is a test message.')
