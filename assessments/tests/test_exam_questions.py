from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from assessments.models import ExamQuestions, ExamQuestionsMapping, Exams, QuestionCategories
from courses.models import Course

User = get_user_model()


class ExamQuestionsMappingAPITestCase(APITestCase):
    """
    Integration tests for Exam Question Mapping management.
    Focuses on the custom DELETE action for decoupling questions from exams.
    """

    def setUp(self):
        # 1. Base Setup
        self.course = Course.objects.create(title="Algorithms", status="p")
        self.exam = Exams.objects.create(
            course=self.course,
            title="Final",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2),
            total_marks=100,
            status="a",
        )
        self.category = QuestionCategories.objects.create(name="Sorting", status="a")
        self.question = ExamQuestions.objects.create(
            category=self.category, question_text="O(n log n)?", question_type="t", marks=5.0, status="a"
        )

        # 2. Create Active Mapping
        self.mapping = ExamQuestionsMapping.objects.create(exam=self.exam, question=self.question, status="a")

    def test_remove_question_success(self):
        """
        Verify DELETE /exams/{id}/questions/{question_id}/ executes a soft-delete.
        """
        # We manually construct the URL since DRF dynamic @action regex URLs can be tricky to reverse()
        url = f"/exams/{self.exam.id}/questions/{self.question.id}/"

        with CaptureQueriesContext(connection=connection) as ctx:
            response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify it was soft-deleted, not hard-deleted
        self.mapping.refresh_from_db()
        self.assertEqual(self.mapping.status, "i")

        # Optimization check: 1 to look up mapping, 1 to UPDATE status
        self.assertLessEqual(len(ctx.captured_queries), 3)

    def test_remove_question_not_found(self):
        """
        Verify providing a non-existent question ID returns a 404.
        """
        url = f"/exams/{self.exam.id}/questions/9999/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Active mapping not found for this exam and question.")

    def test_remove_question_already_inactive(self):
        """
        Verify trying to delete an already inactive mapping returns a 404.
        """
        # Soft-delete it first
        self.mapping.status = "i"
        self.mapping.save()

        url = f"/exams/{self.exam.id}/questions/{self.question.id}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
