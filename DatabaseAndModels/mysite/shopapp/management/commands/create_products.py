from django.core.management import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Создаем товары...")
        products_names = ["Ноутбук", "Смартфон", "Наушники"]

        for name in products_names:
            product, created = Product.objects.get_or_create(name=name, price=1000)
            if created:
                self.stdout.write(f"Создан товар: {product.name}")
            else:
                self.stdout.write(f"Товар уже существует: {product.name}")

        self.stdout.write(self.style.SUCCESS("Команда выполнена!"))
        