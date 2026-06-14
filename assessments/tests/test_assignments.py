from datetime import date

from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from assessments.models import Assignment, Submission
from courses.models import Course
from staffs.models import Teacher
from students.models import Student

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


class AssignmentPendingSubmissionsAPITestCase(APITestCase):
    """
    Integration tests specifically for the custom 'pending_submissions' endpoint.
    Verifies that graded and inactive records are strictly excluded.
    """

    def setUp(self):
        # 1. Base Setup
        self.teacher_user = User.objects.create_user(username="prof_snape", password="123")
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name="Severus",
            last_name="Snape",
            employee_code="EMP-POT-01",
            email_institutional="snape@edu.com",
            status="a",
        )
        self.course = Course.objects.create(title="Potions", status="p")
        self.assignment = Assignment.objects.create(
            course=self.course, teacher=self.teacher, title="Draft of Peace", status="a"
        )

        # 2. Setup Students
        self.stu1 = Student.objects.create(
            user=User.objects.create_user(username="potter", password="123"),
            first_name="Harry",
            last_name="Potter",
            date_of_birth="1980-07-31",
            gender="m",
            contact_number="111",
            emergency_contact_name="Sirius",
            emergency_contact_number="911",
            status="a",
            date_joined=date.today(),
        )
        self.stu2 = Student.objects.create(
            user=User.objects.create_user(username="granger", password="123"),
            first_name="Hermione",
            last_name="Granger",
            date_of_birth="1979-09-19",
            gender="f",
            contact_number="222",
            emergency_contact_name="Parents",
            emergency_contact_number="911",
            status="a",
            date_joined=date.today(),
        )
        self.stu3 = Student.objects.create(
            user=User.objects.create_user(username="weasley", password="123"),
            first_name="Ron",
            last_name="Weasley",
            date_of_birth="1980-03-01",
            gender="m",
            contact_number="333",
            emergency_contact_name="Molly",
            emergency_contact_number="911",
            status="a",
            date_joined=date.today(),
        )
        self.stu4 = Student.objects.create(
            user=User.objects.create_user(username="malfoy", password="123"),
            first_name="Draco",
            last_name="Malfoy",
            date_of_birth="1980-06-05",
            gender="m",
            contact_number="444",
            emergency_contact_name="Lucius",
            emergency_contact_number="911",
            status="a",
            date_joined=date.today(),
        )

        # 3. Create Submissions with varying statuses
        Submission.objects.create(
            assignment=self.assignment, student=self.stu1, file_url="url1", status="s"
        )  # Submitted
        Submission.objects.create(assignment=self.assignment, student=self.stu2, file_url="url2", status="l")  # Late
        Submission.objects.create(assignment=self.assignment, student=self.stu3, file_url="url3", status="g")  # Graded
        Submission.objects.create(
            assignment=self.assignment, student=self.stu4, file_url="url4", status="i"
        )  # Inactive

        # DRF automatically names the URL pattern based on the function name (replacing underscores with hyphens)
        self.pending_url = reverse("assignment-pending-submissions", kwargs={"pk": self.assignment.id})

    def test_pending_submissions_filters_correctly(self):
        """
        Verify the endpoint returns ONLY 's' and 'l' statuses.
        Validates exclusion of 'g' and 'i', and confirms N+1 constraints.
        """
        with CaptureQueriesContext(connection=connection) as ctx:
            response = self.client.get(self.pending_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should only return Potter ('s') and Granger ('l'). Weasley ('g') and Malfoy ('i') MUST be excluded.
        self.assertEqual(response.data["count"], 2)

        returned_statuses = [sub["status"] for sub in response.data["results"]]
        self.assertIn("s", returned_statuses)
        self.assertIn("l", returned_statuses)
        self.assertNotIn("g", returned_statuses)
        self.assertNotIn("i", returned_statuses)

        # Query limit check: 1 for count, 1 for data + select_related
        self.assertLessEqual(len(ctx.captured_queries), 3)
