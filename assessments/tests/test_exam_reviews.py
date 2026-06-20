from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from assessments.models import ExamReviews, Exams, ExamSubmissions
from courses.models import Course
from staffs.models import Teacher
from students.models import Student

User = get_user_model()


class ExamReviewAPITestCase(APITestCase):
    """
    Integration tests for Exam Reviews.
    Validates transactional grading updates, method restrictions, and query safety.
    """

    def setUp(self):
        # Base Setup
        self.user_t = User.objects.create_user(username="prof_lupin", password="123")
        self.teacher = Teacher.objects.create(user=self.user_t, first_name="Filius", last_name="Lupin", status="a")
        self.course = Course.objects.create(title="Defense Against the Dark Arts", status="p")
        self.exam = Exams.objects.create(
            course=self.course,
            title="Boggart Test",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
            total_marks=100,
            status="a",
        )

        self.user_s = User.objects.create_user(username="longbottom_n", password="123")
        self.student = Student.objects.create(
            user=self.user_s,
            first_name="Neville",
            last_name="Longbottom",
            date_of_birth="1980-07-30",
            gender="m",
            contact_number="123",
            emergency_contact_name="Gran",
            emergency_contact_number="911",
            status="a",
            date_joined=date.today(),
        )

        # Target Submission
        self.submission = ExamSubmissions.objects.create(exam=self.exam, student=self.student, status="s")

        self.list_url = reverse("exam-review-list")

    def test_create_review_updates_submission_status(self):
        """Verify POST /exam-reviews/ creates review AND updates exam submission status to 'g'."""
        payload = {
            "exam_submission": self.submission.id,
            "score": 85.00,
            "graded_by": self.teacher.id,
            "feedback": "Riddikulus executed perfectly.",
        }

        response = self.client.post(self.list_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExamReviews.objects.count(), 1)

        # Retrieve submission from database to prove the transaction hook worked
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, "g")

    def test_list_reviews_n_plus_one_safety(self):
        """Verify GET /exam-reviews/ limits queries via select_related."""
        ExamReviews.objects.create(exam_submission=self.submission, score=85.00, graded_by=self.teacher, status="a")

        with CaptureQueriesContext(connection=connection) as ctx:
            response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertLessEqual(len(ctx.captured_queries), 3)

    def test_delete_method_not_allowed(self):
        """Verify DELETE operations are blocked at the routing level."""
        review = ExamReviews.objects.create(
            exam_submission=self.submission, score=85.00, graded_by=self.teacher, status="a"
        )
        detail_url = reverse("exam-review-detail", kwargs={"pk": review.id})

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
