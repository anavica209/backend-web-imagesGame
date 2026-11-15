"""

Module to represent Image challenge tasks.

"""

import uuid
from django.db import models


class ImageTask(models.Model):
    """Represents a single generated geometry challenge task."""
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    # Unique identifier for each generated challenge.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # The algorithm or prompt used to generate the challenge.
    prompt = models.CharField(max_length=255, blank=True, default="")
    # Current lifecycle state of the task.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    # The correct geometry name expected by the user.
    correct_answer = models.CharField(max_length=100, blank=True, default="")
    # Stored generated image for the challenge.
    image_file = models.ImageField(upload_to="challenges/", blank=True, null=True)
    # Public URL pointing to the generated image.
    image_url = models.URLField(max_length=500, blank=True, default="")

    def __str__(self) -> str:
        """Return a readable representation of the task."""
        return str(self.id)
