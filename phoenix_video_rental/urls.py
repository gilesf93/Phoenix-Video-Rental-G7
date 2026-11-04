from django.urls import path

from . import views

app_name = "rentals"

urlpatterns = [
    path(
        "history/",
        views.rental_history,
        name="rental_history",
    ),
    path(
        "staff/dashboard/",
        views.staff_rental_dashboard,
        name="staff_rental_dashboard",
    ),
    path(
        "staff/create/",
        views.create_rental,
        name="create_rental",
    ),
    path(
        "staff/rentals/<int:rental_id>/return/",
        views.return_rental,
        name="return_rental",
    ),
]
