from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=200)
    genres = models.ManyToManyField(Genre, related_name="movies")
    release_year = models.PositiveSmallIntegerField()
    runtime_minutes = models.PositiveIntegerField()
    mpaa_rating = models.CharField(max_length=10, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["title", "release_year"]

    def __str__(self):
        return f"{self.title} ({self.release_year})"


class MovieCopy(models.Model):
    class AvailabilityStatus(models.TextChoices):
        AVAILABLE = "available", "Available"
        RENTED = "rented", "Rented"
        DAMAGED = "damaged", "Damaged"

    movie = models.ForeignKey(
        Movie,
        on_delete=models.PROTECT,
        related_name="copies",
    )
    copy_number = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=AvailabilityStatus.choices,
        default=AvailabilityStatus.AVAILABLE,
        db_index=True,
    )
    acquired_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["movie__title", "copy_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["movie", "copy_number"],
                name="unique_copy_number_per_movie",
            )
        ]

    def __str__(self):
        return f"{self.movie.title} - Copy {self.copy_number}"