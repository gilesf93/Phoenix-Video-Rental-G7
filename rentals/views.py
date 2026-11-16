from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Q

from accounts.models import CustomerProfile
from catalog.models import Movie
from .models import Rental, PaymentRecord
from catalog.models import Movie, MovieCopy


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
def inventory_report(request):
    movies = Movie.objects.annotate(
        total_copies=Count("copies"),
        available_copies=Count(
            "copies",
            filter=Q(copies__status="available")
        ),
        rented_copies=Count(
            "copies",
            filter=Q(copies__status="rented")
        ),
        unavailable_copies=Count(
            "copies",
            filter=Q(copies__status="damaged")
        ),
    )

    copies = MovieCopy.objects.select_related("movie").all()

    total_copies = sum(m.total_copies for m in movies)
    available_copies = sum(m.available_copies for m in movies)
    rented_copies = sum(m.rented_copies for m in movies)
    unavailable_copies = sum(m.unavailable_copies for m in movies)

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
        context
    )
