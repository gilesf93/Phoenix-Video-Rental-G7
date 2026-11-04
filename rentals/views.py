from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from accounts.models import CustomerProfile
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
