"""

Module to route definitions for the challenge API.

"""

from django.urls import path

from .views import chat, next_challenge

# Route definitions for the challenge API.
urlpatterns = [
    path("next-challenge/", next_challenge, name="next-challenge"),
    path("chat/", chat, name="chat"),
]
