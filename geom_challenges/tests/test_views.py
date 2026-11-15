from django.test import TestCase
from rest_framework.test import APIClient

from ..services.figure_generator import FiguresGenerator


class NextChallengeAPITests(TestCase):
    """Regression tests for the challenge generation endpoint."""

    def setUp(self):
        # Initialize the API test client.
        self.client = APIClient()

    def test_next_challenge_returns_expected_payload(self):
        """Ensure the endpoint returns a valid challenge payload."""
        response = self.client.get("/api/next-challenge/")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.assertIn("imageUrl", data)
        self.assertIn("correctAnswer", data)
        self.assertIn("options", data)
        self.assertEqual(len(data["options"]), 4)
        self.assertIn(data["correctAnswer"], data["options"])

    def test_figure_generator_builds_image_for_supported_shape(self):
        """The generator should create an image for a known figure."""
        generator = FiguresGenerator()
        image_bytes = generator.build_image("square", "#2563eb")

        self.assertIsInstance(image_bytes, bytes)
        self.assertGreater(len(image_bytes), 0)
