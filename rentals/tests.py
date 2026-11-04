from django.test import TestCase
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import CustomerProfile
from catalog.models import Movie, MovieCopy
from .models import Rental

class StaffRentalDashboardTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.staff_user = User.objects.create_user(
            username="rentalstaff",
            password="TestPassword123!",
            is_staff=True,
        )

        self.customer_user = User.objects.create_user(
            username="rentalcustomer",
            password="TestPassword123!",
        )

        self.customer_profile = CustomerProfile.objects.create(
            user=self.customer_user
        )

        self.movie = Movie.objects.create(
            title="Test Movie",
            release_year=2020,
            runtime_minutes=120,
            mpaa_rating="PG",
        )
        self.copy1 = MovieCopy.objects.create(
            movie=self.movie,
            copy_number=1,
        )

        self.copy2 = MovieCopy.objects.create(
            movie=self.movie,
            copy_number=2,
        )
        self.active_rental = Rental.objects.create(
            customer=self.customer_profile,
            movie_copy=self.copy1,
            due_date=timezone.localdate() + timedelta(days=7),
            status=Rental.RentalStatus.ACTIVE,
        )

        self.overdue_rental = Rental.objects.create(
            customer=self.customer_profile,
            movie_copy=self.copy2,
            due_date=timezone.localdate() - timedelta(days=3),
            status=Rental.RentalStatus.OVERDUE,
        )
    def test_active_and_overdue_rentals_display_correctly(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(
            reverse("rentals:staff_rental_dashboard")
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            self.active_rental,
            response.context["active_rentals"],
        )

        self.assertNotIn(
            self.overdue_rental,
            response.context["active_rentals"],
        )

        self.assertIn(
            self.overdue_rental,
            response.context["overdue_rentals"],
        )

        self.assertNotIn(
            self.active_rental,
            response.context["overdue_rentals"],
        )

    def test_regular_customer_cannot_access_dashboard(self):
        User = get_user_model()

        customer = User.objects.create_user(
            username="regularcustomer",
            password="TestPassword123!",
            is_staff=False,
        )

        self.client.force_login(customer)

        response = self.client.get(
            reverse("rentals:staff_rental_dashboard")
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_staff_can_access_dashboard(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(
            reverse("rentals:staff_rental_dashboard")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Rentals")
        self.assertContains(response, "Overdue Rentals")


class CreateRentalTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.staff_user = User.objects.create_user(
            username="teststaff",
            password="TestPassword123!",
            is_staff=True,
        )

        self.customer_user = User.objects.create_user(
            username="testcustomer",
            password="TestPassword123!",
        )

        self.customer = CustomerProfile.objects.create(
            user=self.customer_user
        )

        self.movie = Movie.objects.create(
            title="Rental Test Movie",
            release_year=2022,
            runtime_minutes=110,
            mpaa_rating="PG",
        )

        self.movie_copy = MovieCopy.objects.create(
            movie=self.movie,
            copy_number=1,
        )

        self.url = reverse("rentals:create_rental")

    def test_staff_can_create_rental(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(self.url, {
            "customer": self.customer.pk,
            "movie_copy": self.movie_copy.pk,
            "due_date": (
                timezone.localdate() + timedelta(days=7)
            ).isoformat(),
        })

        self.assertRedirects(response, self.url)

        rental = Rental.objects.get(
            movie_copy=self.movie_copy
        )

        self.assertEqual(
            rental.status,
            Rental.RentalStatus.ACTIVE
        )
        self.assertEqual(
            rental.customer,
            self.customer
        )
        self.assertEqual(
            rental.processed_by,
            self.staff_user
        )

    def test_movie_copy_becomes_rented(self):
        self.client.force_login(self.staff_user)

        self.client.post(self.url, {
            "customer": self.customer.pk,
            "movie_copy": self.movie_copy.pk,
            "due_date": (
                timezone.localdate() + timedelta(days=7)
            ).isoformat(),
        })

        self.movie_copy.refresh_from_db()

        self.assertEqual(
            self.movie_copy.status,
            MovieCopy.AvailabilityStatus.RENTED
        )

    def test_rented_copy_cannot_be_rented_again(self):
        self.client.force_login(self.staff_user)

        rental_data = {
            "customer": self.customer.pk,
            "movie_copy": self.movie_copy.pk,
            "due_date": (
                timezone.localdate() + timedelta(days=7)
            ).isoformat(),
        }

        self.client.post(self.url, rental_data)
        self.client.post(self.url, rental_data)

        self.assertEqual(
            Rental.objects.filter(
                movie_copy=self.movie_copy
            ).count(),
            1
        )

    def test_regular_customer_cannot_create_rental(self):
        self.client.force_login(self.customer_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)
