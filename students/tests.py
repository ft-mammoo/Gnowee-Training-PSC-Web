from django.db import connection
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.test.utils import CaptureQueriesContext
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta

from students.models import Student, Enrollment
from courses.models import Course
from staffs.models import Teacher
from assessments.models import Assignment, Submission, SubmissionGrade, Exams, ExamSubmissions, ExamReviews
from students.serializer import (
    StudentAndCourseNestedSerializer, 
    StudentModelSerializer, 
    StudentNestedSerializer, 
    StudentEnrollmentModelSerializer
)

User = get_user_model()


class ModelStudentSerializerTestCase(TestCase):
    def setUp(self):
        student_user = User.objects.create(
            username='student1', 
            password='password'
        )
        self.student_1 = Student.objects.create(
            user=student_user,
            first_name='John',
            last_name='Doe',
            date_of_birth=date(2000, 1, 1),
            gender='m',
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )
    
    def test_serializer(self):
        se = StudentModelSerializer(self.student_1)
        #print(se.data)
        self.assertEqual(se.data['first_name'], 'John')

    def test_serializer_create(self):
        student_user = User.objects.create_user(
            username='john', 
            password='password'
        )
        data = {
            'user': student_user.id,
            'first_name': 'Alice',
            'last_name': 'Smith',
            'date_of_birth': '1999-05-15',
            'gender': 'f',
            'contact_number': '9876543210',
            'emergency_contact_name': 'Bob Smith',
            'emergency_contact_number': '1234567890',
            'status': 'a',
            'date_joined': '2022-01-01',
        }
        se = StudentModelSerializer(data=data)
        print(se.is_valid())
        print(se.errors)
        self.assertTrue(se.is_valid())
        se.save()
        self.assertEqual(Student.objects.count(), 2)
    
    def test_serializer_update(self):
        change = {
            'first_name': 'Johnny',
        }
        se = StudentModelSerializer(self.student_1, data=change, partial=True)
        self.assertTrue(se.is_valid())
        se.save()
        self.student_1.refresh_from_db()
        self.assertEqual(self.student_1.first_name, 'Johnny')

    def test_listing(self):
        u2 = User.objects.create_user(
            username='student2', 
            password='password'
        )
        u3 = User.objects.create_user(
            username='student3', 
            password='password'
        )
        u4 = User.objects.create_user(    
            username='student4',
            password='password'
        )
        u5 = User.objects.create_user(    
            username='student5',
            password='password'
        )

        s2 = Student.objects.create(
            user=u2,
            first_name='Emily',
            last_name='Clark',
            date_of_birth=date(2001, 2, 2),
            gender='f',
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )
        s3 = Student.objects.create(
            user=u3,
            first_name='Michael',
            last_name='Brown',
            date_of_birth=date(2002, 3, 3),
            gender='m',
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )
        s4 = Student.objects.create(
            user=u4,
            first_name='Sarah',
            last_name='Davis',
            date_of_birth=date(2003, 4, 4),
            gender='f',
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )
        s5 = Student.objects.create(
            user=u5,
            first_name='David',
            last_name='Wilson',
            date_of_birth=date(2004, 5, 5), 
            gender='m',
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )

        qs = Student.objects.all()
        se = StudentModelSerializer(qs, many=True)
        print(se.data)
        self.assertEqual(len(se.data), 5)

class NestedSerializerTest(TestCase):
    def setUp(self):
        student_user = User.objects.create(
            username='John', 
            password='password'
        )
        self.student_1 = Student.objects.create(
            user=student_user,
            first_name='John',
            last_name='Doe',
            date_of_birth=date(2000, 1, 1),
            gender='m',
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )
    
    def test_serializer(self):
        se = StudentNestedSerializer(self.student_1)
        print(se.data)
        self.assertEqual(se.data['first_name'], 'John')

    def test_serializer_create(self):
        data = {
            'user': {'username': 'Alice'},
            'first_name': 'Alice',
            'last_name': 'Smith',
            'date_of_birth': '1999-05-15',
            'gender': 'f',
            'contact_number': '9876543210',
            'emergency_contact_name': 'Bob Smith',
            'emergency_contact_number': '1234567890',
            'status': 'a',
            'date_joined': '2022-01-01',
        }
        se = StudentNestedSerializer(data=data)
        print(se.is_valid())
        print(se.errors)
        self.assertTrue(se.is_valid())
        se.save()
        self.assertEqual(Student.objects.count(), 2)
    
    def test_serializer_update(self):
        change = {
            'first_name': 'Johnny',
        }
        se = StudentNestedSerializer(self.student_1, data=change, partial=True)
        self.assertTrue(se.is_valid())
        se.save()
        self.student_1.refresh_from_db()
        self.assertEqual(self.student_1.first_name, 'Johnny')

    def test_listing(self):
        u2 = User.objects.create_user(
            username='student2', 
            password='password'
        )
        u3 = User.objects.create_user(
            username='student3', 
            password='password'
        )
        u4 = User.objects.create_user(    
            username='student4',
            password='password'
        )
        u5 = User.objects.create_user(    
            username='student5',
            password='password'
        )

        s2 = Student.objects.create(
            user=u2,
            first_name='Emily',
            last_name='Clark',
            date_of_birth=date(2001, 2, 2),
            gender='f',
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )
        s3 = Student.objects.create(
            user=u3,
            first_name='Michael',
            last_name='Brown',
            date_of_birth=date(2002, 3, 3),
            gender='m',
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )
        s4 = Student.objects.create(
            user=u4,
            first_name='Sarah',
            last_name='Davis',
            date_of_birth=date(2003, 4, 4),
            gender='f',
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )
        s5 = Student.objects.create(
            user=u5,
            first_name='David',
            last_name='Wilson',
            date_of_birth=date(2004, 5, 5), 
            gender='m',
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )

        qs = Student.objects.all().select_related('user')
        with CaptureQueriesContext(connection=connection) as ctx:
            se = StudentNestedSerializer(qs, many=True)
            print(se.data)
        print(ctx.captured_queries)
        self.assertEqual(len(se.data), 5)

class StudentAndCourseNestedSerializerTestCase(TestCase):
    def setUp(self):
        student_user = User.objects.create(
            username='John', 
            password='password'
        )
        self.student_1 = Student.objects.create(
            user=student_user,
            first_name='John',
            last_name='Doe',
            date_of_birth=date(2000, 1, 1),
            gender='m',
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )
    
    def test_serializer(self):
        se = StudentAndCourseNestedSerializer(self.student_1)
        print(se.data)
        self.assertEqual(se.data['first_name'], 'John')

    def test_serializer_create(self):
        data = {
            'user': {'username': 'Alice'},
            'first_name': 'Alice',
            'last_name': 'Smith',
            'date_of_birth': '1999-05-15',
            'gender': 'f',
            'contact_number': '9876543210',
            'emergency_contact_name': 'Bob Smith',
            'emergency_contact_number': '1234567890',
            'status': 'a',
            'date_joined': '2022-01-01',
        }
        se = StudentAndCourseNestedSerializer(data=data)
        print(se.is_valid())
        print(se.errors)
        self.assertTrue(se.is_valid())
        se.save()
        self.assertEqual(Student.objects.count(), 2)
    
    def test_serializer_update(self):
        change = {
            'first_name': 'Johnny',
        }
        se = StudentAndCourseNestedSerializer(self.student_1, data=change, partial=True)
        self.assertTrue(se.is_valid())
        se.save()
        self.student_1.refresh_from_db()
        self.assertEqual(self.student_1.first_name, 'Johnny')

    def test_listing(self):
        u2 = User.objects.create_user(
            username='student2', 
            password='password'
        )
        u3 = User.objects.create_user(
            username='student3', 
            password='password'
        )
        u4 = User.objects.create_user(    
            username='student4',
            password='password'
        )
        u5 = User.objects.create_user(    
            username='student5',
            password='password'
        )

        s2 = Student.objects.create(
            user=u2,
            first_name='Emily',
            last_name='Clark',
            date_of_birth=date(2001, 2, 2),
            gender='f',
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )
        s3 = Student.objects.create(
            user=u3,
            first_name='Michael',
            last_name='Brown',
            date_of_birth=date(2002, 3, 3),
            gender='m',
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )
        s4 = Student.objects.create(
            user=u4,
            first_name='Sarah',
            last_name='Davis',
            date_of_birth=date(2003, 4, 4),
            gender='f',
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )
        s5 = Student.objects.create(
            user=u5,
            first_name='David',
            last_name='Wilson',
            date_of_birth=date(2004, 5, 5), 
            gender='m',
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )

        qs = Student.objects.all().select_related('user').prefetch_related('courses')
        with CaptureQueriesContext(connection=connection) as ctx:
            se = StudentAndCourseNestedSerializer(qs, many=True)
            print(se.data)
        print(ctx.captured_queries)
        self.assertEqual(len(se.data), 5)

class StudentEnrollmentModelSerializerTestCase(TestCase):
    def setUp(self):
        u1 = User.objects.create_user(
            username='student1',
            password='password'
        )
        self.s1 = Student.objects.create(
            user=u1,
            first_name='John',
            last_name='Doe',
            date_of_birth=date(2000, 1, 1),
            gender='m',
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )
        self.c1 = Course.objects.create(
            title='Math 101',
            description='Basic Mathematics',
            status='p'
        )
        self.e1 = Enrollment.objects.create(
            student=self.s1,
            course=self.c1,
            status='a'
        )
        
    def test_serializer(self):
        se = StudentEnrollmentModelSerializer(self.e1)
        print(se.data)
        self.assertEqual(se.data['student'], self.s1.id)
        self.assertEqual(se.data['course'], self.c1.id)

    def test_serializer_create(self):
        u2 = User.objects.create_user(
            username='student2',
            password='password'
        )
        s2 = Student.objects.create(
            user=u2,
            first_name='Emily',
            last_name='Clark',
            date_of_birth=date(2001, 2, 2),
            gender='f',
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )
        
        c2 = Course.objects.create(
            title='Art 101',
            description='Basic Art',
            status='a'
        )
        data = {
            'student': s2.id,
            'course': c2.id,
            'status': 'a'
        }
        
        se = StudentEnrollmentModelSerializer(data=data)
        print(se.is_valid())
        print(se.errors)
        self.assertTrue(se.is_valid(), se.errors)
        se.save()
        self.assertEqual(Enrollment.objects.count(), 2)

    def test_serializer_update(self):
        change = {
            'status': 'c',
        }
        se = StudentEnrollmentModelSerializer(self.e1, data=change, partial=True)
        self.assertTrue(se.is_valid())
        se.save()
        self.e1.refresh_from_db()
        self.assertEqual(self.e1.status, 'c')

    def test_listing(self):
        u2 = User.objects.create_user(
            username='student2',
            password='password'
        )
        u3 = User.objects.create_user(
            username='student3',
            password='password'
        )
        u4 = User.objects.create_user(    
            username='student4',
            password='password'
        )
        u5 = User.objects.create_user(    
            username='student5',
            password='password'
        )
        s2 = Student.objects.create(
            user=u2,
            first_name='Emily',
            last_name='Clark',
            date_of_birth=date(2001, 2, 2),
            gender='f',
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )
        s3 = Student.objects.create(
            user=u3,
            first_name='Michael',
            last_name='Brown',
            date_of_birth=date(2002, 3, 3),
            gender='m', 
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )
        s4 = Student.objects.create(
            user=u4,
            first_name='Sarah',
            last_name='Davis',
            date_of_birth=date(2003, 4, 4),
            gender='f', 
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )
        s5 = Student.objects.create(
            user=u5,
            first_name='David',
            last_name='Wilson',
            date_of_birth=date(2004, 5, 5),
            gender='m', 
            contact_number='1234567890',
            emergency_contact_name='Jane Doe',  
            emergency_contact_number='9876543210',
            status='a', 
            date_joined=date.today(),
        )
        c2 = Course.objects.create(
            title='Art 101',
            description='Basic Art',
            status='a'
        )
        c3 = Course.objects.create(
            title='Science 101',
            description='Basic Science',
            status='p'
        )
        c4 = Course.objects.create(
            title='History 101',
            description='Basic History',
            status='p'
        )
        c5 = Course.objects.create(
            title='Geography 101',  
            description='Basic Geography',
            status='p'
        )
        e2 = Enrollment.objects.create(
            student=s2,
            course=c2,
            status='a'
        )
        e3 = Enrollment.objects.create(
            student=s3,
            course=c3,
            status='a'
        )
        e4 = Enrollment.objects.create(
            student=s4,
            course=c4,
            status='a'
        )
        e5 = Enrollment.objects.create(
            student=s5,
            course=c5,
            status='a'
        )
        qs = Student.objects.all()
        with CaptureQueriesContext(connection=connection) as ctx:
            se = StudentModelSerializer(qs, many=True)
            print (se.data)
        print(ctx.captured_queries)
        self.assertEqual(len(se.data), 5)


class StudentAssessmentAPITests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        # 1. Setup Users
        self.student_user = User.objects.create_user(username='api_student', password='password123')
        self.teacher_user = User.objects.create_user(username='api_teacher', password='password123')

        # 2. Setup Profiles
        self.student = Student.objects.create(
            user=self.student_user,
            first_name="Test", last_name="Student",
            date_of_birth="2000-01-01", gender="m",
            contact_number="1234567890"
        )
        self.teacher = Teacher.objects.create(user=self.teacher_user)

        # 3. Setup Course & Enrollment
        self.course = Course.objects.create(title="Math 101", status="p", price=100)
        Enrollment.objects.create(student=self.student, course=self.course)

    def test_get_student_assignments_flow(self):
        """
        Verify:
        1. Student sees assignments for their course.
        2. Student sees THEIR OWN submission status.
        3. Student sees THEIR OWN grade.
        """
        # A. Create Assignment
        assignment = Assignment.objects.create(
            course=self.course,
            title="Algebra Homework",
            due_date=timezone.now().date()
        )

        # B. Create Submission (Graded)
        submission = Submission.objects.create(
            assignment=assignment,
            student=self.student,
            status="g"
        )

        # C. Create Grade
        SubmissionGrade.objects.create(
            submission=submission,
            grade=95.5,
            feedback="Good job",
            graded_by=self.teacher
        )

        # D. Call API
        # URL structure: /students/students/{id}/assignments/
        url = f'/students/students/{self.student.pk}/assignments/'
        response = self.client.get(url)

        # E. Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        data = response.data[0]
        self.assertEqual(data['title'], "Algebra Homework")
        self.assertIsNotNone(data['submission'])
        self.assertEqual(data['submission']['status'], "g")
        self.assertIsNotNone(data['submission']['grade'])
        self.assertEqual(float(data['submission']['grade']['grade']), 95.5)

    def test_get_student_exams_flow(self):
        """
        Verify:
        1. Student sees exams.
        2. Duration is calculated correctly.
        3. Score (Review) is nested correctly.
        """
        # A. Create Exam (3 Hours long)
        start = timezone.now()
        end = start + timedelta(hours=3)
        exam = Exams.objects.create(
            course=self.course,
            title="Final Exam",
            start_time=start,
            end_time=end,
            total_marks=100
        )

        # B. Create Submission
        sub = ExamSubmissions.objects.create(
            exam=exam,
            student=self.student
        )

        # C. Create Review
        ExamReviews.objects.create(
            exam_submission=sub,
            score=88.0,
            graded_by=self.teacher,
            feedback="Well done"
        )

        # D. Call API
        url = f'/students/students/{self.student.pk}/exams/'
        response = self.client.get(url)

        # E. Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data[0]
        self.assertIn("3:00:00", data['duration']) 
        self.assertIsNotNone(data['submission'])
        self.assertIsNotNone(data['submission']['review'])
        self.assertEqual(float(data['submission']['review']['score']), 88.0)

    def test_data_privacy_between_students(self):
        """
        Verify that Student A cannot see Student B's submissions.
        """
        # 1. Create another student (Student B)
        other_user = User.objects.create_user(username='other_student', password='pw')
        other_student = Student.objects.create(
            user=other_user, 
            first_name="Other", last_name="Guy",
            date_of_birth="2000-01-01", gender="m",
            contact_number="0000000000"
        )
        
        # 2. Enroll both in the same course
        Enrollment.objects.create(student=other_student, course=self.course)

        # 3. Create Assignment
        assign = Assignment.objects.create(course=self.course, title="Shared HW")

        # 4. Create Submission for Student A (Main Student)
        Submission.objects.create(assignment=assign, student=self.student, status='s')

        # 5. Call API as Student B (Other Student)
        url = f'/students/students/{other_student.pk}/assignments/'
        response = self.client.get(url)

        # 6. Check Result
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data[0]
        self.assertEqual(data['title'], "Shared HW")
        self.assertIsNone(data['submission'])