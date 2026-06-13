from datetime import date

from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from assessments.models import Assignment
from courses.models import Course
from staffs.models import Teacher

User = get_user_model()


class AssignmentAPITestCase(APITestCase):
    """
    Integration tests for Assignment endpoints.
    Enforces N+1 query safety and validates standard CRUD operations.
    """

    def setUp(self):
        # 1. Setup Base Infrastructure
        self.user = User.objects.create_user(username="prof_turing", password="securepassword123")
        self.teacher = Teacher.objects.create(
            user=self.user,
            first_name="Alan",
            last_name="Turing",
            gender="m",
            employee_code="EMP-CS-001",
            experience_years=10,
            email_institutional="turing@edu.com",
            status="a",
        )
        self.course = Course.objects.create(
            title="Advanced Cryptography", description="Enigma and beyond.", status="p"
        )

        # 2. Setup Target Record
        self.assignment = Assignment.objects.create(
            course=self.course,
            teacher=self.teacher,
            title="Enigma Decoding",
            description="Build a programmatic decoder.",
            due_date=date(2026, 12, 31),
            status="a",
        )

        # 3. URL configurations (Assuming router registers as 'assignment')
        self.list_url = reverse("assignment-list")
        self.detail_url = reverse("assignment-detail", kwargs={"pk": self.assignment.id})

    def test_list_assignments_enforces_n_plus_one_safety(self):
        """
        Verify the list endpoint successfully retrieves data and
        maintains a strict query count to prevent N+1 database leaks.
        """
        # Create a second assignment to ensure query count remains flat
        Assignment.objects.create(
            course=self.course,
            teacher=self.teacher,
            title="Turing Machine Theory",
            description="Write a paper on tape computation.",
            due_date=date(2026, 11, 30),
            status="a",
        )

        with CaptureQueriesContext(connection=connection) as ctx:
            response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        # Verify query optimization: 1 for count, 1 for records (with select_related/prefetch joins)
        self.assertLessEqual(len(ctx.captured_queries), 3)

    def test_create_assignment_success(self):
        """Verify successful creation of a new assignment via POST payload."""
        payload = {
            "course": self.course.id,
            "teacher": self.teacher.id,
            "title": "Machine Learning Basics",
            "description": "Intro to neural networks.",
            "due_date": "2026-10-15",
        }

        response = self.client.post(self.list_url, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Assignment.objects.count(), 2)
        self.assertEqual(response.data["title"], "Machine Learning Basics")

    def test_retrieve_assignment_detail(self):
        """Verify fetching a specific assignment by ID."""
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Enigma Decoding")

    def test_update_assignment_partial(self):
        """Verify PATCH updates specific fields while retaining others."""
        payload = {"title": "Updated Enigma Decoding"}

        response = self.client.patch(self.detail_url, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.title, "Updated Enigma Decoding")

    def test_delete_assignment_soft_deletes(self):
        """Verify DELETE operations execute a soft-delete (status='i')."""
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status, "i")
