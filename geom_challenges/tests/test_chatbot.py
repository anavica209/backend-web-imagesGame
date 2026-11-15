from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient


class ChatbotAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("geom_challenges.views.get_chat_chain")
    def test_chat_endpoint_returns_a_meaningful_response_for_how_to_play(self, mock_get_chat_chain):
        class DummyChain:
            def run(self, payload):
                return "Claro, para jugar debes observar la figura oculta y adivinar cuál es."

        mock_get_chat_chain.return_value = DummyChain()

        response = self.client.post(
            "/api/chat/",
            {"mensaje": "como juego?", "figura_actual": "cuadrado"},
            format="json",
        )

        self.assertEqual(response.status_code, 200, msg=response.content.decode())

        data = response.json()
        self.assertNotIn("detail", data)
        self.assertIn("respuesta", data)

        response_text = data["respuesta"]
        self.assertTrue(response_text.strip(), "La respuesta del chatbot está vacía")
        self.assertNotIn("error", response_text.lower())
        self.assertNotIn("traceback", response_text.lower())
