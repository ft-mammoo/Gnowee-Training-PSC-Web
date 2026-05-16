from rest_framework.test import APITestCase
from rest_framework import status
from django.db import connection, IntegrityError
from django.test.utils import CaptureQueriesContext
from datetime import date
from unittest.mock import patch
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

class DepartmentAdministrationAPIEndpointTestCase(APITestCase):
    """
    Integration tests for Department endpoints and nested Teacher allocations.
    Validates transactional consistency, relationship recycling, and subquery isolation.
    """

    def setUp(self):
        self.base_url = '/departments/'

        # 1. Setup Active and Inactive Departments (Regional Kerala/GCC Dataset)
        self.active_dept_cs = mod.Department.objects.create(
            name='Computer Science and Engineering',
            description='Department of CSE at NIT Calicut',
            status='a'
        )
        self.inactive_dept_ee = mod.Department.objects.create(
            name='Electrical Engineering',
            description='Legacy Department holding historical mappings',
            status='i'
        )

        # 2. Setup Faculty Users & Profiles
        self.user_anand = User.objects.create_user(username='anand_narayanan', password='password123')
        self.teacher_anand = mod.Teacher.objects.create(
            user=self.user_anand,
            first_name='Anand',
            last_name='Narayanan',
            employee_code='EMP-CSE-011',
            email_institutional='anand@nitc.ac.in',
            status='a'
        )

        self.user_fahad = User.objects.create_user(username='fahad_mansoor', password='password123')
        self.teacher_fahad = mod.Teacher.objects.create(
            user=self.user_fahad,
            first_name='Fahad',
            last_name='Al-Mansoor',
            employee_code='EMP-ECE-099',
            email_institutional='f.mansoor@ku.ac.ae',
            status='a'
        )

        # 3. Setup Relationships (Active assignment vs Legacy soft-deleted assignment)
        self.active_mapping = mod.UserDepartment.objects.create(
            user=self.user_anand,
            department=self.active_dept_cs,
            status='a'
        )
        self.historical_mapping = mod.UserDepartment.objects.create(
            user=self.user_fahad,
            department=self.active_dept_cs,
            status='i' # Deactivated historical relationship
        )

    def test_list_departments_returns_active_only(self):
        """
        Verify base list view scopes visibility to active rows only,
        enforcing structural segregation from archived institutional records.
        """
        response = self.client.get(self.base_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Computer Science and Engineering')

    def test_list_departments_with_inactive_status_filter(self):
        """
        Verify manager switching securely exposes soft-deleted departments
        when specifically requested via query parameters.
        """
        response = self.client.get(f"{self.base_url}?status=i")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Electrical Engineering')

    def test_list_department_teachers_returns_active_mappings_only(self):
        """
        Verify nested GET route targets active faculty mappings,
        preventing legacy staff associations from showing.
        """
        url = f"{self.base_url}{self.active_dept_cs.id}/teachers/"
        
        with CaptureQueriesContext(connection=connection) as ctx:
            response = self.client.get(url)
            
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only evaluate Dr. Anand Narayanan as active faculty
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['employee_code'], 'EMP-CSE-011')
        # Check optimization to verify lookups do not cascade row operations
        self.assertLessEqual(len(ctx.captured_queries), 4)

    def test_list_department_teachers_with_inactive_status_filter(self):
        """
        Verify status query parameters override normal active query restrictions
        to cleanly retrieve historical allocations.
        """
        url = f"{self.base_url}{self.active_dept_cs.id}/teachers/?status=i"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should cleanly swap contexts to capture Prof. Fahad's historical relationship context
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['employee_code'], 'EMP-ECE-099')

    def test_assign_teacher_to_department_success(self):
        """
        Verify creating a fresh relation safely links the target user 
        to the specified department entity.
        """
        user_new = User.objects.create_user(username='dilip_kumar', password='password123')
        mod.Teacher.objects.create(
            user=user_new, first_name='Dilip', last_name='Kumar',
            employee_code='EMP-CSE-012', email_institutional='dilip@nitc.ac.in', status='a'
        )
        
        url = f"{self.base_url}{self.active_dept_cs.id}/teachers/"
        payload = {'user': user_new.id}
        
        response = self.client.post(url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(mod.UserDepartment.objects.filter(department=self.active_dept_cs, status='a').count(), 2)

    def test_assign_teacher_to_department_fails_on_duplicate_active(self):
        """
        Ensure validation halts transaction and rejects payload with a 400 
        if the teacher is already actively allocated to that department.
        """
        url = f"{self.base_url}{self.active_dept_cs.id}/teachers/"
        payload = {'user': self.user_anand.id} # Dr. Anand is already active here
        
        response = self.client.post(url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], "This user is already active in this department.")

    def test_assign_teacher_to_department_reactivates_historical_mapping(self):
        """
        Confirm recycling mechanism. If a soft-deleted record is matched,
        the system must reactivate the row via partial updates instead of adding a new duplicate row.
        """
        url = f"{self.base_url}{self.active_dept_cs.id}/teachers/"
        payload = {'user': self.user_fahad.id} # Prof. Fahad holds an inactive row ('i')
        
        response = self.client.post(url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.historical_mapping.refresh_from_db()
        # Verify state transitioned cleanly back to Active
        self.assertEqual(self.historical_mapping.status, 'a')
        # Row allocation count remains unchanged
        self.assertEqual(mod.UserDepartment.all_objects.count(), 2)

    def test_assign_teacher_to_department_concurrency_handling(self):
        """
        Verify exception shielding blocks race conditions. Simulates an IntegrityError 
        collision to prove transaction blocks recover with a graceful 400 instead of a 500 server crash.
        """
        user_race = User.objects.create_user(username='race_condition_user', password='password123')
        # Create the missing active Teacher profile so the serializer passes base mapping checks
        mod.Teacher.objects.create(
            user=user_race, first_name='Race', last_name='Condition',
            employee_code='EMP-RNG-999', email_institutional='race@nitc.ac.in', status='a'
        )
        url = f"{self.base_url}{self.active_dept_cs.id}/teachers/"
        payload = {'user': user_race.id}
        
        # Patch the serializer's save method to simulate a concurrent write committing a fraction of a second earlier
        with patch('staffs.views.UserDepartmentSerializer.save') as mock_save:
            mock_save.side_effect = IntegrityError("UNIQUE constraint failed: staffs_userdepartment.user_id")
            response = self.client.post(url, data=payload, format='json')
            
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "This user is already active in this department.")

class StandaloneMappingsAPIEndpointTestCase(APITestCase):
    """
    Integration tests for standalone master files (Qualifications, Specializations, Designations)
    and user-specific relationship records. Validates recycling loops, state lookup guards, 
    and multi-entity collection structures.
    """

    def setUp(self):
        # Base API URL configurations
        self.qual_url = '/qualifications/'
        self.user_qual_url = '/user-qualifications/'

        # Setup Global Master Records (Kerala & GCC dataset alignment)
        self.active_phd = mod.Qualification.objects.create(
            name='Ph.D. in Computer Science',
            description='Doctoral degree from CUSAT Cochin',
            status='a'
        )
        self.inactive_mtech = mod.Qualification.objects.create(
            name='M.Tech in Legacy Systems',
            description='Archived qualification course registry',
            status='i'
        )
        self.active_spec = mod.Specialization.objects.create(
            name='Distributed Ledger Technology',
            description='Blockchain systems research domain',
            status='a'
        )
        self.active_desig = mod.Designation.objects.create(
            name='Associate Professor',
            description='Senior faculty title grade',
            status='a'
        )

        # Setup User Profiles (One Active Teacher, One Base User with no Profile)
        self.user_aslam = User.objects.create_user(username='aslam_kasaragod', password='password123')
        self.teacher_aslam = mod.Teacher.objects.create(
            user=self.user_aslam,
            first_name='Aslam',
            last_name='Kozhikode',
            employee_code='EMP-CS-9911',
            email_institutional='aslam@nitc.ac.in',
            status='a'
        )

        self.user_base_only = User.objects.create_user(username='regular_staff_member', password='password123')
        # user_base_only deliberately has no Teacher profile record attached

        # Setup Relational Mappings (Active vs Historical soft-deleted mapping)
        self.historical_qual_mapping = mod.UserQualification.objects.create(
            user=self.user_aslam,
            qualification=self.active_phd,
            status='i' # Deactivated historical mapping link
        )

    def test_list_global_entities_returns_active_only(self):
        """
        Verify that master collection list views scope execution 
        to active records only, filtering out deprecated educational programs.
        """
        with CaptureQueriesContext(connection=connection) as ctx:
            response = self.client.get(self.qual_url)
            
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only render the active PhD entry, bypassing the inactive record
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Ph.D. in Computer Science')
        # Verify query structure is direct and flat
        self.assertLessEqual(len(ctx.captured_queries), 3)

    def test_list_user_qualifications_with_inactive_status_filter(self):
        """
        Verify query filters switch model managers to unlock historical mapping rows.
        """
        response = self.client.get(f"{self.user_qual_url}?status=i")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return the soft-deleted user-qualification assignment link
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['user'], self.user_aslam.id)

    def test_create_user_qualification_success(self):
        """
        Verify building a pristine relationship mapping succeeds when pointing
        to valid active instances.
        """
        # Create a clean active qualification and active user profile first
        fresh_qual = mod.Qualification.objects.create(name='M.Phil in Computing', status='a')
        user_clean = User.objects.create_user(username='vinod_dr', password='password123')
        mod.Teacher.objects.create(
            user=user_clean, first_name='Vinod', last_name='Kumar',
            employee_code='EMP-EC-4022', email_institutional='vinod@nitc.ac.in', status='a'
        )

        payload = {
            'user': user_clean.id,
            'qualification': fresh_qual.id,
            'status': 'a'
        }
        response = self.client.post(self.user_qual_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(mod.UserQualification.objects.filter(user=user_clean, status='a').count(), 1)

    def test_create_user_qualification_fails_without_active_teacher_profile(self):
        """
        Verify the serialization engine prevents assigning faculty metadata 
        to account entities that lack an active Teacher profile row.
        """
        payload = {
            'user': self.user_base_only.id,
            'qualification': self.active_phd.id,
            'status': 'a'
        }
        response = self.client.post(self.user_qual_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_qualification_fails_on_inactive_global_entity(self):
        """
        Verify relationships cannot link active profiles to soft-deleted 
        or inactive master file dictionary positions.
        """
        payload = {
            'user': self.user_aslam.id,
            'qualification': self.inactive_mtech.id, # Points to status='i' row
            'status': 'a'
        }
        response = self.client.post(self.user_qual_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_qualification_fails_on_duplicate_active(self):
        """
        Ensure constraint assertions block concurrent active assignments 
        of identical academic records onto the same user.
        """
        # Establish an active mapping line first
        fresh_qual = mod.Qualification.objects.create(name='B.Tech CSE', status='a')
        mod.UserQualification.objects.create(user=self.user_aslam, qualification=fresh_qual, status='a')

        payload = {
            'user': self.user_aslam.id,
            'qualification': fresh_qual.id,
            'status': 'a'
        }
        response = self.client.post(self.user_qual_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_reactivates_user_qualification(self):
        """
        Verify state machine operations handle reactivation transitions safely 
        via single field mutations.
        """
        url = f"{self.user_qual_url}{self.historical_qual_mapping.id}/?status=i"
        payload = {'status': 'a'}
        
        response = self.client.patch(url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.historical_mapping.refresh_from_db() if hasattr(self, 'historical_mapping') else self.historical_qual_mapping.refresh_from_db()
        self.assertEqual(self.historical_qual_mapping.status, 'a')

from django.contrib.auth import get_user_model
from courses import models as course_mod
from students import models as student_mod
from assessments import models as assess_mod

class PerformanceAggregationsAPIEndpointTestCase(APITestCase):
    """
    Integration tests for high-performance subqueries and analytical metrics.
    Validates cross-app annotations, parent-state lookups, and distinct counts
    to ensure optimization query barriers remain uncompromised.
    """

    def setUp(self):
        self.base_url = '/teachers/'

        # Setup Analytics Target Teacher
        self.user_faisal = User.objects.create_user(username='dr_faisal_rahman', password='password123')
        self.teacher_faisal = mod.Teacher.objects.create(
            user=self.user_faisal,
            first_name='Faisal',
            last_name='Rahman',
            employee_code='EMP-CS-3022',
            email_institutional='faisal@nitc.ac.in',
            status='a'
        )

        # Setup Student Profiles
        self.user_stu1 = User.objects.create_user(username='asif_ali', password='password123')
        self.student_asif = student_mod.Student.objects.create(
            user=self.user_stu1, first_name='Asif', last_name='Ali',
            date_of_birth=date(2002, 5, 14), gender='m', contact_number='9847012345',
            emergency_contact_name='Ali K', emergency_contact_number='9847054321',
            status='a', date_joined=date(2023, 6, 1)
        )

        self.user_stu2 = User.objects.create_user(username='meera_nair', password='password123')
        self.student_meera = student_mod.Student.objects.create(
            user=self.user_stu2, first_name='Meera', last_name='Nair',
            date_of_birth=date(2003, 9, 21), gender='f', contact_number='9447012345',
            emergency_contact_name='Nair K', emergency_contact_number='9447054321',
            status='a', date_joined=date(2023, 6, 1)
        )

        # Setup Course Infrastructures (Active Published vs Legacy Draft/Archived)
        self.published_course = course_mod.Course.objects.create(
            title='Advanced Machine Learning',
            description='Core research track elective at NIT Calicut',
            status='p' # 'p' = Published
        )
        self.archived_course = course_mod.Course.objects.create(
            title='Introduction to Fortran 77',
            description='Legacy system coursework record',
            status='a' # 'a' = Archived
        )

        # Map Teacher allocations to Course objects
        course_mod.CourseTeachers.objects.create(
            course=self.published_course, teacher=self.teacher_faisal, status='a'
        )
        course_mod.CourseTeachers.objects.create(
            course=self.archived_course, teacher=self.teacher_faisal, status='a'
        )

        # Enroll Students into Active vs Archived Courses
        student_mod.Enrollment.objects.create(
            student=self.student_asif, course=self.published_course, status='a'
        )
        student_mod.Enrollment.objects.create(
            student=self.student_meera, course=self.published_course, status='a'
        )
        # Meera is also enrolled in the inactive course to verify exclusion logic boundaries
        student_mod.Enrollment.objects.create(
            student=self.student_meera, course=self.archived_course, status='a'
        )

        # Establish Assignments & Submissions Context
        self.active_assignment = assess_mod.Assignment.objects.create(
            course=self.published_course, teacher=self.teacher_faisal,
            title='Neural Networks Optimization', status='a'
        )
        self.legacy_assignment = assess_mod.Assignment.objects.create(
            course=self.archived_course, teacher=self.teacher_faisal,
            title='Punch Card Programming Lab', status='a'
        )

        assess_mod.Submission.objects.create(
            assignment=self.active_assignment, student=self.student_asif,
            file_url='https://storage.nitc.ac.in/sub/asif_nn.pdf', status='s' # Submitted
        )

        # Upload Materials (Active vs Archived)
        self.active_material = course_mod.Material.objects.create(
            course=self.published_course, teacher=self.teacher_faisal,
            title='Backpropagation Mathematics Notes', type='d', status='a'
        )
        self.archived_material = course_mod.Material.objects.create(
            course=self.published_course, teacher=self.teacher_faisal,
            title='Obsolete Reference Document', type='d', status='i' # Inactive resource
        )

    def test_get_teachers_with_workload_aggregates_metrics_correctly(self):
        """
        Verify that the with-workload endpoint accurately rolls up multi-table 
        subqueries into optimized structural metrics per teacher profile.
        """
        url = f"{self.base_url}with-workload/"
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Find Dr. Faisal's analytics row from the collection response payload
        target_row = next(item for item in response.data['results'] if item['id'] == self.teacher_faisal.id)
        
        # Verify the database subquery calculations matched our predefined setup boundaries
        self.assertEqual(target_row['total_courses'], 1)       # Only 'Advanced Machine Learning' is status='p'
        self.assertEqual(target_row['total_students'], 2)      # Both Asif and Meera are in that active course
        self.assertEqual(target_row['total_assignments'], 1)   # Excludes the punch card assignment
        self.assertEqual(target_row['pending_submissions'], 1) # Asif's submission requires review

    def test_workload_metrics_exclude_inactive_course_structures(self):
        """
        Ensure metrics are not inflated by soft-deleted or archived course lines.
        If we transition our active course to Archived status, metrics should immediately evaluate to 0.
        """
        self.published_course.status = 'a' # Mutate status to Archived
        self.published_course.save()

        url = f"{self.base_url}with-workload/"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target_row = next(item for item in response.data['results'] if item['id'] == self.teacher_faisal.id)
        
        # All subquery positions must cleanly drop to zero due to Coalesce optimization
        self.assertEqual(target_row['total_courses'], 0)
        self.assertEqual(target_row['total_students'], 0)
        self.assertEqual(target_row['total_assignments'], 0)
        self.assertEqual(target_row['pending_submissions'], 0)

    def test_teacher_courses_endpoint_annotates_distinct_student_reach(self):
        """
        Verify nested courses view performs count tracking optimizations correctly 
        and validates database query safety metrics via CaptureQueriesContext.
        """
        url = f"{self.base_url}{self.teacher_faisal.id}/courses/"
        
        with CaptureQueriesContext(connection=connection) as ctx:
            response = self.client.get(url)
            
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Dr. Faisal has 2 active course mappings, but only 1 points to a Published course
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['student_count'], 2)
        # Ensure query optimization rules are upheld (prevents hidden loops over list records)
        self.assertLessEqual(len(ctx.captured_queries), 4)

    def test_teacher_materials_endpoint_resolves_soft_deleted_resources(self):
        """
        Verify the custom materials details method uses soft-delete manager overrides 
        to accurately pull back archived files when filtering via query strings.
        """
        url = f"{self.base_url}{self.teacher_faisal.id}/materials/?status=i"
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should cleanly swap query scopes to pull back the archived reference document
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Obsolete Reference Document')
