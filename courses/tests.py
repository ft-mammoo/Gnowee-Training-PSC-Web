import uuid
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.contrib.auth import get_user_model
from datetime import date

from courses.models import Course, CourseTeachers
from staffs.models import Teacher
from students.models import Student, Enrollment

User = get_user_model()

# --- 2.1 TESTS ---
class CourseAPITests(APITestCase):
    def setUp(self):
        # Initial data for testing
        self.course = Course.objects.create(
            title="Django API Mastery",
            description="Professional REST API development",
            status="p"
        )
        self.list_url = reverse('course-list')
        self.detail_url = reverse('course-detail', kwargs={'pk': self.course.pk})

    def test_get_course_list(self):
        """Test GET /courses/ returns list of courses"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # We check the 'count' key provided by the paginator
        self.assertEqual(response.data['count'], 1)
        
        # We check the length of the 'results' list
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], self.course.title)

    def test_create_course(self):
        """Test POST /courses/ creates a new course"""
        data = {
            "title": "React UI Engineering",
            "description": "Modern frontend architecture",
            "status": "p"
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)
        self.assertEqual(Course.objects.last().title, "React UI Engineering")

    def test_get_course_detail(self):
        """Test GET /courses/{id}/ returns specific course"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.course.title)

    def test_update_course_full(self):
        """Test PUT /courses/{id}/ updates all fields"""
        data = {
            "title": "Updated Title",
            "description": "Updated Description",
            "status": "a"
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Updated Title")

    def test_update_course_partial(self):
        """Test PATCH /courses/{id}/ updates single field"""
        data = {"title": "Partial Update"}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Partial Update")

    def test_delete_course(self):
        """Test DELETE /courses/{id}/ removes record"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.count(), 0)


# --- 2.2 TESTS (NESTED ENDPOINTS) ---
class CourseNestedAPITests(APITestCase):
    def setUp(self):
        self.course = Course.objects.create(title="Backend Sprint", status="p")
        self.user = User.objects.create_user(username="sofia_r", password="password123")
        self.teacher = Teacher.objects.create(
            user=self.user,
            first_name="Sofia",
            last_name="Rossi",
            gender="f",
            employee_code="EMP001",
            experience_years=8,
            email_institutional="sofia@edu.com",
            status="a",
            date_joined=date.today()
        )
        self.teachers_url = reverse('course-teachers', kwargs={'pk': self.course.pk})

    def test_get_teachers_sql_performance(self):
        """Test GET /courses/{id}/teachers/ and print SQL queries to catch N+1"""
        # Create 3 links to check if queries scale with data size (N+1 check)
        CourseTeachers.objects.create(course=self.course, teacher=self.teacher, status='a')
        
        print(f"\n--- SQL Queries for GET {self.teachers_url} ---")
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.teachers_url)
            
            for i, query in enumerate(ctx.captured_queries, 1):
                print(f"Query {i}: {query['sql']}\n")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(ctx), 3, "Potential N+1 query detected!")

    def test_post_teacher_assignment(self):
        """Test POST /courses/{id}/teachers/ link creation"""
        payload = {"teacher": self.teacher.id, "status": "a"}
        response = self.client.post(self.teachers_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CourseTeachers.objects.filter(course=self.course, teacher=self.teacher).exists())

# --- 2.2 STUDENTS NESTED ENDPOINT TESTS ---
class CourseStudentsNestedTests(APITestCase):
    def setUp(self):
        unique_suffix = str(uuid.uuid4())[:8]
        self.course = Course.objects.create(title=f"Backend Sprint {unique_suffix}", status="p")
        self.user = User.objects.create_user(username=f"sofia_{unique_suffix}", password="password123")
        self.teacher = Teacher.objects.create(
            user=self.user,
            first_name="Sofia",
            last_name="Rossi",
            gender="f",
            employee_code=f"EMP_{unique_suffix}",
            experience_years=8,
            email_institutional=f"sofia_{unique_suffix}@edu.com",
            status="a",
            date_joined=date.today()
        )
        self.teachers_url = reverse('course-teachers', kwargs={'pk': self.course.pk})
        
        # Requirement: pagination_size=30
        # We create 35 students to verify that only 30 appear per page
        for i in range(35):
            s_user = User.objects.create_user(username=f"student_{i}", password="password123")
            student = Student.objects.create(
                user=s_user,
                first_name=f"First_{i}",
                last_name=f"Last_{i}",
                date_of_birth="2000-01-01",
                gender='m',
                contact_number="1234567890",
                emergency_contact_name="Emergency Name",
                emergency_contact_number="0987654321",
                date_joined=date.today()
            )
            # Link each student to this specific course
            Enrollment.objects.create(student=student, course=self.course, status='a')

        self.students_url = reverse('course-students', kwargs={'pk': self.course.pk})

    def test_get_students_structure_and_performance(self):
        """Verify optimized query count and nested JSON structure"""
        print(f"\n--- SQL Queries for Students Endpoint ---")
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.students_url)
            
            for i, query in enumerate(ctx.captured_queries, 1):
                print(f"Query {i}: {query['sql']}\n")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify pagination: should be 30 results on page 1
        self.assertEqual(len(response.data['results']), 30)
        self.assertEqual(response.data['count'], 35)

        # Verify nested enrollment structure matches documentation
        # Example: {"id": 1, ..., "enrollment": {"id": 12, "status": "a", ...}}
        first_student = response.data['results'][0]
        self.assertIn('enrollment', first_student)
        self.assertIn('enrollment_date', first_student['enrollment'])
        
        # Verify N+1 check: Expect ~3-4 queries (Course, Students, Prefetched Enrollments)
        self.assertLessEqual(len(ctx), 4, "High query count detected! Check Prefetch logic.")

    def test_students_search_logic(self):
        """Verify search: first_name, last_name"""
        # Search for the 10th student by last name
        url = f"{self.students_url}?search=10"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only find the student with "Last_10"
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['last_name'], "Last_10")

from courses.models import Material

class CourseMaterialsTests(APITestCase):
    def setUp(self):
        self.unique_suffix = str(uuid.uuid4())[:8]
        
        # Setup Course and Teacher
        self.course = Course.objects.create(title=f"Global Course {self.unique_suffix}", status='p')
        self.user = User.objects.create_user(username=f"staff_{self.unique_suffix}", password="p123")
        self.teacher = Teacher.objects.create(
            user=self.user,
            employee_code=f"E_{self.unique_suffix}",
            email_institutional=f"staff_{self.unique_suffix}@edu.com",
            status='a'
        )
        
        self.materials_url = reverse('material-list')

    def test_get_materials_performance_and_pagination(self):
        # Create 35 materials (should trigger 2 pages since page_size=30)
        materials = [
            Material(
                course=self.course,
                teacher=self.teacher,
                title=f"Material {i}",
                file_url=f"http://example.com/file{i}.pdf",
                type="d",
                status="a"
            ) for i in range(35)
        ]
        Material.objects.bulk_create(materials)

        print(f"\n--- SQL Queries for Global GET {self.materials_url} ---")
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.materials_url)
            
            for i, query in enumerate(ctx.captured_queries, 1):
                print(f"Query {i}: {query['sql']}\n")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify Pagination: Page 1 should have exactly 30 results
        self.assertEqual(len(response.data['results']), 30)
        self.assertEqual(response.data['count'], 35)

        # Verify SQL: Expect ~2-3 queries (1 for Count, 1 for Data with JOINS)
        # Without select_related, this would be 30+ queries.
        self.assertLessEqual(len(ctx), 3, "N+1 query detected on top-level materials list!")

    def test_material_search_and_filters(self):
        # Create a specific material to find
        target = Material.objects.create(
            course=self.course,
            teacher=self.teacher,
            title="Unique Target Title",
            description="Find me",
            type="v",
            status="a"
        )
        
        # Test Search
        response = self.client.get(f"{self.materials_url}?search=Unique")
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], target.id)
        
        # Test Filter (type)
        response = self.client.get(f"{self.materials_url}?type=v")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) > 0)
        self.assertEqual(response.data['results'][0]['type'], "v")

    def test_post_material_success(self):
        """Verify successful material creation and file_url handling"""
        payload = {
            "course": self.course.id,
            "teacher": self.teacher.id,
            "title": "New Lecture Slides",
            "description": "Introduction to DRF",
            "file_url": "http://example.com/slides.pdf",
            "type": "s",
            "status": "a"
        }
        
        # We expect exactly 2 for FK validation + 1 for INSERT
        with self.assertNumQueries(3): # Adjust number based on your specific validation logic
            response = self.client.post(self.materials_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Material.objects.count(), 1)
        self.assertEqual(response.data['title'], "New Lecture Slides")

    def test_post_material_invalid_course(self):
        """Edge Case: Ensure creation fails with a non-existent course ID"""
        payload = {
            "course": 9999, # Non-existent ID
            "teacher": self.teacher.id,
            "title": "Ghost Material",
            "file_url": "http://example.com/ghost.pdf",
            "type": "d",
            "status": "a"
        }
        response = self.client.post(self.materials_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('course', response.data)
        # Verify no material was accidentally created
        self.assertEqual(Material.objects.count(), 0)

    def test_get_material_detail_success(self):
        """Verify material detail view with nested data and optimized SQL"""
        material = Material.objects.create(
            course=self.course,
            teacher=self.teacher,
            title="Detail Test Material",
            file_url="http://example.com/detail.pdf",
            type="d",
            status="a"
        )
        url = reverse('material-detail', kwargs={'pk': material.pk})
        
        # Should be exactly 1 query due to select_related in the ViewSet queryset
        with self.assertNumQueries(1):
            response = self.client.get(url)
            
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Detail Test Material")
        # Verify nested data is present (from MaterialListSerializer)
        self.assertEqual(response.data['teacher']['id'], self.teacher.id)
        self.assertEqual(response.data['course']['title'], self.course.title)

    def test_get_material_detail_404(self):
        """Verify 404 response for non-existent material ID"""
        url = reverse('material-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
