from datetime import date

from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from assessments.models import Assignment, Submission, SubmissionGrade
from courses.models import Course
from staffs.models import Teacher
from students.models import Student

User = get_user_model()


class SubmissionGradeAPITestCase(APITestCase):
    """
    Integration tests for Submission Grades.
    Validates transactional status updates, N+1 query limits, and method restrictions.
    """

    def setUp(self):
        # Base Setup
        self.user_t = User.objects.create_user(username="prof_flitwick", password="123")
        self.teacher = Teacher.objects.create(user=self.user_t, first_name="Filius", last_name="Flitwick", status="a")
        self.course = Course.objects.create(title="Charms", status="p")
        self.assignment = Assignment.objects.create(
            course=self.course, teacher=self.teacher, title="Levitation Charm", status="a"
        )

        self.user_s = User.objects.create_user(username="granger_h", password="123")
        self.student = Student.objects.create(
            user=self.user_s,
            first_name="Hermione",
            last_name="Granger",
            date_of_birth="1979-09-19",
            gender="f",
            contact_number="123",
            emergency_contact_name="Parents",
            emergency_contact_number="911",
            status="a",
            date_joined=date.today(),
        )

        # Target Submission
        self.submission = Submission.objects.create(
            assignment=self.assignment, student=self.student, file_url="url1", status="s"
        )

        self.list_url = reverse("submission-grade-list")

    def test_create_grade_updates_submission_status(self):
        """Verify POST /submission-grades/ creates grade AND updates submission status to 'g'."""
        payload = {
            "submission": self.submission.id,
            "grade": 98.50,
            "graded_by": self.teacher.id,
            "feedback": "Swish and flick executed perfectly.",
        }

        response = self.client.post(self.list_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SubmissionGrade.objects.count(), 1)

        # Retrieve submission from database to prove the perform_create hook worked
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, "g")

    def test_list_grades_n_plus_one_safety(self):
        """Verify GET /submission-grades/ works and uses select_related limits queries."""
        SubmissionGrade.objects.create(submission=self.submission, grade=95.00, graded_by=self.teacher, status="a")

        with CaptureQueriesContext(connection=connection) as ctx:
            response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertLessEqual(len(ctx.captured_queries), 3)

    def test_delete_method_not_allowed(self):
        """Verify DELETE operations are completely blocked by the API routing."""
        grade = SubmissionGrade.objects.create(
            submission=self.submission, grade=95.00, graded_by=self.teacher, status="a"
        )
        detail_url = reverse("submission-grade-detail", kwargs={"pk": grade.id})

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
