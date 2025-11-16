from datetime import date
from django.test import TestCase
from utility.models import User
from staffs.models import Teacher
from staffs.serializer import TeacherModelSerializer
from django.test.utils import CaptureQueriesContext

class TeacherModelSerializerTestCase(TestCase):
    def setUp(self):
        self_user = User.objects.create_user(
            username='teacher1',
            password='password123',
        )
        self.teacher_1 = Teacher.objects.create(
            user=self_user,
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

    def test_teacher_model_serializer(self):
        se = TeacherModelSerializer(self.teacher_1)
        print(se.data)
        self.assertEqual(se.data['first_name'], 'John')
