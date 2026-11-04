from django.urls import path
from . import views

app_name = "rentals"

urlpatterns = [
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
]
