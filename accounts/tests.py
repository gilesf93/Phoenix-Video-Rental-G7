from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class CustomerRegistrationTests(TestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.valid_data = {
            "username": "newcustomer",
            "email": "customer@example.com",
            "password1": "SecurePassword123!",
            "password2": "SecurePassword123!",
        }

    def test_registration_page_loads(self):
        response = self.client.get(self.register_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")
        self.assertContains(response, "Create an Account")

    def test_valid_registration_creates_customer(self):
        response = self.client.post(self.register_url, self.valid_data)

        self.assertRedirects(response, reverse("login"))
        self.assertTrue(
            User.objects.filter(
                username="newcustomer",
                email="customer@example.com",
            ).exists()
        )
        user = User.objects.get(username="newcustomer")

        self.assertTrue(user.groups.filter(name="Customer").exists())

    def test_email_is_required(self):
        registration_data = self.valid_data.copy()
        registration_data["email"] = ""

        response = self.client.post(self.register_url, registration_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "email", "This field is required."
        )
        self.assertFalse(User.objects.filter(username="newcustomer").exists())

    def test_invalid_email_is_rejected(self):
        registration_data = self.valid_data.copy()
        registration_data["email"] = "not-an-email"

        response = self.client.post(self.register_url, registration_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "email",
            "Enter a valid email address.",
        )
        self.assertFalse(User.objects.filter(username="newcustomer").exists())

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user(
            username="newcustomer",
            email="existing@example.com",
            password="ExistingPassword123!",
        )

        response = self.client.post(self.register_url, self.valid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].has_error("username"))
        self.assertEqual(User.objects.filter(username="newcustomer").count(), 1)

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            username="existingcustomer",
            email="customer@example.com",
            password="ExistingPassword123!",
        )

        response = self.client.post(self.register_url, self.valid_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "email",
            "An account with this email address already exists.",
        )
        self.assertFalse(User.objects.filter(username="newcustomer").exists())

    def test_mismatched_passwords_are_rejected(self):
        registration_data = self.valid_data.copy()
        registration_data["password2"] = "DifferentPassword123!"

        response = self.client.post(self.register_url, registration_data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].has_error("password2"))
        self.assertFalse(User.objects.filter(username="newcustomer").exists())


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.password = "Password123!"
        self.user = User.objects.create_user(
            username="testuser",
            password=self.password,
        )

    def test_valid_login(self):
        response = self.client.post(
            reverse("login"),
            {"username": "testuser", "password": self.password},
        )
        self.assertRedirects(response, reverse("core:home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_login(self):
        response = self.client.post(
            reverse("login"),
            {"username": "testuser", "password": "WrongPassword"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout(self):
        self.client.login(username="testuser", password=self.password)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("core:home"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertNotIn("_auth_user_id", self.client.session)
