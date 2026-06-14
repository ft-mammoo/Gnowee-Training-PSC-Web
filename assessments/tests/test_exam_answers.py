from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from assessments.models import ExamAnswers, ExamQuestions, Exams, ExamSubmissions, QuestionCategories
from courses.models import Course
from students.models import Student

User = get_user_model()


class ExamAnswerAPITestCase(APITestCase):
    """
    Integration tests for ExamAnswer endpoints.
    Enforces that ONLY POST (Create) is allowed per API spec.
    """

    def setUp(self):
        # 1. Setup Base Infrastructure
        self.user = User.objects.create_user(username="student_turing", password="123")
        self.student = Student.objects.create(
            user=self.user,
            first_name="Alan",
            last_name="Turing",
            date_of_birth="1912-06-23",
            gender="m",
            contact_number="123",
            emergency_contact_name="None",
            emergency_contact_number="911",
            status="a",
            date_joined=date.today(),
        )
        self.course = Course.objects.create(title="Logic", status="p")
        self.exam = Exams.objects.create(
            course=self.course,
            title="Final",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2),
            total_marks=100,
            status="a",
        )
        self.submission = ExamSubmissions.objects.create(exam=self.exam, student=self.student, status="a")

        self.category = QuestionCategories.objects.create(name="Math", status="a")
        self.question = ExamQuestions.objects.create(
            category=self.category, question_text="1+1?", question_type="t", marks=10.00, status="a"
        )

        # 2. URL configurations
        self.list_url = reverse("exam-answer-list")

    def test_create_answer_success(self):
        """Verify POST /exam-answers/ creates a record successfully."""
        payload = {"exam_submission": self.submission.id, "question": self.question.id, "answer_text": "2"}
        response = self.client.post(self.list_url, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExamAnswers.objects.count(), 1)
        self.assertEqual(response.data["answer_text"], "2")

    def test_list_method_not_allowed(self):
        """
        Verify GET /exam-answers/ is blocked.
        Because we omitted ListModelMixin, the router makes the URL but blocks GET.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_detail_routes_are_disabled(self):
        """
        Verify that detail routes (GET, PUT, PATCH, DELETE) do not exist.
        Because Retrieve, Update, and Destroy mixins are removed,
        the DRF Router physically does not create the /{id}/ route.
        """
        answer = ExamAnswers.objects.create(
            exam_submission=self.submission, question=self.question, answer_text="1", status="a"
        )

        # We must manually construct the URL string because reverse() will fail for missing routes
        detail_url = f"/exam-answers/{answer.id}/"

        self.assertEqual(self.client.get(detail_url).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.put(detail_url, {}).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.patch(detail_url, {}).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.delete(detail_url).status_code, status.HTTP_404_NOT_FOUND)
