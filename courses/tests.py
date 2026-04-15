from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from courses.models import Course

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