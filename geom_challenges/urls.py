"""

Module to route definitions for the challenge API.

"""

from django.urls import path

from .views import chat, next_challenge, submit_challenge_answer

# Route definitions for the challenge API.
urlpatterns = [
    path("next-challenge/", next_challenge, name="next-challenge"),
    path(
        "challenges/<uuid:challenge_id>/answer/",
        submit_challenge_answer,
        name="submit-challenge-answer",
    ),
    path("chat/", chat, name="chat"),
]
