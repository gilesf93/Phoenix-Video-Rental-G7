from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from .models import Movie, MovieCopy


class MovieCopyModelTests(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title="The Matrix",
            release_year=1999,
            runtime_minutes=136,
            mpaa_rating="R",
        )

    def test_create_movie_copy_with_available_status(self):
        movie_copy = MovieCopy.objects.create(
            movie=self.movie,
            copy_number=1,
        )

        self.assertEqual(
            movie_copy.status,
            MovieCopy.AvailabilityStatus.AVAILABLE,
        )
        self.assertEqual(movie_copy.movie, self.movie)
        self.assertEqual(str(movie_copy), "The Matrix - Copy 1")

    def test_multiple_copies_can_belong_to_same_movie(self):
        first_copy = MovieCopy.objects.create(
            movie=self.movie,
            copy_number=1,
        )
        second_copy = MovieCopy.objects.create(
            movie=self.movie,
            copy_number=2,
        )

        self.assertEqual(self.movie.copies.count(), 2)
        self.assertNotEqual(first_copy.copy_number, second_copy.copy_number)

    def test_copy_number_must_be_unique_for_each_movie(self):
        MovieCopy.objects.create(
            movie=self.movie,
            copy_number=1,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            MovieCopy.objects.create(
                movie=self.movie,
                copy_number=1,
            )

    def test_movie_with_inventory_copy_cannot_be_deleted(self):
        MovieCopy.objects.create(
            movie=self.movie,
            copy_number=1,
        )

        with self.assertRaises(ProtectedError):
            self.movie.delete()

    def test_inventory_status_can_be_updated(self):
        movie_copy = MovieCopy.objects.create(
            movie=self.movie,
            copy_number=1,
        )

        movie_copy.status = MovieCopy.AvailabilityStatus.RENTED
        movie_copy.save()
        movie_copy.refresh_from_db()

        self.assertEqual(
            movie_copy.status,
            MovieCopy.AvailabilityStatus.RENTED,
        )
