from datetime import date, timedelta
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone 
from rest_framework import status
from rest_framework.test import APITestCase

from students.models import Student, Enrollment
from courses.models import Course
from assessments.models import Assignment, Exams

User = get_user_model()

class StudentModuleTests(APITestCase):
    """
    Finalized test suite for the Students Module.
    Verifies API stability, model constraints, and performance targets.
    """

    def setUp(self):
        # Admin authentication
        self.staff_user = User.objects.create_user(
            username='system_manager', 
            password='secure_admin_pass'
        )
        self.client.force_authenticate(user=self.staff_user)

        # Core project data
        self.math_course = Course.objects.create(title="Advanced Calculus", status="p")
        self.physics_course = Course.objects.create(title="Quantum Mechanics", status="p")

        # Standard student record
        self.profile_user = User.objects.create_user(username='m_smith', password='student_pass_123')
        self.student = Student.objects.create(
            user=self.profile_user,
            first_name='Michael',
            last_name='Smith',
            gender='m',
            date_of_birth=date(2003, 8, 12),
            contact_number='9876543210',
            emergency_contact_name='Sarah Smith',
            emergency_contact_number='9876543211',
            status='a',
            date_joined=date.today()
        )

        # Enrollment and related assessment data
        self.enrollment = Enrollment.objects.create(
            student=self.student, 
            course=self.math_course, 
            status='a'
        )
        
        self.assignment = Assignment.objects.create(
            title="Calculus Problem Set 1",
            course=self.math_course,
            description="Initial set for integration modules."
        )
        
        now = timezone.now()
        self.midterm_exam = Exams.objects.create(
            title="Physics Midterm",
            course=self.physics_course,
            total_marks=50,
            start_time=now,
            end_time=now + timedelta(hours=3)
        )

    # --- 1.1 Student Management ---

    def test_list_students_functional(self):
        url = reverse('student-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_create_student_transaction_integrity(self):
        url = reverse('student-list')
        payload = {
            "user": {"username": "j_doe_new", "password": "new_secure_pass"},
            "first_name": "Jane",
            "last_name": "Doe",
            "gender": "f",
            "contact_number": "1122334455",
            "date_of_birth": "2005-01-01",
            "date_joined": str(date.today()),
            "emergency_contact_name": "Richard Doe",
            "emergency_contact_number": "5544332211"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        created_user = User.objects.get(username="j_doe_new")
        self.assertTrue(created_user.check_password("new_secure_pass"))

    def test_student_soft_delete(self):
        url = reverse('student-detail', args=[self.student.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.student.refresh_from_db()
        self.assertEqual(self.student.status, 'i')

    # --- 1.2 Nested Endpoints ---

    def test_with_courses_output_optimization(self):
        url = reverse('student-with-courses')
        response = self.client.get(url)
        
        student_entry = response.data['results'][0]
        self.assertIn('courses', student_entry)
        
        course_data = student_entry['courses'][0]
        self.assertIn('id', course_data)
        self.assertIn('title', course_data)
        self.assertNotIn('description', course_data)

    def test_student_assignments_filtering(self):
        url = reverse('student-assignments', args=[self.student.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['title'], "Calculus Problem Set 1")

    def test_query_count_prevention(self):
        """Confirm select_related('user') avoids N+1 database hits."""
        for i in range(2):
            u = User.objects.create_user(username=f'node_{i}', password='p')
            Student.objects.create(
                user=u, 
                first_name='F', 
                last_name='L', 
                gender='o', 
                contact_number='0000000000', 
                date_of_birth=date(2000, 1, 1), 
                date_joined=date.today(), 
                emergency_contact_name='G', 
                emergency_contact_number='0'
            )

        url = reverse('student-list')
        with CaptureQueriesContext(connection) as ctx:
            self.client.get(url)
        self.assertLessEqual(len(ctx.captured_queries), 8)

    # --- 1.3 Enrollment Management ---

    def test_enrollment_status_patch(self):
        url = reverse('enrollment-detail', args=[self.enrollment.id])
        payload = {"status": "c"}
        response = self.client.patch(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.status, 'c')

    def test_enrollment_routing_integrity(self):
        url = reverse('enrollment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
