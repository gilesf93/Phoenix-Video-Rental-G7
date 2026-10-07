from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render


def home(request):
    return render(request, "core/home.html")


@login_required
def staff_dashboard(request):
    is_staff_role = request.user.groups.filter(name__in=["Admin", "Employee"]).exists()
    if not is_staff_role:
        raise PermissionDenied("You do not have permission to access this page.")

    return render(request, "core/staff_dashboard.html")


@login_required
def admin_dashboard(request):
    is_admin = request.user.groups.filter(name="Admin").exists()
    if not is_admin:
        raise PermissionDenied("You do not have permission to access this page.")

    return render(request, "core/admin_dashboard.html")
