from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone

from .models import Rental


@staff_member_required
def staff_rental_dashboard(request):
    today = timezone.localdate()

    active_rentals = Rental.objects.filter(
        return_date__isnull=True,
        due_date__gte=today,
    ).select_related("customer", "movie_copy")

    overdue_rentals = Rental.objects.filter(
        return_date__isnull=True,
        due_date__lt=today,
    ).select_related("customer", "movie_copy")

    context = {
        "active_rentals": active_rentals,
        "overdue_rentals": overdue_rentals,
    }

    return render(
        request,
        "rentals/staff_rental_dashboard.html",
        context,
    )
