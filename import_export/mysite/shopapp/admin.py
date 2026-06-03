import csv
from io import TextIOWrapper

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import path
from django.shortcuts import render, redirect

from .models import Product, Order, ProductImage
from .admin_mixins import ExportAsCSVMixin
from .forms import CSVImportForm


class OrderInline(admin.TabularInline):
    model = Product.orders.through


class ProductInline(admin.StackedInline):
    model = ProductImage


@admin.action(description="Archive products")
def mark_archived(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
):
    queryset.update(archived=True)


@admin.action(description="Unarchive products")
def mark_unarchived(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [
        mark_archived,
        mark_unarchived,
        "export_csv",
    ]
    inlines = [
        OrderInline,
        ProductInline,
    ]
    list_display = "pk", "name", "description_short", "price", "discount", "archived"
    list_display_links = "pk", "name"
    ordering = "-name", "pk"
    search_fields = "name", "description"
    fieldsets = [
        (
            None,
            {
                "fields": ("name", "description"),
            },
        ),
        (
            "Price options",
            {
                "fields": ("price", "discount"),
                "classes": ("wide", "collapse"),
            },
        ),
        (
            "Images",
            {
                "fields": ("preview",),
            },
        ),
        (
            "Extra options",
            {
                "fields": ("archived",),
                "classes": ("collapse",),
                "description": "Extra options. Field 'archived' is for soft delete",
            },
        ),
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."


class ProductInlineOrder(admin.StackedInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = "shopapp/orders_changelist.html"

    inlines = [
        ProductInlineOrder,
    ]
    list_display = "delivery_address", "promocode", "created_at", "user_verbose"

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-csv/",
                self.import_csv,
                name="import_orders_csv",
            ),
        ]
        return new_urls + urls

    def import_csv(self, request: HttpRequest):
        if request.method == "GET":
            form = CSVImportForm()
            context = {"form": form}
            return render(request, "admin/csv_form.html", context)

        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {"form": form}
            return render(request, "admin/csv_form.html", context, status=400)

        csv_file = TextIOWrapper(
            form.files["csv_file"].file,
            encoding="utf-8",
        )
        reader = csv.DictReader(csv_file)

        orders_to_create = []
        product_mappings = []

        for row in reader:
            user_id = row.get("user_id") or request.user.id

            order = Order(
                delivery_address=row.get("delivery_address", "Адрес не указан"),
                promocode=row.get("promocode", ""),
                user_id=user_id,
            )
            orders_to_create.append(order)

            products_str = row.get("products", "")
            if products_str:
                product_ids = [
                    int(p.strip())
                    for p in products_str.split(",")
                    if p.strip().isdigit()
                ]
            else:
                product_ids = []
            product_mappings.append(product_ids)

        created_orders = Order.objects.bulk_create(orders_to_create)

        for order, product_ids in zip(created_orders, product_mappings):
            if product_ids:
                order.products.set(product_ids)

        self.message_user(
            request, "Заказы из CSV успешно импортированы (с защитой от пустых полей)"
        )
        return redirect("..")
