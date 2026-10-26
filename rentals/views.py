from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

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


@staff_member_required
@require_POST
def return_rental(request, rental_id):
    rental = get_object_or_404(
        Rental,
        pk=rental_id,
        return_date__isnull=True,
    )

    rental.return_date = timezone.now()
    rental.status = Rental.RentalStatus.RETURNED
    rental.processed_by = request.user
    rental.save(
        update_fields=[
            "return_date",
            "status",
            "processed_by",
        ]
    )

    return redirect("rentals:staff_rental_dashboard")
