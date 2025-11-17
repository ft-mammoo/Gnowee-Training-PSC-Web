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
        #print(se.data)
        self.assertEqual(se.data['first_name'], 'John')

    def test_serializer_create(self):
        teacher_user = User.objects.create_user(
            username='teacher2',
            password='password123',
        )
        data = {
            'user': teacher_user.id,
            'first_name': 'Jane',
            'last_name': 'Smith',
            'dob': '1990-05-15',
            'gender': 'f',
            'employee_code': '5678',
            'experience_years': 5,
            'contact_number': '0987654321',
            'emergency_contact_number': '1234509876',
            'email_institutional': 'HcMl7@example.com', 
            'status': 'a',
            'date_joined': '2022-01-01',
        }
        se = TeacherModelSerializer(data=data)
        print(se.is_valid())
        print(se.errors)
        self.assertTrue(se.is_valid())
        se.save()
        self.assertEqual(Teacher.objects.count(), 2)
