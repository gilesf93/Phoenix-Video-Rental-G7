from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import CustomerRegistrationForm


@require_http_methods(["GET", "POST"])
def register(request):
    """Create a new customer account with validated registration data."""
    if request.user.is_authenticated:
        return redirect("core:home")

    form = CustomerRegistrationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        customer_group, _ = Group.objects.get_or_create(name="Customer")
        user.groups.add(customer_group)
        return redirect("accounts:login")

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile_view(request):
    return render(
        request,
        "accounts/profile.html",
        {"customer": request.user},
    )
