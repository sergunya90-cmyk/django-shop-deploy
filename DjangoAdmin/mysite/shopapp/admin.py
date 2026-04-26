from django.contrib import admin
from .models import Product, Order


@admin.action(description="Архивировать продукты")
def mark_archived(modeladmin, request, queryset):
    queryset.update(archived=True)


class OrderInline(admin.TabularInline):
    model = Order.products.through


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    actions = [mark_archived]
    inlines = [OrderInline]

    list_display = ("pk", "name", "description_short", "price", "discount", "archived")
    list_display_links = ("pk", "name")

    search_fields = ("name", "description", "price")

    fieldsets = [
        (None, {
            "fields": ("name", "description"),
        }),
        ("Price options", {
            "fields": ("price", "discount"),
        }),
        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse",),
        }),
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("delivery_address", "promocode", "created_at", "user")