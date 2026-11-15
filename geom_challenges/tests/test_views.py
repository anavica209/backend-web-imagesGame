from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from ..models import ImageTask
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
        self.assertEqual(set(data), {"id", "imageUrl", "options"})
        task = ImageTask.objects.get(pk=data["id"])
        self.assertEqual(self.client.session["current_challenge_id"], data["id"])
        self.assertEqual(len(data["options"]), 4)
        self.assertIn(task.correct_answer, data["options"])

    def test_correct_answer_updates_score_streak_and_returns_next_challenge(self):
        challenge = ImageTask.objects.create(
            correct_answer="square",
            status="completed",
        )
        next_challenge = ImageTask.objects.create(
            correct_answer="circle",
            status="completed",
            image_url="http://localhost:8000/media/circle.png",
        )
        self._set_session(challenge, score=15, streak=2)
        next_options = ["circle", "triangle", "square", "star"]

        with patch(
            "geom_challenges.views._create_challenge",
            return_value=(next_challenge, next_options),
        ):
            response = self.client.post(
                f"/api/challenges/{challenge.pk}/answer/",
                {"answer": "square"},
                format="json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "challengeId": str(challenge.pk),
                "isCorrect": True,
                "feedback": "¡Correcto! Sumas 5 puntos.",
                "scoreDelta": 5,
                "scoreTotal": 20,
                "streak": 3,
                "nextChallenge": {
                    "id": str(next_challenge.pk),
                    "imageUrl": next_challenge.image_url,
                    "options": next_options,
                },
            },
        )
        session = self.client.session
        self.assertEqual(session["current_challenge_id"], str(next_challenge.pk))
        self.assertEqual(session["challenge_score_total"], 20)
        self.assertEqual(session["challenge_streak"], 3)

    def test_incorrect_answer_preserves_score_resets_streak_and_keeps_challenge(self):
        challenge = ImageTask.objects.create(
            correct_answer="square",
            status="completed",
        )
        self._set_session(challenge, score=15, streak=2)

        response = self.client.post(
            f"/api/challenges/{challenge.pk}/answer/",
            {"answer": "circle"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "challengeId": str(challenge.pk),
                "isCorrect": False,
                "feedback": "No es correcto. Inténtalo otra vez.",
                "scoreDelta": 0,
                "scoreTotal": 15,
                "streak": 0,
                "nextChallenge": None,
            },
        )
        session = self.client.session
        self.assertEqual(session["current_challenge_id"], str(challenge.pk))
        self.assertEqual(session["challenge_score_total"], 15)
        self.assertEqual(session["challenge_streak"], 0)

    def test_answer_requires_nonempty_string(self):
        response = self.client.post(
            "/api/challenges/00000000-0000-0000-0000-000000000001/answer/",
            {"answer": ""},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def _set_session(self, challenge, score, streak):
        session = self.client.session
        session["current_challenge_id"] = str(challenge.pk)
        session["challenge_score_total"] = score
        session["challenge_streak"] = streak
        session.save()

    def test_figure_generator_builds_image_for_supported_shape(self):
        """The generator should create an image for a known figure."""
        generator = FiguresGenerator()
        image_bytes = generator.build_image("square", "#2563eb")

        self.assertIsInstance(image_bytes, bytes)
        self.assertGreater(len(image_bytes), 0)
