
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import CustomerRegistrationForm, StaffCustomerForm

User = get_user_model()


@require_http_methods(["GET", "POST"])
def register(request):
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
        "profile.html",
        {"customer": request.user},
    )


@staff_member_required
def staff_customers(request):
    query = request.GET.get("q", "").strip()

    customers = User.objects.filter(
        groups__name="Customer"
    ).distinct()

    if query:
        customers = customers.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
        )

    return render(
        request,
        "accounts/staff_customers.html",
        {"customers": customers, "query": query},
    )


@staff_member_required
@require_http_methods(["GET", "POST"])
def staff_customer_create(request):
    if request.method == "POST":
        form = StaffCustomerForm(request.POST)

        if form.is_valid():
            customer = form.save()
            customer_group, _ = Group.objects.get_or_create(name="Customer")
            customer.groups.add(customer_group)
            return redirect("accounts:staff_customers")
    else:
        form = StaffCustomerForm()

    return render(
        request,
        "accounts/staff_customer_form.html",
        {"form": form, "title": "Add Customer"},
    )


@staff_member_required
@require_http_methods(["GET", "POST"])
def staff_customer_update(request, user_id):
    customer = get_object_or_404(
        User.objects.filter(groups__name="Customer").distinct(),
        pk=user_id,
    )

    if request.method == "POST":
        form = StaffCustomerForm(request.POST, instance=customer)

        if form.is_valid():
            form.save()
            return redirect("accounts:staff_customers")
    else:
        form = StaffCustomerForm(instance=customer)

    return render(
        request,
        "accounts/staff_customer_form.html",
        {"form": form, "title": "Edit Customer"},
    )


@staff_member_required
@require_http_methods(["GET", "POST"])
def staff_customer_delete(request, user_id):
    customer = get_object_or_404(
        User.objects.filter(groups__name="Customer").distinct(),
        pk=user_id,
    )

    if request.method == "POST":
        customer.delete()
        return redirect("accounts:staff_customers")

    return render(
        request,
        "accounts/staff_customer_confirm_delete.html",
        {"customer": customer},
    )
