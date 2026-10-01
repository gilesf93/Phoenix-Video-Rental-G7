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
        form.save()
        return redirect("login")

    return render(request, "accounts/register.html", {"form": form})
