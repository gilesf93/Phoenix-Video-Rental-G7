
from django.urls import path
from . import views

app_name = "rentals"

urlpatterns = [
    path(
        "history/",
        views.rental_history,
        name="rental_history",
    ),
]
