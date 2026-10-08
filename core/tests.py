from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class HomePageTest(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)


class RoleAccessTests(TestCase):
    def setUp(self):
        self.password = "Password123!"

        self.admin_group, _ = Group.objects.get_or_create(name="Admin")
        self.employee_group, _ = Group.objects.get_or_create(name="Employee")
        self.customer_group, _ = Group.objects.get_or_create(name="Customer")

        self.admin_user = User.objects.create_user(
            username="admintest",
            password=self.password,
        )
        self.admin_user.groups.add(self.admin_group)

        self.employee_user = User.objects.create_user(
            username="employeetest",
            password=self.password,
        )
        self.employee_user.groups.add(self.employee_group)

        self.customer_user = User.objects.create_user(
            username="customertest",
            password=self.password,
        )
        self.customer_user.groups.add(self.customer_group)

    def test_logged_out_user_cannot_access_staff_dashboard(self):
        response = self.client.get(reverse("core:staff_dashboard"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_logged_out_user_cannot_access_admin_dashboard(self):
        response = self.client.get(reverse("core:admin_dashboard"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_customer_cannot_access_staff_dashboard(self):
        self.assertTrue(
            self.client.login(username="customertest", password=self.password)
        )
        response = self.client.get(reverse("core:staff_dashboard"))
        self.assertEqual(response.status_code, 403)  # Permission Denied

    def test_employee_can_access_staff_dashboard(self):
        self.assertTrue(
            self.client.login(username="employeetest", password=self.password)
        )
        response = self.client.get(reverse("core:staff_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_staff_dashboard(self):
        self.assertTrue(self.client.login(username="admintest", password=self.password))
        response = self.client.get(reverse("core:staff_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_employee_cannot_access_admin_dashboard(self):
        self.assertTrue(
            self.client.login(username="employeetest", password=self.password)
        )
        response = self.client.get(reverse("core:admin_dashboard"))
        self.assertEqual(response.status_code, 403)  # Permission Denied

    def test_customer_cannot_access_admin_dashboard(self):
        self.assertTrue(
            self.client.login(username="customertest", password=self.password)
        )
        response = self.client.get(reverse("core:admin_dashboard"))
        self.assertEqual(response.status_code, 403)  # Permission Denied

    def test_admin_can_access_admin_dashboard(self):
        self.assertTrue(self.client.login(username="admintest", password=self.password))
        response = self.client.get(reverse("core:admin_dashboard"))
        self.assertEqual(response.status_code, 200)
