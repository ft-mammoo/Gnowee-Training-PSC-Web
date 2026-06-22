from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from assessments.models import Exams, ExamSubmissions
from courses.models import Course
from students.models import Student

User = get_user_model()


class ExamSubmissionAPITestCase(APITestCase):
    """
    Integration tests for ExamSubmission endpoints.
    Enforces that only GET (List/Retrieve) and POST (Create) are allowed.
    """

    def setUp(self):
        # 1. Setup Base Infrastructure
        self.user = User.objects.create_user(username="student_hopper", password="password123")
        self.student = Student.objects.create(
            user=self.user,
            first_name="Grace",
            last_name="Hopper",
            date_of_birth="1906-12-09",
            gender="f",
            contact_number="5551234",
            emergency_contact_name="Navy",
            emergency_contact_number="911",
            status="a",
            date_joined=date.today(),  # Fixed NOT NULL constraint here
        )
        self.course = Course.objects.create(
            title="Compiler Design", description="Building the first compiler.", status="p"
        )
        self.exam = Exams.objects.create(
            course=self.course,
            title="Midterm",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2),
            total_marks=100,
            status="a",
        )

        # 2. Setup Target Record
        self.submission = ExamSubmissions.objects.create(exam=self.exam, student=self.student, status="a")

        self.list_url = reverse("exam-submission-list")
        self.detail_url = reverse("exam-submission-detail", kwargs={"pk": self.submission.id})

    def test_list_submissions_success_and_query_optimized(self):
        """Verify GET /exam-submissions/ works and uses select_related to limit queries."""
        # Create a second submission to ensure flat query count
        second_user = User.objects.create_user(username="student_lovelace", password="password123")
        second_student = Student.objects.create(
            user=second_user,
            first_name="Ada",
            last_name="Lovelace",
            date_of_birth="1815-12-10",
            gender="f",
            contact_number="5559876",
            emergency_contact_name="Babbage",
            emergency_contact_number="911",
            status="a",
            date_joined=date.today(),  # Fixed NOT NULL constraint here
        )
        ExamSubmissions.objects.create(exam=self.exam, student=second_student, status="a")

        with CaptureQueriesContext(connection=connection) as ctx:
            response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        # 1 for COUNT(), 1 for the SELECT query (which includes JOINs to user/student/exam)
        self.assertLessEqual(len(ctx.captured_queries), 3)

    def test_create_submission_success(self):
        """Verify POST /exam-submissions/ creates a record."""
        # Note: We must use a different student/exam combo because our constraints block duplicates
        new_exam = Exams.objects.create(
            course=self.course,
            title="Final",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2),
            total_marks=100,
            status="a",
        )
        payload = {"exam": new_exam.id, "student": self.student.id}

        response = self.client.post(self.list_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExamSubmissions.objects.count(), 2)

    def test_retrieve_submission_success(self):
        """Verify GET /exam-submissions/{id}/ works (Retrieve is allowed)."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["student"], self.student.id)

    def test_update_and_delete_methods_not_allowed(self):
        """Verify PUT, PATCH, and DELETE are blocked per API spec."""
        self.assertEqual(self.client.put(self.detail_url, {}).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.patch(self.detail_url, {}).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.delete(self.detail_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_filter_exam_submissions_by_date(self):
        """Verify the newly standardized filterset correctly filters by submission_time."""
        today_str = date.today().strftime("%Y-%m-%d")

        # Fire a GET request with the new model-aligned query parameter
        response = self.client.get(f"{self.list_url}?submission_time={today_str}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assuming the setUp created at least one submission today
        self.assertGreaterEqual(response.data["count"], 1)


class ExamNestedSubmissionsAPITestCase(APITestCase):
    """
    Integration tests specifically for the custom 'submissions' endpoint on ExamViewSet.
    Verifies nested data retrieval, filtering, and N+1 query limits.
    """

    def setUp(self):
        self.course = Course.objects.create(title="Hardware Architecture", status="p")
        self.exam = Exams.objects.create(
            course=self.course,
            title="Final",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2),
            total_marks=100,
            status="a",
        )

        self.stu1 = Student.objects.create(
            user=User.objects.create_user(username="babbage", password="123"),
            first_name="Charles",
            last_name="Babbage",
            date_of_birth="1791-12-26",
            gender="m",
            contact_number="111",
            emergency_contact_name="None",
            emergency_contact_number="911",
            status="a",
            date_joined=date.today(),
        )
        self.stu2 = Student.objects.create(
            user=User.objects.create_user(username="turing", password="123"),
            first_name="Alan",
            last_name="Turing",
            date_of_birth="1912-06-23",
            gender="m",
            contact_number="222",
            emergency_contact_name="None",
            emergency_contact_number="911",
            status="a",
            date_joined=date.today(),
        )

        self.sub1 = ExamSubmissions.objects.create(exam=self.exam, student=self.stu1, status="a")
        self.sub2 = ExamSubmissions.objects.create(exam=self.exam, student=self.stu2, status="a")

        self.nested_url = reverse("exam-submissions", kwargs={"pk": self.exam.id})

    def test_get_nested_submissions_with_n_plus_one_check(self):
        """Verify the endpoint returns all submissions for the exam efficiently."""
        with CaptureQueriesContext(connection=connection) as ctx:
            response = self.client.get(self.nested_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        # 1 COUNT query, 1 SELECT query with JOINs
        self.assertLessEqual(len(ctx.captured_queries), 3)

    def test_nested_submissions_student_filter(self):
        """Verify query parameter filtering isolates a specific student."""
        response = self.client.get(f"{self.nested_url}?student={self.stu1.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["student"], self.stu1.id)

    def test_nested_submissions_date_filter(self):
        """Verify submission_time filtering operates correctly on the date part."""
        today_str = date.today().strftime("%Y-%m-%d")
        response = self.client.get(f"{self.nested_url}?submission_time={today_str}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
