from django.test import TestCase

from ..models import ImageTask


class ImageTaskModelTests(TestCase):
    def test_default_values_are_persisted(self):
        task = ImageTask.objects.create()
        task.refresh_from_db()

        self.assertEqual(task.status, "pending")
        self.assertEqual(task.prompt, "")
        self.assertEqual(task.correct_answer, "")
