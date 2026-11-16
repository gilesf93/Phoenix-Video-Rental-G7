from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", views.profile_view, name="profile"),

    path("staff/customers/", views.staff_customers, name="staff_customers"),
    path(
        "staff/customers/add/",
        views.staff_customer_create,
        name="staff_customer_create",
    ),
    path(
        "staff/customers/<int:user_id>/edit/",
        views.staff_customer_update,
        name="staff_customer_update",
    ),
    path(
        "staff/customers/<int:user_id>/delete/",
        views.staff_customer_delete,
        name="staff_customer_delete",
    ),

]
