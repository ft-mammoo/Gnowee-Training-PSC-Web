from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from assessments.models import QuestionCategories


class QuestionCategoryAPITestCase(APITestCase):
    """
    Integration tests for QuestionCategory endpoints.
    Enforces that only GET (List) and POST (Create) are allowed.
    """

    def setUp(self):
        # 1. Setup Base Infrastructure
        self.category1 = QuestionCategories.objects.create(
            name="Advanced Mathematics", description="Calculus and linear algebra concepts.", status="a"
        )
        self.category2 = QuestionCategories.objects.create(
            name="Physics", description="Quantum mechanics.", status="a"
        )

        # Only the list URL exists now because we stripped the detail mixins
        self.list_url = reverse("question-category-list")

    def test_list_categories_success_and_query_optimized(self):
        """Verify GET /question-categories/ works and limits queries."""
        with CaptureQueriesContext(connection=connection) as ctx:
            response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        # Only 2 queries should run: 1 for COUNT(), 1 for the SELECT query
        self.assertLessEqual(len(ctx.captured_queries), 2)

    def test_create_category_success(self):
        """Verify POST /question-categories/ creates a record."""
        payload = {"name": "Chemistry", "description": "Organic and inorganic chemistry."}

        response = self.client.post(self.list_url, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(QuestionCategories.objects.count(), 3)
        self.assertEqual(response.data["name"], "Chemistry")

    def test_detail_routes_are_disabled(self):
        """
        Verify that detail routes (GET, PUT, PATCH, DELETE) do not exist.
        Because we removed Retrieve, Update, and Destroy mixins,
        the DRF Router physically does not create the /{id}/ route.
        """
        # We must manually construct the URL string because reverse() will fail
        detail_url = f"/question-categories/{self.category1.id}/"

        # Since the route doesn't exist at all, Django resolves this as 404 Not Found
        self.assertEqual(self.client.get(detail_url).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.put(detail_url, {}).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.patch(detail_url, {}).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.delete(detail_url).status_code, status.HTTP_404_NOT_FOUND)

        # Ensure the record was NOT actually deleted
        self.category1.refresh_from_db()
        self.assertEqual(self.category1.status, "a")
