from django.db import connection
from datetime import date
from django.test import TestCase
from utility.models import User
from staffs.models import Teacher, Qualification, UserQualification, Specialization, UserSpecialization, Department, UserDepartment, Designation, UserDesignation
from staffs.serializer import TeacherModelSerializer, QualificationModelSerializer, UserQualificationModelSerializer, SpecializationSerializer
from django.test.utils import CaptureQueriesContext

class TeacherModelSerializerTestCase(TestCase):
    def setUp(self):
        self_user = User.objects.create_user(
            username='John',
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
            username='Jane',
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

    def test_serializer_update(self):
        change = {
            'first_name': 'Johnny',
            'last_name': 'Doe',
            'dob': '1984-01-01',
        }
        se = TeacherModelSerializer(self.teacher_1, data=change, partial=True)
        self.assertTrue(se.is_valid())
        se.save()
        self.teacher_1.refresh_from_db()
        self.assertEqual(self.teacher_1.first_name, 'Johnny')

    def test_listing(self):
        u2 = User.objects.create_user(
            username='Steve',
            password='password123',
        )
        u3 = User.objects.create_user(
            username='Anna',
            password='password123',
        )
        u4 = User.objects.create_user(
            username='Mary',
            password='password123',
        )
        u5 = User.objects.create_user(
            username='Bob',
            password='password123',
        )

        t2 = Teacher.objects.create(
            user=u2,
            first_name='Steve',
            last_name='Brown',
            dob=date(1975, 6, 20),
            gender='m',
            employee_code='2345',   
            experience_years=10,
            contact_number='1234567890', 
            emergency_contact_number='9876543210',
            email_institutional='q1w2@example.com',
            status='a', 
            date_joined=date.today(),
        )
        t3 = Teacher.objects.create(
            user=u3,
            first_name='Anna',
            last_name='Davis',
            dob=date(1988, 3, 14),
            gender='f',
            employee_code='3456',
            experience_years=5,
            contact_number='1234567890', 
            emergency_contact_number='9876543210',
            email_institutional='e3r4r4@example.com',
            status='a', 
            date_joined=date.today(),
        )
        t4 = Teacher.objects.create(
            user=u4,
            first_name='Mary',
            last_name='Wilson',
            dob=date(1992, 11, 30),
            gender='f',
            employee_code='4567',
            experience_years=3,
            contact_number='1234567890', 
            emergency_contact_number='9876543210',
            email_institutional='q1w2e3t5y6@example.com',
            status='a', 
            date_joined=date.today(),
        )
        t5 = Teacher.objects.create(
            user=u5,
            first_name='Bob',
            last_name='Taylor',
            dob=date(1980, 8, 25),
            gender='m',
            employee_code='5678',
            experience_years=8,
            contact_number='1234567890', 
            emergency_contact_number='9876543210',
            email_institutional='q1w2o90p@example.com',
            status='a', 
            date_joined=date.today(),
        )
        qs = Teacher.objects.all().select_related('user')
        with CaptureQueriesContext(connection=connection) as ctx:
            se = TeacherModelSerializer(qs, many=True)
            print (se.data)
        print(ctx.captured_queries)
        self.assertEqual(len(se.data), 5)

class QualificationModelSerializerTestCase(TestCase):
    def setUp(self):
        self.qualification_1 = Qualification.objects.create(
            name='Bachelor of Science',
            description='Undergraduate academic degree',
            status='a',
        )

    def test_qualification_model_serializer(self):
        se = QualificationModelSerializer(self.qualification_1)
        print(se.data)
        self.assertEqual(se.data['name'], 'Bachelor of Science')

    def test_serializer_create(self):
        data = {
            'name': 'Master of Science',
            'description': 'Graduate academic degree',
            'status': 'a',
        }
        se = QualificationModelSerializer(data=data)
        print(se.is_valid())
        print(se.errors)
        self.assertTrue(se.is_valid())
        se.save()
        self.assertEqual(Qualification.objects.count(), 2)

    def test_serializer_update(self):
        change = {
            'description': 'Updated description for Bachelor of Science',
        }
        se = QualificationModelSerializer(self.qualification_1, data=change, partial=True)
        self.assertTrue(se.is_valid())
        se.save()
        self.qualification_1.refresh_from_db()
        self.assertEqual(self.qualification_1.description, 'Updated description for Bachelor of Science')
        print(se.is_valid())
        print(se.errors)

    def test_listing(self):
        q2 = Qualification.objects.create(
            name='Doctor of Philosophy',
            description='Highest academic degree',
            status='a',
        )
        q3 = Qualification.objects.create(
            name='Associate Degree',
            description='Undergraduate academic degree',
            status='a',
        )
        qs = Qualification.objects.all()
        with CaptureQueriesContext(connection=connection) as ctx:
            se = QualificationModelSerializer(qs, many=True)
            print (se.data)
        print(ctx.captured_queries)
        self.assertEqual(len(se.data), 3)

class UserQualificationModelSerializerTestCase(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user(
            username='Alice',
            password='password123',
        )
        self.qualification_1 = Qualification.objects.create(
            name='Bachelor of Arts',
            description='Undergraduate academic degree',
            status='a',
        )
        self.user_qualification_1 = UserQualification.objects.create(
            user=self.user_1,
            qualification=self.qualification_1,
            status='a',
        )

    def test_user_qualification_model_serializer(self):
        se = UserQualificationModelSerializer(self.user_qualification_1)
        print(se.data)
        self.assertEqual(se.data['user'], self.user_1.id)

    def test_serializer_create(self):
        u2 = User.objects.create_user(
            username='Bob',
            password='password123',
        )
        q2 = Qualification.objects.create(
            name='Master of Arts',
            description='Graduate academic degree',
            status='a',
        )
        data = {
            'user': u2.id,
            'qualification': q2.id,
            'status': 'a',
        }
        se = UserQualificationModelSerializer(data=data)
        print(se.is_valid())
        print(se.errors)
        self.assertTrue(se.is_valid())
        se.save()
        self.assertEqual(UserQualification.objects.count(), 2)
    
    def test_serializer_update(self):
        change = {
            'status': 'i',
        }
        se = UserQualificationModelSerializer(self.user_qualification_1, data=change, partial=True)
        self.assertTrue(se.is_valid())
        se.save()
        self.user_qualification_1.refresh_from_db()
        self.assertEqual(self.user_qualification_1.status, 'i')
        print(se.is_valid())
        print(se.errors)

    def test_listing(self):
        u2 = User.objects.create_user(
            username='Charlie',
            password='password123',
        )
        u3 = User.objects.create_user(
            username='Diana',
            password='password123',
        )
        u4 = User.objects.create_user(    
            username='Eva',
            password='password123',
        )
        u5 = User.objects.create_user(
            username='Frank',
            password='password123',
        )
        q2 = Qualification.objects.create(
            name='Doctor of Arts',
            description='Highest academic degree',
            status='a',
        )
        q3 = Qualification.objects.create(
            name='Associate of Arts',
            description='Undergraduate academic degree',
            status='a',
        )
        uq2 = UserQualification.objects.create(
            user=u2,
            qualification=q2,
            status='a', 
        )
        uq3 = UserQualification.objects.create(
            user=u3,
            qualification=q3,
            status='a',
        )
        uq4 = UserQualification.objects.create(
            user=u4,
            qualification=self.qualification_1,
            status='a',
        )
        uq5 = UserQualification.objects.create(
            user=u5,
            qualification=q2,
            status='a',
        )
        qs = UserQualification.objects.all().select_related('user', 'qualification')
        with CaptureQueriesContext(connection=connection) as ctx:
            se = UserQualificationModelSerializer(qs, many=True)
            print (se.data)
        print(ctx.captured_queries)
        self.assertEqual(len(se.data), 5)

class SpecializationModelSerializerTestCase(TestCase):
    def setUp(self):
        self.specialization_1 = Specialization.objects.create(
            name='Mathematics',
            description='Study of numbers and shapes',
            status='a',
        )

    def test_specialization_serializer(self):
        se = SpecializationSerializer(self.specialization_1)
        print(se.data)
        self.assertEqual(se.data['name'], 'Mathematics')

    def test_serializer_create(self):
        data = {
            'name': 'Physics',
            'description': 'Study of matter and energy',
            'status': 'a',
        }
        se = SpecializationSerializer(data=data)
        print(se.is_valid())
        print(se.errors)
        self.assertTrue(se.is_valid())
        se.save()
        self.assertEqual(Specialization.objects.count(), 2)

    def test_serializer_update(self):
        change = {
            'description': 'Updated description for Mathematics',
        }
        se = SpecializationSerializer(self.specialization_1, data=change, partial=True)
        self.assertTrue(se.is_valid())
        se.save()
        self.specialization_1.refresh_from_db()
        self.assertEqual(self.specialization_1.description, 'Updated description for Mathematics')
        print(se.is_valid())
        print(se.errors)

    def test_listing(self):
        s2 = Specialization.objects.create(
            name='Chemistry',
            description='Study of substances and reactions',
            status='a',
        )
        s3 = Specialization.objects.create(
            name='Biology',
            description='Study of living organisms',
            status='a',
        )
        qs = Specialization.objects.all()
        with CaptureQueriesContext(connection=connection) as ctx:
            se = SpecializationSerializer(qs, many=True)
            print (se.data)
        print(ctx.captured_queries)
        self.assertEqual(len(se.data), 3)

    