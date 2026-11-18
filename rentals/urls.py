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
        "inventory/",
        views.inventory_report,
        name="inventory_report",
    ),
    path(
        "staff/history/",
        views.staff_rental_history_report,
        name="staff_rental_history_report",
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
    path(
        "staff/payments/summary/",
        views.payment_summary_report,
        name="payment_summary_report",
    ),
]
