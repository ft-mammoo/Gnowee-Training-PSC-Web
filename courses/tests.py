from django.test import TestCase
from django.contrib.auth import get_user_model
from courses import models
from courses import serializer
from django.db import connection
from django.test.utils import CaptureQueriesContext

User = get_user_model()

class CourseTest(TestCase):
    def setUp(self):
        # Create a test admin
        self.admin = User.objects.create_user(username='TestAdmin', password='1234')
    
    def test_signal(self):
        c1 = models.Course.objects.create(
            title='Physics 101',
            description='',
            status='d',
            created_by=self.admin,
            updated_by=self.admin
        )
        # Verify that the description was updated by the pre-save signal
        self.assertEqual(c1.description, "Signal Description Update")

        # Update the course to trigger post-save signal for update
        c1.title = 'Advanced Physics 101'
        c1.description = 'Advanced concepts in Physics.'
        c1.save()

class CourseSerializerTest(TestCase):
    def setUp(self):        
        self.c1 = models.Course.objects.create(
            title='Chemistry 101',
            description='Basic concepts in Chemistry.',
            status='d',
        )
    def test_course_serializer(self):
        se = serializer.CourseSerializer(self.c1)
        print(se.data)
        self.assertEqual(se.data['title'], 'Chemistry 101')

    def test_create(self):
        data = {
            'title': 'Biology 101',
            'description': 'Introduction to Biology.',
            'status': 'd',
        }
        se = serializer.CourseSerializer(data=data)
        self.assertTrue(se.is_valid(), se.errors)
        course = se.save()
        self.assertEqual(course.title, 'Biology 101')
        print(se.data)

    def test_update(self):
        change = {
            'title': 'Chemistry 102',
            'description': 'Updated concepts in Chemistry.',
            'status': 'p',
        }
        se = serializer.CourseSerializer(self.c1, data = change, partial = True)
        self.assertTrue(se.is_valid(), se.errors)
        course = se.save()
        self.assertEqual(course.title, 'Chemistry 102')
        print(se.data)

    def test_listing(self):
        c2 = models.Course.objects.create(
            title='Mathematics 101',
            description='Basic concepts in Mathematics.',
            status='d',
        )
        c3 = models.Course.objects.create(
            title='History 101',
            description='World History Overview.',
            status='d',
        )
        c4 = models.Course.objects.create(
            title='Geography 101',
            description='Introduction to Geography.',
            status='d',
        )
        c5 = models.Course.objects.create(
            title='English 101',
            description='Basic English Language Skills.',
            status='d',
        )

        qs = models.Course.objects.all()
        with CaptureQueriesContext(connection=connection) as ctx:
            se = serializer.CourseSerializer(qs, many=True)
            print(se.data)
        print(ctx.captured_queries)
        self.assertLessEqual(len(ctx.captured_queries), 5) 
               
