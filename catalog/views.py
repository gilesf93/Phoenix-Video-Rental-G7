from django.shortcuts import get_object_or_404, render

from .models import Genre, Movie, MovieCopy


def movie_list(request):
    movies = Movie.objects.all()
    genres = Genre.objects.all()

    title_query = request.GET.get("title", "")
    genre_query = request.GET.get("genre", "")
    availability_query = request.GET.get("availability", "")

    if title_query:
        movies = movies.filter(title__icontains=title_query)

    if genre_query:
        movies = movies.filter(genres__id=genre_query)

    if availability_query:
        movies = movies.filter(copies__status=availability_query)

    movies = movies.distinct()

    context = {
        "movies": movies,
        "genres": genres,
        "title_query": title_query,
        "genre_query": genre_query,
        "availability_query": availability_query,
        "availability_choices": MovieCopy.AvailabilityStatus.choices,
    }

    return render(request, "catalog/movie_list.html", context)


def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)

    return render(
        request,
        "catalog/movie_detail.html",
        {"movie": movie},
    )