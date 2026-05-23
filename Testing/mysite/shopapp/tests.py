from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from .models import Order


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username="test_buyer", password="test_password"
        )

        permission = Permission.objects.get(codename="view_order")
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.force_login(self.user)

        self.order = Order.objects.create(
            delivery_address="ул. Тестовая, дом 404",
            promocode="SKILLBOX2026",
            user=self.user,
        )

    def tearDown(self):
        self.order.delete()

    def test_order_details(self):
        url = reverse("shopapp:order_details", kwargs={"pk": self.order.pk})
        response = self.client.get(url)

        self.assertContains(response, self.order.delivery_address)

        self.assertContains(response, self.order.promocode)

        self.assertEqual(response.context["object"].pk, self.order.pk)


class OrdersExportTestCase(TestCase):
    fixtures = ["orders-fixture.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username="staff_user", password="staff_password", is_staff=True
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.force_login(self.user)

    def test_export_orders(self):
        url = reverse("shopapp:orders_export")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        orders = Order.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user": order.user.pk,
                "products": [p.pk for p in order.products.all()],
            }
            for order in orders
        ]

        response_data = response.json()

        self.assertIn("orders", response_data)
        self.assertEqual(response_data["orders"], expected_data)
