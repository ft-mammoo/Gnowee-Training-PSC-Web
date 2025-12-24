from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model
from courses import models
from staffs.models import Teacher
from courses import serializer
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APITestCase
from rest_framework import status

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

class CourseTeachersSerializerTest(TestCase):
    def setUp(self):        
        self.u1 = User.objects.create_user(username='TeacherUser', password='teach123')
        self.t1 = Teacher.objects.create(
            user=self.u1,
            first_name='John',
            last_name='Doe',            
            dob=date(1984, 1, 1),
            gender='m',
            employee_code='1234',
            experience_years=10,
            contact_number='1234567890', 
            emergency_contact_number='9876543210',
            email_institutional='2GK5V@example.com',
            status='a', 
            date_joined=date.today(),
        )
        self.c1 = models.Course.objects.create(
            title='Philosophy 101',
            description='Introduction to Philosophy.',
            status='d',
        )
        self.ct1 = models.CourseTeachers.objects.create(
            course=self.c1,
            teacher=self.t1,
            status='a',
        )
    def test_course_teacher_serializer(self):
        se = serializer.CourseTeacherSerializer(self.ct1)
        print(se.data)
        self.assertEqual(se.data['course'], self.c1.id)
        self.assertEqual(se.data['teacher'], self.t1.id)

    def test_create(self):
        u2 = User.objects.create_user(username='TeacherUser2', password='teach1234')
        t2 = Teacher.objects.create(
            user=u2,
            first_name='Jane',
            last_name='Smith',            
            dob=date(1990, 2, 2),
            gender='f',
            employee_code='5678',
            experience_years=5,
            contact_number='2345678901', 
            emergency_contact_number='8765432109',
            email_institutional='HcMl7@example.com',
            status='a', 
            date_joined=date.today(),
        )
        c2 = models.Course.objects.create(
            title='Sociology 101',
            description='Basics of Sociology.',
            status='a',
        )
        data = {
            'course': c2.id,
            'teacher': t2.id,
            'status': 'a',
        }
        se = serializer.CourseTeacherSerializer(data=data)
        self.assertTrue(se.is_valid(), se.errors)
        course_teacher = se.save()
        self.assertEqual(course_teacher.course.id, c2.id)
        print(se.data)

    def test_update(self):
        change = {
            'status': 'i',
        }
        se = serializer.CourseTeacherSerializer(self.ct1, data = change, partial = True)
        self.assertTrue(se.is_valid(), se.errors)
        course_teacher = se.save()
        self.assertEqual(course_teacher.status, 'i')
        print(se.data)

    def test_listing(self):
        u3 = User.objects.create_user(username='TeacherUser3', password='teach12345')
        u4 = User.objects.create_user(username='TeacherUser4', password='teach123456')
        t3 = Teacher.objects.create(
            user=u3,
            first_name='Alice',
            last_name='Johnson',            
            dob=date(1988, 3, 3),
            gender='f',
            employee_code='6789',
            experience_years=8,
            contact_number='3456789012', 
            emergency_contact_number='7654321098',
            email_institutional='7oE6T@example.com',
            status='a', 
            date_joined=date.today(),
        )
        t4 = Teacher.objects.create(
            user=u4,
            first_name='Bob',
            last_name='Brown',            
            dob=date(1975, 4, 4),
            gender='m',
            employee_code='7890',
            experience_years=15,
            contact_number='4567890123', 
            emergency_contact_number='6543210987',
            email_institutional='q1w2@example.com',
            status='a', 
            date_joined=date.today(),
        )
        c2 = models.Course.objects.create(
            title='Psychology 101',
            description='Basics of Psychology.',
            status='p',
        )
        c3 = models.Course.objects.create(
            title='Economics 101',
            description='Basics of Economics.',
            status='p',
        )
        c4 = models.Course.objects.create(
            title='Political Science 101',
            description='Introduction to Political Science.',
            status='a',
        )
        ct2 = models.CourseTeachers.objects.create(
            course=c3,
            teacher=t3,
            status='a',
        )
        ct3 = models.CourseTeachers.objects.create(
            course=self.c1,
            teacher=t3,
            status='a',
        )
        ct4 = models.CourseTeachers.objects.create(
            course=c4,
            teacher=t4,
            status='a',
        )
        ct5 = models.CourseTeachers.objects.create(
            course=c2,
            teacher=self.t1,
            status='a',
        )
        qs = models.CourseTeachers.objects.all()
        with CaptureQueriesContext(connection=connection) as ctx:
            se = serializer.CourseTeacherSerializer(qs, many=True)
            print(se.data)
        print(ctx.captured_queries)
        self.assertLessEqual(len(ctx.captured_queries), 5)

class MaterialSerializerTest(TestCase):
    def setUp(self):        
        self.u1 = User.objects.create_user(username='MaterialTeacher', password='matteach123')
        self.t1 = Teacher.objects.create(
            user=self.u1,
            first_name='Laura',
            last_name='Wilson',            
            dob=date(1985, 5, 5),
            gender='f',
            employee_code='1234',
            experience_years=10,
            contact_number='1234567890', 
            emergency_contact_number='9876543210',
            email_institutional='2GK5V@example.com',
            status='a', 
            date_joined=date.today(),
        )
        self.c1 = models.Course.objects.create(
            title='Art 101',
            description='Introduction to Art.',
            status='d',
        )
        self.m1 = models.Material.objects.create(
            course=self.c1,
            teacher=self.t1,
            title='Art Basics',
            description='Basic concepts of Art.',
            file_url='http://example.com/art_basics.pdf',
            type='d',
            status='a',
        )

    def test_material_serializer(self):
        se = serializer.MaterialSerializer(self.m1)
        self.assertEqual(se.data['title'], 'Art Basics')
        print(se.data)

    def test_create(self):
        u2 = User.objects.create_user(username='MaterialTeacher2', password='matteach1234')
        t2 = Teacher.objects.create(
            user=u2,
            first_name='Mark',
            last_name='Taylor',            
            dob=date(1992, 6, 6),            
            gender='m',            
            employee_code='5678',
            experience_years=8,
            contact_number='2345678901', 
            emergency_contact_number='8765432109',
            email_institutional='HcMl7@example.com',
            status='a', 
            date_joined=date.today(),
        )
        c2 = models.Course.objects.create(
            title='Music 101',
            description='Introduction to Music.',
            status='a',
        )
        data = {
            'course': c2.id,
            'teacher': t2.id,
            'title': 'Music Basics',
            'description': 'Basic concepts of Music.',
            'file_url': 'http://example.com/music_basics.pdf',
            'type': 'd',
            'status': 'a',
        }
        se = serializer.MaterialSerializer(data=data)
        self.assertTrue(se.is_valid(), se.errors)
        material = se.save()
        self.assertEqual(material.title, 'Music Basics')
        print(se.data)

    def test_update(self):
        change = {
            'title': 'Advanced Art Basics',
            'description': 'Advanced concepts of Art.',
            'status': 'i',
        }
        se = serializer.MaterialSerializer(self.m1, data = change, partial = True)
        self.assertTrue(se.is_valid(), se.errors)
        material = se.save()
        self.assertEqual(material.title, 'Advanced Art Basics')
        print(se.data)

    def test_listing(self):
        u3 = User.objects.create_user(username='MaterialTeacher3', password='matteach12345')
        u4 = User.objects.create_user(username='MaterialTeacher4', password='matteach123456')
        u5 = User.objects.create_user(username='MaterialTeacher5', password='matteach1234567')
        t3 = Teacher.objects.create(
            user=u3,
            first_name='Emma',
            last_name='Davis',            
            dob=date(1987, 7, 7),            
            gender='f',            
            employee_code='6789',
            experience_years=9,
            contact_number='3456789012', 
            emergency_contact_number='7654321098',
            email_institutional='HcMl7@example.com',
            status='a', 
            date_joined=date.today(),
        )
        t4 = Teacher.objects.create(
            user=u4,
            first_name='Liam',
            last_name='Garcia',            
            dob=date(1978, 8, 8),            
            gender='m',            
            employee_code='7890',
            experience_years=7,
            contact_number='4567890123', 
            emergency_contact_number='6543210987',
            email_institutional='HcM7@example.com',
            status='a', 
            date_joined=date.today(),
        )
        t5 = Teacher.objects.create(
            user=u5,
            first_name='Olivia',
            last_name='Martinez',            
            dob=date(1995, 9, 9),            
            gender='f',            
            employee_code='8901',
            experience_years=6,
            contact_number='5678901234', 
            emergency_contact_number='5432109876',
            email_institutional='HcMl@example.com',
            status='a', 
            date_joined=date.today(),
        )
        c3 = models.Course.objects.create(
            title='Drama 101',
            description='Introduction to Drama.',
            status='p',
        )
        c4 = models.Course.objects.create(
            title='Dance 101',
            description='Basics of Dance.',
            status='a',
        )
        c5 = models.Course.objects.create(
            title='Photography 101',
            description='Basics of Photography.',
            status='a',
        )
        m2 = models.Material.objects.create(
            course=c3,
            teacher=t3,
            title='Drama Basics',
            description='Basic concepts of Drama.',
            file_url='http://example.com/drama_basics.pdf',
            type='d',
            status='a',
        )
        m3 = models.Material.objects.create(
            course=self.c1,
            teacher=t3,
            title='Art History',
            description='History of Art.',
            file_url='http://example.com/art_history.pdf',
            type='d',
            status='a',
        )
        m4 = models.Material.objects.create(
            course=c4,
            teacher=t4,
            title='Dance Moves',
            description='Basic Dance Moves.',
            file_url='http://example.com/dance_moves.pdf',
            type='d',
            status='a',
        )
        m5 = models.Material.objects.create(
            course=c5,
            teacher=t5,
            title='Photography Techniques',
            description='Basic Photography Techniques.',
            file_url='http://example.com/photography_techniques.pdf',
            type='d',
            status='a',
        )
        qs = models.Material.objects.all()
        with CaptureQueriesContext(connection=connection) as ctx:
            se = serializer.MaterialSerializer(qs, many=True)
            print(se.data)
        print(ctx.captured_queries)
        self.assertLessEqual(len(ctx.captured_queries), 5)

class CourseViewTest(APITestCase):
    def test_course_crud(self):
        resp = self.client.post("/courses/courses/", {
            "title": "Test Course",
            "description": "This is a test course.",
        }, format='json')
        self.assertTrue(resp.status_code == status.HTTP_201_CREATED)

        resp = self.client.get("/courses/courses/")
        print(resp.data)
        self.assertTrue(resp.status_code == status.HTTP_200_OK)
        self.assertTrue(len(resp.data['results']) == 1)

        resp = self.client.patch("/courses/courses/1/", {
            "description": "Updated description.",
        }, format='json')
        resp = self.client.get("/courses/courses/1/")
        print(resp.data)
        self.assertTrue(resp.data['description'] == "Updated description.")
        self.assertTrue(resp.status_code == status.HTTP_200_OK)

        resp = self.client.delete("/courses/courses/1/")
        self.assertTrue(resp.status_code == status.HTTP_204_NO_CONTENT)
        

