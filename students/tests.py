from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Course
from students.models import Student, Enrollment
from datetime import date

User = get_user_model()

class StudentEnrollmentTestCase(TestCase):
    def setUp(self):
        # Create a test admin
        self.admin = User.objects.create_user(username='TestAdmin', password='1234')
    
    def test_admin_count(self):
        count = User.objects.count()
        self.assertEqual(count, 1)

    def test_enrollment(self):
        #  Create another user
        u1 = User.objects.create_user(username='James', password='abcd')
        # Create a student
        s1 = Student.objects.create(
            user=u1,
            first_name='James',
            last_name='Smith',
            date_of_birth=date(2000, 1, 1),
            gender='M',
            contact_number='1234567890',
            emergency_contact_name='John Smith',
            emergency_contact_number='0987654321',
            status='a',
            date_joined=date(2022, 9, 1),
            created_by=self.admin,
            updated_by=self.admin
        )
        # Create a course
        c1 = Course.objects.create(
            title='Mathematics 101',
            description='An introductory course to Mathematics.',
            status='p',
            created_by=self.admin,
            updated_by=self.admin
        )
        # Enroll the student in the course
        Enrollment.objects.create(
            student=s1,
            course=c1,
            status='a',
            created_by=self.admin,
            updated_by=self.admin
        )
        # Verify enrollment
        E_count = Enrollment.objects.count()
        self.assertEqual(E_count, 1)