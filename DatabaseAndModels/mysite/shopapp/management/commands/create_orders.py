from django.core.management import BaseCommand
from django.contrib.auth.models import User
from shopapp.models import Order, Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Создаем заказ...")
        user = User.objects.first()

        order, created = Order.objects.get_or_create(
            delivery_address="ул. Ленина, д. 1",
            promocode="SKILLBOX",
            user=user,
        )

        for product in Product.objects.all():
            order.products.add(product)

        order.save()
        self.stdout.write(self.style.SUCCESS(f"Заказ #{order.id} успешно создан!"))
