from rest_framework.test import APITestCase
from rest_framework import status
from django.db import connection
from django.test.utils import CaptureQueriesContext
from datetime import date
from utility.models import User
from staffs import models as mod

class TeacherProfileAPIEndpointTestCase(APITestCase):
    """
    Integration tests for the Teacher ViewSet.
    Validates CRUD operations, soft-delete visibility logic (StatusManagerMixin),
    and database integrity constraints.
    """
    
    def setUp(self):
        # Base endpoint URL (Adjust if you have an API prefix like '/api/v1/teachers/')
        self.base_url = '/teachers/'
        
        # 1. Setup Active Teacher (Kerala Institutional Data)
        self.active_user = User.objects.create_user(
            username='muhammed_sadiq',
            password='securepassword123',
        )
        self.active_teacher = mod.Teacher.objects.create(
            user=self.active_user,
            first_name='Muhammed',
            last_name='Sadiq',
            dob=date(1985, 4, 12),
            gender='m',
            employee_code='EMP-CS-1042',
            experience_years=8,
            contact_number='9846012345',
            emergency_contact_number='9846054321',
            email_institutional='m.sadiq@nitc.ac.in',
            status='a', 
            date_joined=date(2018, 8, 1),
        )

        # 2. Setup Inactive / Soft-Deleted Teacher (GCC Institutional Data)
        self.inactive_user = User.objects.create_user(
            username='fatima_hashmi',
            password='securepassword123',
        )
        self.inactive_teacher = mod.Teacher.objects.create(
            user=self.inactive_user,
            first_name='Fatima',
            last_name='Al Hashmi',
            dob=date(1990, 7, 22),
            gender='f',
            employee_code='EMP-EE-2050',
            experience_years=5,
            contact_number='0501234567',
            emergency_contact_number='0507654321',
            email_institutional='f.hashmi@ku.ac.ae',
            status='i', # Notice the status is 'i' (Inactive)
            date_joined=date(2020, 1, 15),
        )

    def test_list_teachers_returns_active_only(self):
        """
        Verify standard GET request returns only active profiles.
        Also utilizes CaptureQueriesContext to ensure we aren't hitting N+1 query leaks
        when serializing the related User models.
        """
        with CaptureQueriesContext(connection=connection) as ctx:
            response = self.client.get(self.base_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return Muhammed Sadiq (Active), skipping Fatima (Inactive)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['employee_code'], 'EMP-CS-1042')
        # Ensure query count is optimized (usually 2: one for count, one for data fetch)
        self.assertLessEqual(len(ctx.captured_queries), 3)

    def test_list_teachers_with_inactive_status_filter(self):
        """
        Verify passing '?status=i' dynamically escalates the manager 
        to fetch soft-deleted records via the StatusManagerMixin.
        """
        response = self.client.get(f"{self.base_url}?status=i")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should now return Fatima Hashmi (Inactive)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['employee_code'], 'EMP-EE-2050')

    def test_list_teachers_ignores_empty_status_parameter(self):
        """
        Prevent data leakage if a client sends an empty query param ('?status=').
        The mixin must evaluate to false and maintain the default active manager.
        """
        response = self.client.get(f"{self.base_url}?status=")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should still only return Muhammed Sadiq (Active)
        self.assertEqual(response.data['count'], 1)

    def test_create_teacher_success_creates_user_and_profile(self):
        """
        Verify a completely valid payload successfully persists to the database.
        """
        new_user = User.objects.create_user(username='zayed_ahmed', password='password')
        payload = {
            'user': new_user.id,
            'first_name': 'Zayed',
            'last_name': 'Ahmed',
            'dob': '1992-11-05',
            'gender': 'm',
            'employee_code': 'EMP-ME-3010',
            'experience_years': 4,
            'contact_number': '0559876543',
            'emergency_contact_number': '0553456789',
            'email_institutional': 'z.ahmed@aus.edu',
            'status': 'a',
            'date_joined': '2023-09-01'
        }
        
        response = self.client.post(self.base_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(mod.Teacher.all_objects.count(), 3)

    def test_create_teacher_fails_on_duplicate_active_code(self):
        """
        Ensure UniqueValidator blocks creation if the employee code 
        is already held by an ACTIVE teacher.
        """
        new_user = User.objects.create_user(username='test_duplicate', password='password')
        payload = {
            'user': new_user.id,
            'first_name': 'Clone',
            'last_name': 'Teacher',
            'dob': '1990-01-01',
            'gender': 'm',
            'employee_code': 'EMP-CS-1042', # Duplicating Muhammed Sadiq's active code
            'experience_years': 1,
            'contact_number': '1111111111',
            'emergency_contact_number': '2222222222',
            'email_institutional': 'clone@nitc.ac.in',
            'status': 'a',
            'date_joined': '2024-01-01'
        }
        
        response = self.client.post(self.base_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('employee_code', response.data)

    def test_create_teacher_succeeds_reusing_inactive_code(self):
        """
        Crucial architectural test. If an employee code belongs to a 
        SOFT-DELETED (inactive) teacher, the system should permit a new active teacher 
        to inherit and reuse that code.
        """
        new_user = User.objects.create_user(username='new_hire', password='password')
        payload = {
            'user': new_user.id,
            'first_name': 'Aisha',
            'last_name': 'Rahman',
            'dob': '1995-03-10',
            'gender': 'f',
            'employee_code': 'EMP-EE-2050', # Reusing Fatima Hashmi's inactive code
            'experience_years': 2,
            'contact_number': '0528889999',
            'emergency_contact_number': '0529998888',
            'email_institutional': 'a.rahman@ku.ac.ae',
            'status': 'a',
            'date_joined': '2024-02-01'
        }
        
        response = self.client.post(self.base_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verify the database now holds both the inactive legacy profile and the new active profile
        self.assertEqual(mod.Teacher.all_objects.filter(employee_code='EMP-EE-2050').count(), 2)

    def test_create_teacher_fails_on_multiple_active_profiles_per_user(self):
        """
        A single User account cannot be mapped to multiple Active Teacher profiles.
        """
        payload = {
            'user': self.active_user.id, # Attempting to map to Muhammed Sadiq's already active account
            'first_name': 'Muhammed',
            'last_name': 'Sadiq V2',
            'dob': '1985-04-12',
            'gender': 'm',
            'employee_code': 'EMP-CS-1043', # Different code
            'experience_years': 8,
            'contact_number': '9846012345',
            'emergency_contact_number': '9846054321',
            'email_institutional': 'm.sadiq.v2@nitc.ac.in', # Different email
            'status': 'a',
            'date_joined': '2018-08-01'
        }
        
        response = self.client.post(self.base_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_active_teacher_detail_success(self):
        """
        Detail endpoint should resolve active items cleanly.
        """
        url = f"{self.base_url}{self.active_teacher.id}/"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Muhammed')

    def test_retrieve_inactive_teacher_detail_with_status_parameter(self):
        """
        Detail endpoint must bypass the 404 block for soft-deleted items 
        if explicitly requested by the client via the ?status= query string.
        """
        url = f"{self.base_url}{self.inactive_teacher.id}/?status=i"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Fatima')

    def test_delete_teacher_executes_soft_delete(self):
        """
        Ensure the DELETE method does not drop the database row, 
        but instead mutates the record's status to 'i'.
        """
        url = f"{self.base_url}{self.active_teacher.id}/"
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify row still exists in DB, but status is mutated
        self.active_teacher.refresh_from_db()
        self.assertEqual(self.active_teacher.status, 'i')
