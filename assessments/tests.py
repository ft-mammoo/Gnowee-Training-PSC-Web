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

    def test_update(self):
        change = {
            'grade': 100,
        }
        se = serializer.SubmissionGradeSerializer(self.subgr1, data=change, partial=True)
        print(se.is_valid())
        print(se.errors)
        self.assertTrue(se.is_valid())
        se.save()
        self.subgr1.refresh_from_db()
        self.assertEqual(self.subgr1.grade, 100)
        print(se.data)

    def test_list(self):
        ut2 = User.objects.create_user(
            username='testteacher2',
            password='1234',
        )
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
        t2 = Teacher.objects.create(
            user=ut2,
            first_name='Johen',
            last_name='Doe',            
            dob='1997-01-01',
            gender='m',
            employee_code='32442',
            experience_years=10,
            contact_number='1234567890', 
            emergency_contact_number='9876543210',
            email_institutional='2Ksfd5@example.com',
            status='a', 
            date_joined=date.today(),
        )
        t3 = Teacher.objects.create(
            user=ut3,
            first_name='Joqhn',
            last_name='Doe',            
            dob='1997-01-01',
            gender='m',
            employee_code='54543',
            experience_years=10,
            contact_number='1234567890', 
            emergency_contact_number='9876543210',
            email_institutional='2Kew5@example.com',
            status='a', 
            date_joined=date.today(),
        )
        t4 = Teacher.objects.create(
            user=ut4,
            first_name='Joehne',
            last_name='Docde',            
            dob='1997-01-01',
            gender='m',
            employee_code='efcdsd',
            experience_years=10,
            contact_number='1234567890', 
            emergency_contact_number='9876543210',
            email_institutional='2Kdcew5@example.com',
            status='a', 
            date_joined=date.today(),
        )
        t5 = Teacher.objects.create(
            user=ut5,
            first_name='Joqehne',
            last_name='Dode',            
            dob='1997-01-01',
            gender='f',
            employee_code='efcdcd',
            experience_years=10,
            contact_number='1234567890', 
            emergency_contact_number='9876543210',
            email_institutional='2Kzcdcew5@example.com',
            status='a', 
            date_joined=date.today(),
        )
        c2 = Course.objects.create(
            title='Chemistry 101',
            description='Basic concepts in Chemistry.',
            status='d',
        )
        c3 = Course.objects.create(
            title='Mathematics 101',
            description='Basic concepts in Mathematics.',
            status='d',
        )
        c4 = Course.objects.create(
            title='Physics 101',
            description='Basic concepts in Physics.',
            status='d',
        )
        c5 = Course.objects.create(
            title='Biology 101',
            description='Basic concepts in Biology.',
            status='d',
        )
        a2 = models.Assignment.objects.create(
            course=c2,
            teacher=t2,
            title='Chemistry Basics',
            description='Basic concepts of Chemistry.',
            due_date='2023-09-30',
        )
        a3 = models.Assignment.objects.create(
            course=c3,
            teacher=t3,
            title='Mathematics Basics',
            description='Basic concepts of Mathematics.',
            due_date='2023-09-30',
        )
        a4 = models.Assignment.objects.create(
            course=c4,
            teacher=t4,
            title='Physics Basics',
            description='Basic concepts of Physics.',
            due_date='2023-09-30',
        )
        a5 = models.Assignment.objects.create(
            course=c5,
            teacher=t5,
            title='Biology Basics',
            description='Basic concepts of Biology.',
            due_date='2023-09-30',
        )
        us2 = User.objects.create_user(
            username='teststudent2',
            password='1234',
        )
        us3 = User.objects.create_user(
            username='teststudent3',
            password='1234',
        )
        us4 = User.objects.create_user(
            username='teststudent4',
            password='1234',
        )
        us5 = User.objects.create_user(
            username='teststudent5',
            password='1234',
        )
        s2 = Student.objects.create(
            user = us2,
            first_name = 'Bibi',
            last_name = 'Nun',
            date_of_birth = '2000-01-01',
            gender = 'f',
            contact_number = '1234567890',
            emergency_contact_name = 'Jane Doe',  
            emergency_contact_number = '9876543210',
            status = 'a', 
            date_joined = date.today(),
        )
        s3 = Student.objects.create(
            user = us3,
            first_name = 'Alina',
            last_name = 'Becker',
            date_of_birth = '1996-01-01',
            gender = 'f',
            contact_number = '1234567890',
            emergency_contact_name = 'Alison Becker',  
            emergency_contact_number = '9876543210',
            status = 'a', 
            date_joined = date.today(),
        )
        s4 = Student.objects.create(
            user = us4,
            first_name = 'Alison',
            last_name = 'Becker',
            date_of_birth = '1996-01-01',
            gender = 'm',
            contact_number = '1234567890',
            emergency_contact_name = 'Alina Becker',  
            emergency_contact_number = '9876543210',
            status = 'a', 
            date_joined = date.today(),
        )
        s5 = Student.objects.create(
            user = us5,
            first_name = 'Lionel',
            last_name = 'Messi',
            date_of_birth = '1996-01-01',
            gender = 'f',
            contact_number = '1234567890',
            emergency_contact_name = 'Cristiano Ronaldo',  
            emergency_contact_number = '9876543210',
            status = 'a', 
            date_joined = date.today(),
        )
        sb2 = models.Submission.objects.create(
            assignment=a2,
            student=s2,
            submitted_date='2023-09-30',
            status='a',
        )
        sb3 = models.Submission.objects.create(
            assignment=a3,
            student=s3,
            submitted_date='2023-09-30',
            status='a',
        )
        sb4 = models.Submission.objects.create(
            assignment=a4,
            student=s4,
            submitted_date='2023-09-30',
            status='a',
        )
        sb5 = models.Submission.objects.create(
            assignment=a5,
            student=s5,
            submitted_date='2023-09-30',
            status='a',
        )
        sg2 = models.SubmissionGrade.objects.create(
            submission=sb2,
            grade=90,
            graded_by=t2,
            feedback='Good job!',
        )
        sg3 = models.SubmissionGrade.objects.create(
            submission=sb3,
            grade=80,
            graded_by=t3,
            feedback='Good job!',
        )
        sg4 = models.SubmissionGrade.objects.create(
            submission=sb4,
            grade=70,
            graded_by=t4,
            feedback='Good job!',
        )
        sg5 = models.SubmissionGrade.objects.create(
            submission=sb5,
            grade=60,
            graded_by=t5,
            feedback='Good job!',
        )
        qs = models.SubmissionGrade.objects.all()
        with CaptureQueriesContext(connection=connection) as ctx:
            se = serializer.SubmissionGradeSerializer(qs, many=True)
            print(se.data)
        print(ctx.captured_queries)
        self.assertLessEqual(len(ctx.captured_queries), 1)

class QuestionCategoriesTest(TestCase):
    def setUp(self):
        self.qc1 = models.QuestionCategories.objects.create(
            name='Mathematics',
            description='Questions related to Mathematics.',
        )
    def test_serializer(self):
        se = serializer.QuestionCategoriesSerializer(self.qc1)
        print(se.data)
    def test_create(self):
        data = {
            'name': 'Physics',
            'description': 'Questions related to Physics.',
        }
        se = serializer.QuestionCategoriesSerializer(data=data)
        self.assertTrue(se.is_valid(), se.errors)
        qc = se.save()
        self.assertEqual(qc.name, 'Physics')
        print(se.data)
    def test_update(self):
        change = {
            'name': 'Chemistry',
            'description': 'Questions related to Chemistry.',
        }
        se = serializer.QuestionCategoriesSerializer(self.qc1, data = change, partial = True)
        self.assertTrue(se.is_valid(), se.errors)
        qc = se.save()
        self.assertEqual(qc.name, 'Chemistry')
        print(se.data)
    def test_listing(self):
        qc2 = models.QuestionCategories.objects.create(
            name='Physics',
            description='Questions related to Physics.',
        )
        qc3 = models.QuestionCategories.objects.create(
            name='Chemistry',
            description='Questions related to Chemistry.',
        )
        qc4 = models.QuestionCategories.objects.create(
            name='Biology',
            description='Questions related to Biology.',
        )
        qc5 = models.QuestionCategories.objects.create(
            name='Geography',
            description='Questions related to Geography.',
        )
        qs = models.QuestionCategories.objects.all()
        with CaptureQueriesContext(connection=connection) as ctx:
            se = serializer.QuestionCategoriesSerializer(qs, many=True)
            print(se.data)
        print(ctx.captured_queries)
        self.assertLessEqual(len(ctx.captured_queries), 1)

class ExamsTest(TestCase):
    def setUp(self):
        self.c1 = Course.objects.create(
            title = 'Mathematics',
            description = 'Mathematics course',
            status = 'a',
        )
        self.ex1 = models.Exams.objects.create(
            course = self.c1,
            title = 'Mathematics Exam',
            description = 'Mathematics Exam',
            start_time = '2023-09-30 09:00',
            end_time = '2023-09-30 11:00',
            total_marks = 100,
        )
    def test_serializer(self):
        se = serializer.ExamsSerializer(self.ex1)
        print(se.data)
    def test_create(self):
        data = {
            'course': self.c1.id,
            'title': 'Physics Exam',
            'description': 'Physics Exam',
            'start_time': '2023-09-30 09:00',
            'end_time': '2023-09-30 11:00',
            'total_marks': 100,
        }
        se = serializer.ExamsSerializer(data=data)
        self.assertTrue(se.is_valid(), se.errors)
        ex = se.save()
        self.assertEqual(ex.title, 'Physics Exam')
        print(se.data)
    def test_update(self):
        change = {
            'title': 'Chemistry Exam',
            'description': 'Chemistry Exam',
        }
        se = serializer.ExamsSerializer(self.ex1, data = change, partial = True)
        self.assertTrue(se.is_valid(), se.errors)
        ex = se.save()
        self.assertEqual(ex.title, 'Chemistry Exam')
        print(se.data)
    def test_listing(self):
        c2 = Course.objects.create(
            title = 'Physics',
            description = 'Physics course',
            status = 'a',
        )
        c3 = Course.objects.create(
            title = 'Chemistry',
            description = 'Chemistry course',
            status = 'a',
        )
        c4 = Course.objects.create(
            title = 'Biology',
            description = 'Biology course',
            status = 'a',
        )
        c5 = Course.objects.create(
            title = 'Geography',
            description = 'Geography course',
            status = 'a',
        )
        ex2 = models.Exams.objects.create(
            course = c2,
            title = 'Physics Exam',
            description = 'Physics Exam',
            start_time = '2023-09-30 09:00',
            end_time = '2023-09-30 11:00',
            total_marks = 100,
        )
        ex3 = models.Exams.objects.create(
            course = c3,
            title = 'Chemistry Exam',
            description = 'Chemistry Exam',
            start_time = '2023-09-30 09:00',
            end_time = '2023-09-30 11:00',
            total_marks = 100,
        )
        ex4 = models.Exams.objects.create(
            course = c4,
            title = 'Biology Exam',
            description = 'Biology Exam',
            start_time = '2023-09-29 09:00',
            end_time = '2023-09-29 11:00',
            total_marks = 100,
        )
        ex5 = models.Exams.objects.create(
            course = c5,
            title = 'Geography Exam',
            description = 'Geography Exam',
            start_time = '2023-10-31 09:00',
            end_time = '2023-10-31 11:00',
            total_marks = 100,
        )
        qs = models.Exams.objects.all()
        with CaptureQueriesContext(connection=connection) as ctx:
            se = serializer.ExamsSerializer(qs, many=True)
            print(se.data)
        print(ctx.captured_queries)
        self.assertLessEqual(len(ctx.captured_queries), 1)

class ExamsQuestionsTest(TestCase):
    def setUp(self):
        self.qc1 = models.QuestionCategories.objects.create(
            name = 'Mathematics',
            description = 'Questions related to Mathematics.',
        )
        self.eq1 = models.ExamQuestions.objects.create(
            category = self.qc1,
            question_text = 'What is 2 + 2?',
            question_type = 's',
            marks = 1, 
        )
    def test_serializer(self):
        se = serializer.ExamQuestionsSerializer(self.eq1)
        print(se.data)
    def test_create(self):
        qc2 = models.QuestionCategories.objects.create(
            name = 'Chemistry',
            description = 'Questions related to Chemistry.',
        )
        data = {
            'category': qc2.id,
            'question_text': 'What is the boiling point of water?',
            'question_type': 's',
            'marks': 3,
        }
        se = serializer.ExamQuestionsSerializer(data=data)
        self.assertTrue(se.is_valid(), se.errors)
        se.save()
        print(se.data)
    def test_update(self):
        change = {
            'question_text': 'What is 4+4?',            
        }
        se = serializer.ExamQuestionsSerializer(self.eq1, data = change, partial = True)
        self.assertTrue(se.is_valid(), se.errors)
        se.save()
        print(se.data)

    def test_listing(self):
        qc2 = models.QuestionCategories.objects.create(
            name = 'General Knowledge',
            description = 'Questions related to General Knowledge.',
        )
        eq2 = models.ExamQuestions.objects.create(
            category = qc2,
            question_text = 'What is the boiling point of water?',
            question_type = 's',
            marks = 3,
        )
        eq3 = models.ExamQuestions.objects.create(
            category = qc2,
            question_text = 'What is the boiling point of Gold?',
            question_type = 's',
            marks = 3,
        )
        eq4 = models.ExamQuestions.objects.create(
            category = qc2,
            question_text = 'What is the boiling point of Silver?',
            question_type = 's',
            marks = 3,
        )
        eq5 = models.ExamQuestions.objects.create(
            category = qc2,
            question_text = 'What is the boiling point of Iron?',
            question_type = 's',
            marks = 3,
        )
        qs = models.ExamQuestions.objects.all()
        with CaptureQueriesContext(connection=connection) as ctx:
            se = serializer.ExamQuestionsSerializer(qs, many=True)
            print(se.data)
        print(ctx.captured_queries)
        self.assertLessEqual(len(ctx.captured_queries), 1)
        self.assertEqual(len(se.data), 5)

class QuestionOptionsTest(TestCase):
    def setUp(self):
        self.qc1 = models.QuestionCategories.objects.create(
            name = 'Mathematics',
            description = 'Questions related to Mathematics.',
        )
        self.q1 = models.ExamQuestions.objects.create(
            category = self.qc1,
            question_text = 'What is 2 + 2?',
            question_type = 's',
            marks = 1, 
        )
        self.qo1 = models.QuestionOptions.objects.create(
            question = self.q1,
            option_code = 'A',
            option_text = '4',
            is_correct = True,
        )
    def test_serializer(self):
        se = serializer.QuestionOptionsSerializer(self.qo1)
        print(se.data)
    def test_create(self):
        data = {
            'question': self.q1.id,
            'option_code': 'B',
            'option_text': '2',
            'is_correct': False,
        }
        se = serializer.QuestionOptionsSerializer(data=data)
        self.assertTrue(se.is_valid(), se.errors)
        se.save()
        print(se.data)
    def test_update(self):
        change = {
            'option_text': '3',
            'is_correct': False,            
        }
        se = serializer.QuestionOptionsSerializer(self.qo1, data = change, partial = True)
        self.assertTrue(se.is_valid(), se.errors)
        se.save()
        print(se.data)
    def test_listing(self):
        q2 = models.ExamQuestions.objects.create(
            category = self.qc1,
            question_text = 'What is 4 + 4?',
            question_type = 's',
            marks = 1, 
        )
        qo2 = models.QuestionOptions.objects.create(
            question = q2,
            option_code = 'A',
            option_text = '8',
            is_correct = True,
        )
        qo3 = models.QuestionOptions.objects.create(
            question = q2,
            option_code = 'B',
            option_text = '4',
            is_correct = False,
        )
        qo4 = models.QuestionOptions.objects.create(
            question = q2,
            option_code = 'C',
            option_text = '2',
            is_correct = False,
        )
        qo5 = models.QuestionOptions.objects.create(
            question = q2,
            option_code = 'D',
            option_text = '6',
            is_correct = False,
        )
        qs = models.QuestionOptions.objects.all()
        with CaptureQueriesContext(connection=connection) as ctx:
            se = serializer.QuestionOptionsSerializer(qs, many=True)
            print(se.data)
        print(ctx.captured_queries)
        self.assertLessEqual(len(ctx.captured_queries), 1)
        self.assertEqual(len(se.data), 5)
