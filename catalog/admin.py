from django.contrib import admin

from .models import Genre, Movie, MovieCopy

admin.site.register(Genre)
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "release_year", "mpaa_rating")
    search_fields = ("title",)
    list_filter = ("release_year", "mpaa_rating")
    ordering = ("title",)

@admin.register(MovieCopy)
class MovieCopyAdmin(admin.ModelAdmin):
    list_display = ("movie", "copy_number", "status", "acquired_date")
    list_filter = ("status", "acquired_date")
    search_fields = ("movie__title",)
    ordering = ("movie__title", "copy_number")
