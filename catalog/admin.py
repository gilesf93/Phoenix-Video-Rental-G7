from django.contrib import admin

from .models import Genre, Movie, MovieCopy

admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(MovieCopy)