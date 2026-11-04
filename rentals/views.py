
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone

from accounts.models import CustomerProfile
from catalog.models import MovieCopy
from .forms import RentalForm
from .models import Rental, PaymentRecord


@login_required
def rental_history(request):
    customer = get_object_or_404(
        CustomerProfile,
        user=request.user
    )

    rentals = Rental.objects.filter(
        customer=customer
    ).select_related("movie_copy")

    payments = PaymentRecord.objects.filter(
        rental__customer=customer
    ).select_related("rental")

    context = {
        "rentals": rentals,
        "payments": payments,
    }

    return render(
        request,
        "rentals/history.html",
        context
    )


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
def create_rental(request):
    if request.method == "POST":
        form = RentalForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                copy = MovieCopy.objects.select_for_update().get(
                    pk=form.cleaned_data["movie_copy"].pk
                )

                if copy.status != MovieCopy.AvailabilityStatus.AVAILABLE:
                    form.add_error(
                        "movie_copy",
                        "This movie copy is no longer available."
                    )
                else:
                    rental = form.save(commit=False)
                    rental.movie_copy = copy
                    rental.processed_by = request.user
                    rental.status = Rental.RentalStatus.ACTIVE
                    rental.save()

                    copy.status = MovieCopy.AvailabilityStatus.RENTED
                    copy.save(update_fields=["status"])

                    messages.success(
                        request,
                        "Movie rental created successfully!"
                    )
                    return redirect("rentals:create_rental")

    else:
        form = RentalForm()

    return render(
        request,
        "rentals/create_rental.html",
        {"form": form}
    )
