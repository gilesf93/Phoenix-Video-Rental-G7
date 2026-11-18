from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import CustomerProfile
from catalog.models import Movie, MovieCopy

from .forms import RentalForm
from .models import PaymentRecord, Rental


@login_required
def rental_history(request):
    customer = get_object_or_404(
        CustomerProfile,
        user=request.user,
    )

    rentals = Rental.objects.filter(
        customer=customer,
    ).select_related("movie_copy", "movie_copy__movie")

    payments = PaymentRecord.objects.filter(
        rental__customer=customer,
    ).select_related("rental")

    context = {
        "rentals": rentals,
        "payments": payments,
    }

    return render(request, "rentals/history.html", context)


@staff_member_required
def staff_rental_history_report(request):
    rentals = Rental.objects.select_related(
        "customer",
        "customer__user",
        "movie_copy",
        "movie_copy__movie",
    ).order_by("-rental_date")

    return render(
        request,
        "rentals/staff_rental_history_report.html",
        {"rentals": rentals},
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
@require_POST
def return_rental(request, rental_id):
    with transaction.atomic():
        rental = Rental.objects.select_for_update().filter(pk=rental_id).first()

        if rental is None:
            messages.error(request, "Rental record not found.")
            return redirect("rentals:staff_rental_dashboard")

        if rental.return_date is not None:
            messages.warning(request, "This movie has already been returned.")
            return redirect("rentals:staff_rental_dashboard")

        copy = MovieCopy.objects.select_for_update().get(pk=rental.movie_copy_id)

        if copy.status not in (
            MovieCopy.AvailabilityStatus.RENTED,
            MovieCopy.AvailabilityStatus.DAMAGED,
        ):
            messages.error(
                request,
                "Unable to return this movie due to an invalid inventory status.",
            )
            return redirect("rentals:staff_rental_dashboard")

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

        if copy.status != MovieCopy.AvailabilityStatus.DAMAGED:
            copy.status = MovieCopy.AvailabilityStatus.AVAILABLE
            copy.save(update_fields=["status"])

        messages.success(request, "Movie returned successfully!")

    return redirect("rentals:staff_rental_dashboard")


@staff_member_required
def create_rental(request):
    available_copies = MovieCopy.objects.filter(
        status=MovieCopy.AvailabilityStatus.AVAILABLE
    )

    if not available_copies.exists():
        messages.warning(request, "All movie copies are currently out of stock.")

    if request.method == "POST":
        form = RentalForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                copy = (
                    MovieCopy.objects.select_for_update()
                    .filter(pk=form.cleaned_data["movie_copy"].pk)
                    .first()
                )

                if copy is None:
                    form.add_error("movie_copy", "Movie copy not found.")

                elif copy.status != MovieCopy.AvailabilityStatus.AVAILABLE:
                    form.add_error(
                        "movie_copy", "This movie copy is currently out of stock."
                    )

                elif Rental.objects.filter(
                    movie_copy=copy, return_date__isnull=True
                ).exists():
                    form.add_error(
                        "movie_copy", "This movie copy already has an active rental."
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
                        "Movie rental created successfully!",
                    )

                    return redirect("rentals:create_rental")

        messages.error(
            request, "Unable to process rental. Please review the errors below."
        )

    else:
        form = RentalForm()

    return render(
        request,
        "rentals/create_rental.html",
        {"form": form},
    )


@staff_member_required
def inventory_report(request):
    movies = Movie.objects.annotate(
        total_copies=Count("copies"),
        available_copies=Count(
            "copies",
            filter=Q(copies__status="available"),
        ),
        rented_copies=Count(
            "copies",
            filter=Q(copies__status="rented"),
        ),
        unavailable_copies=Count(
            "copies",
            filter=Q(copies__status="damaged"),
        ),
    )

    copies = MovieCopy.objects.select_related("movie").all()

    total_copies = sum(movie.total_copies for movie in movies)
    available_copies = sum(movie.available_copies for movie in movies)
    rented_copies = sum(movie.rented_copies for movie in movies)
    unavailable_copies = sum(movie.unavailable_copies for movie in movies)

    context = {
        "movies": movies,
        "copies": copies,
        "total_copies": total_copies,
        "available_copies": available_copies,
        "rented_copies": rented_copies,
        "unavailable_copies": unavailable_copies,
    }

    return render(
        request,
        "rentals/inventory_report.html",
        context,
    )


@staff_member_required
def payment_summary_report(request):
    payments = PaymentRecord.objects.select_related(
        "rental", "rental__customer__user", "rental__movie_copy__movie"
    )
    completed_payments = payments.filter(
        payment_status=PaymentRecord.PaymentStatus.COMPLETED
    )
    total_completed = completed_payments.aggregate(total_amount=Sum("amount"))[
        "total_amount"
    ] or Decimal("0.00")

    context = {"payments": payments, "total_completed": total_completed}
    return render(
        request,
        "rentals/payment_summary_report.html",
        context,
    )
