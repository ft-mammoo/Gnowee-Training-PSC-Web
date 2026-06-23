from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError, connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from assessments.models import Assignment, Exams, ExamSubmissions, Submission
from courses.models import Course
from staffs.models import Teacher
from students.models import Student

User = get_user_model()


class SubmissionAPITestCase(APITestCase):
    """
    Integration tests for Assignment Submissions.
    Validates CRUD operations, deadline blocking, update locks, and query optimization.
    """

    def setUp(self):
        # Base Setup
        self.user_t = User.objects.create_user(username="prof_mcgonagall", password="123")
        self.teacher = Teacher.objects.create(
            user=self.user_t, first_name="Minerva", last_name="McGonagall", status="a"
        )
        self.course = Course.objects.create(title="Transfiguration", status="p")

        self.user_s = User.objects.create_user(username="weasley_r", password="123")
        self.student = Student.objects.create(
            user=self.user_s,
            first_name="Ron",
            last_name="Weasley",
            date_of_birth="1980-03-01",
            gender="m",
            contact_number="123",
            emergency_contact_name="Molly",
            emergency_contact_number="911",
            status="a",
            date_joined=date.today(),
        )

        # Assignments (One Future, One Past)
        self.active_assignment = Assignment.objects.create(
            course=self.course,
            teacher=self.teacher,
            title="Turn beetle into button",
            due_date=date.today() + timedelta(days=7),
            status="a",
        )
        self.expired_assignment = Assignment.objects.create(
            course=self.course,
            teacher=self.teacher,
            title="Match to needle",
            due_date=date.today() - timedelta(days=7),
            status="a",
        )

        # Submissions (One Active, One Graded)
        self.active_sub = Submission.objects.create(
            assignment=self.active_assignment, student=self.student, file_url="url1", status="s"
        )
        self.graded_sub = Submission.objects.create(
            assignment=self.expired_assignment, student=self.student, file_url="url2", status="g"
        )

        # URLs
        self.list_url = reverse("submission-list")
        self.active_detail_url = reverse("submission-detail", kwargs={"pk": self.active_sub.id})
        self.graded_detail_url = reverse("submission-detail", kwargs={"pk": self.graded_sub.id})

    def test_database_structural_integrity_unique_submission(self):
        """Verify that a student cannot have multiple active submissions for the same assignment."""
        with self.assertRaises(IntegrityError):
            Submission.objects.create(
                assignment=self.active_assignment, student=self.student, file_url="duplicate_hacked_url", status="s"
            )

    def test_database_read_optimization_indexes(self):
        """Verify that critical filtering fields are mathematically indexed at the database level."""
        self.assertTrue(Submission._meta.get_field("status").db_index)
        self.assertTrue(Submission._meta.get_field("submitted_date").db_index)
        self.assertTrue(Assignment._meta.get_field("due_date").db_index)
        self.assertTrue(Exams._meta.get_field("start_time").db_index)
        self.assertTrue(Exams._meta.get_field("end_time").db_index)
        self.assertTrue(ExamSubmissions._meta.get_field("submission_time").db_index)

    def test_list_submissions_n_plus_one_safety(self):
        """Verify GET /submissions/ works and uses select_related to limit queries."""
        with CaptureQueriesContext(connection=connection) as ctx:
            response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        # 1 COUNT query, 1 SELECT query with JOINs
        self.assertLessEqual(len(ctx.captured_queries), 3)

    def test_filter_submissions_by_date(self):
        """Verify django-filters successfully parses the submitted_date param."""
        today_str = date.today().strftime("%Y-%m-%d")
        response = self.client.get(f"{self.list_url}?submitted_date={today_str}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)

    def test_create_submission_success(self):
        """Verify POST /submissions/ works for an active assignment."""
        new_assignment = Assignment.objects.create(
            course=self.course,
            teacher=self.teacher,
            title="New task",
            due_date=date.today() + timedelta(days=7),
            status="a",
        )
        payload = {
            "assignment": new_assignment.id,
            "student": self.student.id,
            "file_url": "new_url",
            "status": "s",
        }
        response = self.client.post(self.list_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_submission_deadline_passed(self):
        """Verify POST /submissions/ is blocked if assignment is past due."""
        # Create a brand new expired assignment so we don't trip the unique constraint on self.expired_assignment
        new_expired = Assignment.objects.create(
            course=self.course,
            teacher=self.teacher,
            title="Old task",
            due_date=date.today() - timedelta(days=7),
            status="a",
        )
        payload = {
            "assignment": new_expired.id,
            "student": self.student.id,
            "file_url": "late_url",
            "status": "s",
        }
        response = self.client.post(self.list_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Submission deadline has passed.")

    def test_update_active_submission_success(self):
        """Verify PATCH /submissions/{id}/ works for ungraded items."""
        # DRF's UniqueConstraintValidator requires condition fields to be present in the validation context
        payload = {
            "file_url": "updated_url",
            "status": "s",
            "assignment": self.active_assignment.id,
            "student": self.student.id,
        }
        response = self.client.patch(self.active_detail_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["file_url"], "updated_url")

    def test_update_graded_submission_blocked(self):
        """Verify PATCH /submissions/{id}/ is blocked if status is 'g'."""
        payload = {"file_url": "hacked_url"}
        response = self.client.patch(self.graded_detail_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Cannot update a graded submission.")

    def test_delete_active_submission_success(self):
        """Verify DELETE /submissions/{id}/ works for ungraded items."""
        response = self.client.delete(self.active_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Submission.objects.count(), 1)

    def test_delete_graded_submission_blocked(self):
        """Verify DELETE /submissions/{id}/ is blocked if status is 'g'."""
        response = self.client.delete(self.graded_detail_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Cannot delete a graded submission.")
