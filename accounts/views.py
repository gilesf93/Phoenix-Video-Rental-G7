from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
def register(request):
    """Create a new user account using Django's secure authentication form."""
    if request.user.is_authenticated:
        return redirect("core:home")

    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("login")

    return render(request, "accounts/register.html", {"form": form})
