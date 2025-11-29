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

class ChatResponseTest(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(
            username='testuser1',
            password='1234',
        )
        self.c1 = Course.objects.create(
            title ='Test Course',
            description='Test Description',
            status='d',
        )
        self.chat1 = models.Chat.objects.create(
            course=self.c1,
            sender=self.u1,
            message='Hello, this is a test message.',
            auditory='General',
        )
        self.chat_response1 = models.ChatResponse.objects.create(
            course=self.c1,
            chat=self.chat1,
            sender=self.u1,
            message='This is a response to the chat message.',
            auditory='General',
        )

    def test_chat_response_serializer(self):
        se = serializer.chatResponseSerializer(self.chat_response1)
        print(se.data)
        self.assertEqual(se.data['message'], 'This is a response to the chat message.')
        self.assertEqual(se.data['chat'], self.chat1.id)

    def test_create(self):
        u2 = User.objects.create_user(
            username='testuser2',
            password='1234',
        )
        c2 = Course.objects.create(
            title ='Another Test Course',
            description='Another Test Description',
            status='d',
        )
        chat2 = models.Chat.objects.create(
            course=c2,
            sender=u2,
            message='Another chat message.',
            auditory='General',
        )
        data = {
            'course': c2.id,
            'chat': chat2.id,
            'sender': u2.id,
            'message': 'Response to another chat message.',
            'auditory': 'General',
        }
        se = serializer.chatResponseSerializer(data=data)
        print(se.is_valid())
        print(se.errors)
        self.assertTrue(se.is_valid())
        se.save()
        self.assertEqual(models.ChatResponse.objects.count(), 2)
        print(models.ChatResponse.objects.last().message)
        print(se.data)

    def test_update(self):
        data = {
            'message': 'Updated response message.',
        }
        se = serializer.chatResponseSerializer(instance=self.chat_response1, data=data, partial=True)
        print(se.is_valid())
        print(se.errors)
        self.assertTrue(se.is_valid())
        se.save()
        self.chat_response1.refresh_from_db()
        self.assertEqual(self.chat_response1.message, 'Updated response message.')
        print(se.data)

    def test_listing(self):
        u2 = User.objects.create_user(
            username='testuser2',
            password='1234',
        )
        u3 = User.objects.create_user(
            username='testuser3',
            password='1234',
        )
        u4 = User.objects.create_user(
            username='testuser4',
            password='1234',
        )
        u5 = User.objects.create_user(
            username='testuser5',
            password='1234',
        )
        c2 = Course.objects.create(
            title ='Another Test Course',
            description='Another Test Description',
            status='d',
        )
        c3 = Course.objects.create(
            title ='Third Test Course',
            description='Third Test Description',
            status='d',
        )
        c4 = Course.objects.create(
            title ='Fourth Test Course',
            description='Fourth Test Description',
            status='d',
        )
        c5 = Course.objects.create(
            title ='Fifth Test Course',
            description='Fifth Test Description',
            status='d',
        )
        chat2 = models.Chat.objects.create(
            course=c2,
            sender=u2,
            message='Another chat message.',
            auditory='General',
        )
        chat3 = models.Chat.objects.create(
            course=c3,
            sender=u3,
            message='Third chat message.',
            auditory='General',
        )
        chat4 = models.Chat.objects.create(
            course=c4,
            sender=u4,
            message='Fourth chat message.',
            auditory='General',
        )
        chat5 = models.Chat.objects.create(
            course=c5,
            sender=u5,
            message='Fifth chat message.',
            auditory='General',
        )
        cr2 = models.ChatResponse.objects.create(
            course=c2,
            chat=chat2,
            sender=u2,
            message='Response to another chat message.',
            auditory='General',
        )
        cr3 = models.ChatResponse.objects.create(
            course=c3,
            chat=chat3,
            sender=u3,
            message='Response to third chat message.',
            auditory='General',
        )
        cr4 = models.ChatResponse.objects.create(
            course=c4,
            chat=chat4,
            sender=u4,
            message='Response to fourth chat message.',
            auditory='General',
        )
        cr5 = models.ChatResponse.objects.create(
            course=c5,
            chat=chat5,
            sender=u5,
            message='Response to fifth chat message.',
            auditory='General',
        )

        qs = models.ChatResponse.objects.all()
        with CaptureQueriesContext(connection) as ctx:
            se = serializer.chatResponseSerializer(qs, many=True)
            print(se.data)
        print(ctx.captured_queries)
