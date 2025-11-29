from django.test import TestCase
from assessments import models, serializer
from datetime import date, datetime
from courses.models import Course
from staffs.models import Teacher
from students.models import Student
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.contrib.auth import get_user_model

User = get_user_model()

class AssignmentTest(TestCase):
    def setUp(self):
        self.c1 = Course.objects.create(
            title='Chemistry 101',
            description='Basic concepts in Chemistry.',
            status='d',
        )
        self.u1 = User.objects.create_user(username='TeacherUser', password='teach123')
        self.t1 = Teacher.objects.create(
            user=self.u1,
            first_name='John',
            last_name='Doe',            
            dob=datetime(1984, 1, 1),
            gender='m',
            employee_code='1234',
            experience_years=10,
            contact_number='1234567890', 
            emergency_contact_number='9876543210',
            email_institutional='2GK5V@example.com',
            status='a', 
            date_joined=datetime.now(),
        )
        self.a1 = models.Assignment.objects.create(
            course=self.c1,
            teacher=self.t1,
            title='Chemistry Basics',
            description='Basic concepts of Chemistry.',
            due_date='2023-09-30',
        )

    def test_assignment_serializer(self):
        se = serializer.AssignmentSerializer(self.a1)
        print(se.data)
        self.assertEqual(se.data['title'], 'Chemistry Basics')

    def test_create(self):
        u2 = User.objects.create_user(username='TeacherUser2', password='teach1234')
        t2 = Teacher.objects.create(
            user=u2,
            first_name='Jane',
            last_name='Smith',            
            dob=datetime(1990, 2, 2),
            gender='f',
            employee_code='5678',
            experience_years=5,
            contact_number='2345678901', 
            emergency_contact_number='8765432109',
            email_institutional='HcMl7@example.com',
            status='a', 
            date_joined=datetime.now(),
        )
        c2 = Course.objects.create(
            title='Sociology 101',
            description='Basics of Sociology.',
            status='a',
        )
        data = {
            'course': c2.id,
            'teacher': t2.id,
            'title': 'Sociology Basics',
            'description': 'Basic concepts of Sociology.',
            'due_date': '2023-09-30',
        }
        se = serializer.AssignmentSerializer(data=data)
        print(se.is_valid())
        print(se.errors)
        self.assertTrue(se.is_valid())
        se.save()
        self.assertEqual(models.Assignment.objects.count(), 2)
        print(se.data)

    def test_update(self):
        change = {
            'title': 'Updated Assignment',
        }
        se = serializer.AssignmentSerializer(instance=self.a1, data=change, partial=True)
        print(se.is_valid())
        print(se.errors)
        self.assertTrue(se.is_valid())
        se.save()
        self.a1.refresh_from_db()
        self.assertEqual(self.a1.title, 'Updated Assignment')
        print(se.data)

    def test_listing(self):
        u2 = User.objects.create_user(username='TeacherUser2', password='teach1234')
        u3 = User.objects.create_user(username='TeacherUser3', password='teach1234')
        u4 = User.objects.create_user(username='TeacherUser4', password='teach1234')
        u5 = User.objects.create_user(username='TeacherUser5', password='teach1234')
        t2 = Teacher.objects.create(
            user=u2,
            first_name='Jane',
            last_name='Smith',            
            dob=datetime(1990, 2, 2),
            gender='f',
            employee_code='56078',
            experience_years=5,
            contact_number='2345678901', 
            emergency_contact_number='8765432109',
            email_institutional='HMl7@example.com',
            status='a', 
            date_joined=datetime.now(),
        )
        t3 = Teacher.objects.create(
            user=u3,
            first_name='Jane',
            last_name='Smith',            
            dob=datetime(1990, 2, 2),
            gender='f',
            employee_code='0678',
            experience_years=5,
            contact_number='2345678901', 
            emergency_contact_number='8765432109',
            email_institutional='Hcl7@example.com',
            status='a', 
            date_joined=datetime.now(),
        )
        t4 = Teacher.objects.create(
            user=u4,
            first_name='Jane',
            last_name='Smith',            
            dob=datetime(1990, 2, 2),
            gender='f',
            employee_code='5670',
            experience_years=5,
            contact_number='2345678901', 
            emergency_contact_number='8765432109',
            email_institutional='HcMl7@examle.com',
            status='a', 
            date_joined=datetime.now(),
        )
        t5 = Teacher.objects.create(
            user=u5,
            first_name='Jane',
            last_name='Smith',            
            dob=datetime(1990, 2, 2),
            gender='f',
            employee_code='5078',
            experience_years=5,
            contact_number='2345678901', 
            emergency_contact_number='8765432109',
            email_institutional='HcMl7@exaple.com',
            status='a', 
            date_joined=datetime.now(),
        )

        c2 = Course.objects.create(
            title='Sociology 101',
            description='Basics of Sociology.',
            status='a',
        )
        c3 = Course.objects.create(
            title='Chemistry 101',
            description='Basics of Chemistry.',
            status='a',
        )
        a2 = models.Assignment.objects.create(
            course=c2,
            teacher=t2,
            title='Sociology Basics',
            description='Basic concepts of Sociology.',
            due_date='2023-09-30',
        )
        a3 = models.Assignment.objects.create(
            course=c3,
            teacher=t3,
            title='Chemistry Basics',
            description='Basic concepts of Chemistry.',
            due_date='2023-09-30',
        )
        a4 = models.Assignment.objects.create(
            course=c3,
            teacher=t4,
            title='Chemistry Basics',
            description='Basic concepts of Chemistry.',
            due_date='2023-09-30',
        )
        a5 = models.Assignment.objects.create(
            course=c3,
            teacher=t5,
            title='Chemistry Basics',
            description='Basic concepts of Chemistry.',
            due_date='2023-09-30',
        )
        qs = models.Assignment.objects.all()
        with CaptureQueriesContext(connection=connection) as ctx:
            se = serializer.AssignmentSerializer(qs, many=True)
            print (se.data)
        print(ctx.captured_queries)
        self.assertEqual(len(se.data), 5)

class SubmissionTest(TestCase):
    def setUp(self):
        self.ut1 = User.objects.create_user(
            username='testuser1',
            password='1234',
        )
        self.us1 = User.objects.create_user(
            username='studentuser1',
            password='1234',
        )
        self.t1 = Teacher.objects.create(
            user=self.ut1,
            first_name='John',
            last_name='Doe',            
            dob='1997-01-01',
            gender='m',
            employee_code='1234',
            experience_years=10,
            contact_number='1234567890', 
            emergency_contact_number='9876543210',
            email_institutional='2GK5V@example.com',
            status='a', 
            date_joined=date.today(),
        )
        self.c1 = Course.objects.create(
            title='Philosophy 101',
            description='Introduction to Philosophy.',
            status='d',
        )
        self.a1 = models.Assignment.objects.create(
            course=self.c1,
            teacher=self.t1,
            title='Philosophy Basics',
            description='Basic concepts of Philosophy.',
            due_date='2023-09-30',
        )
        self.s1 = Student.objects.create(
            user=self.us1,
            first_name='Jane',
            last_name='Smith',            
            date_of_birth=date(1990, 2, 2),
            gender='f',
            contact_number='2345678901', 
            emergency_contact_name='John Doe',
            emergency_contact_number='8765432109',
            status='a', 
            date_joined=date.today(),
        )
        self.sub1 = models.Submission.objects.create(
            assignment=self.a1,
            student=self.s1,
            file_url='https://example.com/file.pdf',
            submitted_date='2023-09-30',
            status='s',
        )

    def test_submission_serializer(self):
        se = serializer.SubmissionSerializer(self.sub1)
        print(se.data)

    def test_create(self):
        ut2 = User.objects.create_user(
            username='testuser2',
            password='1234',
        )
        us2 = User.objects.create_user(
            username='studentuser2',
            password='1234',
        )
        t2 = Teacher.objects.create(
            user=ut2,
            first_name='John',
            last_name='Doe',            
            dob='1997-01-01',
            gender='m',
            employee_code='126334',
            experience_years=10,
            contact_number='1234567890', 
            emergency_contact_number='9876543210',
            email_institutional='2GK5@example.com',
            status='a', 
            date_joined=date.today(),
        )
        c2 = Course.objects.create(
            title='Philosophy 101',
            description='Introduction to Philosophy.',
            status='d',
        )
        a2 = models.Assignment.objects.create(
            course=c2,
            teacher=t2,
            title='Philosophy Basics',
            description='Basic concepts of Philosophy.',
            due_date='2023-09-30',
        )
        s2 = Student.objects.create(
            user=us2,
            first_name='Jane',
            last_name='Smith',            
            date_of_birth=date(1990, 2, 2),
            gender='f',
            contact_number='2345678901', 
            emergency_contact_name='John Doe',
            emergency_contact_number='8765432109',
            status='a', 
            date_joined=date.today(),
        )
        data = {
            'assignment': a2.id,
            'student': s2.id,
            'file_url': 'https://example.com/file.pdf',
            'submitted_date': '2023-09-30',
            'status': 's',
        }
        se = serializer.SubmissionSerializer(data=data)
        self.assertTrue(se.is_valid(), se.errors)
        se.save()
        print(se.data)

    def test_update(self):
        change = {
            'status': 'g',
        }
        se = serializer.SubmissionSerializer(self.sub1, data=change, partial=True)
        self.assertTrue(se.is_valid(), se.errors)
        se.save()
        self.sub1.refresh_from_db()
        self.assertEqual(self.sub1.status, 'g')
        print(se.is_valid())
        print(se.errors)
        print(se.data)

    def test_listing(self):
        ut3 = User.objects.create_user(
            username='testteacher3',
            password='1234',
        )
        ut4 = User.objects.create_user(
            username='testteacher4',
            password='1234',
        )
        ut5 = User.objects.create_user(
            username='testteacher5',
            password='1234',
        )
        t3 = Teacher.objects.create(
            user=ut3,
            first_name='John',
            last_name='Doe',            
            dob='1997-01-01',
            gender='m',
            employee_code='1263334',
            experience_years=10,
            contact_number='1234567890', 
            emergency_contact_number='9876543210',
            email_institutional='2GKf5@example.com',
            status='a', 
            date_joined=date.today(),
        )
        t4 = Teacher.objects.create(
            user=ut4,
            first_name='John',
            last_name='Doe',            
            dob='1997-01-01',
            gender='m',
            employee_code='1263234',
            experience_years=10,
            contact_number='1234567890', 
            emergency_contact_number='9876543210',
            email_institutional='2K5@example.com',
            status='a', 
            date_joined=date.today(),
        )
        t5 = Teacher.objects.create(
            user=ut5,
            first_name='John',
            last_name='Doe',            
            dob='1997-01-01',
            gender='m',
            employee_code='126344334',
            experience_years=10,
            contact_number='1234567890', 
            emergency_contact_number='9876543210',
            email_institutional='2G5@example.com',
            status='a', 
            date_joined=date.today(),
        )
        c3 = Course.objects.create(
            title='Philosophy 101',
            description='Introduction to Philosophy.',
            status='d',
        )
        a3 = models.Assignment.objects.create(
            course=c3,
            teacher=t3,
            title='Philosophy Basics',
            description='Basic concepts of Philosophy.',
            due_date='2023-09-30',
        )
        a4 = models.Assignment.objects.create(
            course=c3,
            teacher=t4,
            title='Philosophy Basics',
            description='Basic concepts of Philosophy.',
            due_date='2023-09-30',
        )
        a5 = models.Assignment.objects.create(
            course=c3,
            teacher=t5,
            title='Philosophy Basics',
            description='Basic concepts of Philosophy.',
            due_date='2023-09-30',
        )
        us3 = User.objects.create(
            username='teststudent3',
            password='1234',
        )
        us4 = User.objects.create(
            username='teststudent4',
            password='1234',
        )
        us5 = User.objects.create(
            username='teststudent5',
            password='1234',
        )
        s3 = Student.objects.create(
            user=us3,
            first_name='Jane',
            last_name='Smith',            
            date_of_birth=date(1990, 2, 2),
            gender='f',
            contact_number='2345678901', 
            emergency_contact_name='John Doe',
            emergency_contact_number='8765432109',
            status='a', 
            date_joined=date.today(),
        )
        s4 = Student.objects.create(
            user=us4,
            first_name='Jane',
            last_name='Smith',            
            date_of_birth=date(1990, 2, 2),
            gender='f',
            contact_number='2345678901', 
            emergency_contact_name='John Doe',
            emergency_contact_number='8765432109',
            status='a', 
            date_joined=date.today(),
        )
        s5 = Student.objects.create(
            user=us5,
            first_name='Jane',
            last_name='Smith',            
            date_of_birth=date(1990, 2, 2),
            gender='f',
            contact_number='2345678901', 
            emergency_contact_name='John Doe',
            emergency_contact_number='8765432109',
            status='a', 
            date_joined=date.today(),
        )
        sub3 = models.Submission.objects.create(
            student=s3,
            assignment=a3,
            submitted_date='2023-09-30',
        )
        sub4 = models.Submission.objects.create(
            student=s4,
            assignment=a4,
            submitted_date='2023-09-30',
        )
        sub5 = models.Submission.objects.create(
            student=s5,
            assignment=a5,
            submitted_date='2023-09-30',
        )
        qs = models.Submission.objects.all()
        with CaptureQueriesContext(connection=connection) as ctx:
            se = serializer.SubmissionSerializer(qs, many=True)
            print(se.data)
        print(ctx.captured_queries)
        self.assertLessEqual(len(ctx.captured_queries), 5)
    
class SubmissionGradeTest(TestCase):
    def setUp(self):
        self.ut1 = User.objects.create_user(
            username='testteacher1',
            password='1234',
        )
        self.t1 = Teacher.objects.create(
            user=self.ut1,
            first_name='John',
            last_name='Doe',            
            dob='1997-01-01',
            gender='m',
            employee_code='1263234',
            experience_years=10,
            contact_number='1234567890', 
            emergency_contact_number='9876543210',
            email_institutional='2K5@example.com',
            status='a', 
            date_joined=date.today(),
        )
        self.us1 = User.objects.create_user(
            username='teststudent1',
            password='1234',
        )
        self.s1 = Student.objects.create(
            user=self.us1,
            first_name='Jane',
            last_name='Smith',            
            date_of_birth=date(1990, 2, 2),
            gender='f',
            contact_number='2345678901', 
            emergency_contact_name='John Doe',
            emergency_contact_number='8765432109',
            status='a', 
            date_joined=date.today(),
        )
        self.c1 = Course.objects.create(
            title='Chemistry 101',
            description='Basic concepts in Chemistry.',
            status='d',
        )
        self.a1 = models.Assignment.objects.create(
            course=self.c1,
            teacher=self.t1,
            title='Chemistry Basics',
            description='Basic concepts of Chemistry.',
            due_date='2023-09-30',
        )
        self.sub1 = models.Submission.objects.create(
            student=self.s1,
            assignment=self.a1,
            file_url='https://example.com/file1.pdf',
            submitted_date='2023-09-30',
            status='s',
        )
        self.subgr1 = models.SubmissionGrade.objects.create(
            submission=self.sub1,
            grade=90,
            graded_by=self.t1,
            feedback='Good job!',
        )

    def test_serializer(self):
        se = serializer.SubmissionGradeSerializer(self.subgr1)
        print(se.data)
