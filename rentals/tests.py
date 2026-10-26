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

        self.customer_profile = CustomerProfile.objects.create(user=self.customer_user)

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

        response = self.client.get(reverse("rentals:staff_rental_dashboard"))

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
        self.client.force_login(self.customer_user)

        response = self.client.get(reverse("rentals:staff_rental_dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_staff_can_access_dashboard(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("rentals:staff_rental_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Rentals")
        self.assertContains(response, "Overdue Rentals")
        self.assertContains(response, "Return Movie")

    def test_staff_can_return_active_rental(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse(
                "rentals:return_rental",
                args=[self.active_rental.pk],
            )
        )

        self.assertRedirects(
            response,
            reverse("rentals:staff_rental_dashboard"),
        )

        self.active_rental.refresh_from_db()

        self.assertEqual(
            self.active_rental.status,
            Rental.RentalStatus.RETURNED,
        )
        self.assertIsNotNone(self.active_rental.return_date)
        self.assertEqual(
            self.active_rental.processed_by,
            self.staff_user,
        )

    def test_returned_rental_is_removed_from_dashboard(self):
        self.client.force_login(self.staff_user)

        self.client.post(
            reverse(
                "rentals:return_rental",
                args=[self.active_rental.pk],
            )
        )

        response = self.client.get(reverse("rentals:staff_rental_dashboard"))

        self.assertNotIn(
            self.active_rental,
            response.context["active_rentals"],
        )
        self.assertNotIn(
            self.active_rental,
            response.context["overdue_rentals"],
        )

    def test_regular_customer_cannot_return_rental(self):
        self.client.force_login(self.customer_user)

        response = self.client.post(
            reverse(
                "rentals:return_rental",
                args=[self.active_rental.pk],
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

        self.active_rental.refresh_from_db()

        self.assertIsNone(self.active_rental.return_date)
        self.assertEqual(
            self.active_rental.status,
            Rental.RentalStatus.ACTIVE,
        )

    def test_return_rental_requires_post(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(
            reverse(
                "rentals:return_rental",
                args=[self.active_rental.pk],
            )
        )

        self.assertEqual(response.status_code, 405)

    def test_returned_rental_cannot_be_returned_twice(self):
        self.client.force_login(self.staff_user)

        return_url = reverse(
            "rentals:return_rental",
            args=[self.active_rental.pk],
        )

        self.client.post(return_url)
        response = self.client.post(return_url)

        self.assertEqual(response.status_code, 404)


class InventoryStatusSignalTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.customer_user = User.objects.create_user(
            username="inventorycustomer",
            password="TestPassword123!",
        )

        self.customer_profile = CustomerProfile.objects.create(user=self.customer_user)

        self.movie = Movie.objects.create(
            title="Inventory Test Movie",
            release_year=2021,
            runtime_minutes=100,
            mpaa_rating="PG",
        )

        self.movie_copy = MovieCopy.objects.create(
            movie=self.movie,
            copy_number=1,
        )

    def create_rental(
        self,
        status=Rental.RentalStatus.ACTIVE,
    ):
        return Rental.objects.create(
            customer=self.customer_profile,
            movie_copy=self.movie_copy,
            due_date=timezone.localdate() + timedelta(days=7),
            status=status,
        )

    def test_creating_active_rental_marks_copy_rented(self):
        self.create_rental()
        self.movie_copy.refresh_from_db()

        self.assertEqual(
            self.movie_copy.status,
            MovieCopy.AvailabilityStatus.RENTED,
        )

    def test_creating_overdue_rental_marks_copy_rented(self):
        self.create_rental(Rental.RentalStatus.OVERDUE)
        self.movie_copy.refresh_from_db()

        self.assertEqual(
            self.movie_copy.status,
            MovieCopy.AvailabilityStatus.RENTED,
        )

    def test_returning_rental_marks_copy_available(self):
        rental = self.create_rental()

        rental.status = Rental.RentalStatus.RETURNED
        rental.return_date = timezone.now()
        rental.save(
            update_fields=[
                "status",
                "return_date",
            ]
        )

        self.movie_copy.refresh_from_db()

        self.assertEqual(
            self.movie_copy.status,
            MovieCopy.AvailabilityStatus.AVAILABLE,
        )

    def test_damaged_copy_remains_damaged_after_return(self):
        rental = self.create_rental()

        self.movie_copy.status = MovieCopy.AvailabilityStatus.DAMAGED
        self.movie_copy.save(update_fields=["status"])

        rental.status = Rental.RentalStatus.RETURNED
        rental.return_date = timezone.now()
        rental.save(
            update_fields=[
                "status",
                "return_date",
            ]
        )

        self.movie_copy.refresh_from_db()

        self.assertEqual(
            self.movie_copy.status,
            MovieCopy.AvailabilityStatus.DAMAGED,
        )

    def test_deleting_open_rental_marks_copy_available(self):
        rental = self.create_rental()
        rental.delete()

        self.movie_copy.refresh_from_db()

        self.assertEqual(
            self.movie_copy.status,
            MovieCopy.AvailabilityStatus.AVAILABLE,
        )
