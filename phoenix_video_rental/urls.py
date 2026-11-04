from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("movies/", include("catalog.urls")),
    path("rentals/", include("rentals.urls")),
    path("", include("core.urls")),
]
