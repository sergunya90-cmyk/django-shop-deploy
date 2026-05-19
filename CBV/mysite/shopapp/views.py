from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.models import Group, User
from timeit import default_timer
from .models import Product, Order


class ShopIndexView(TemplateView):
    template_name = "shopapp/shop-index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["time_running"] = default_timer()
        context["products"] = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        return context


class GroupsListView(ListView):
    queryset = Group.objects.prefetch_related('permissions').all()
    template_name = "shopapp/groups-list.html"
    context_object_name = "groups"


class ProductListView(ListView):
    queryset = Product.objects.filter(archived=False)
    template_name = "shopapp/products-list.html"
    context_object_name = "products"


class ProductDetailView(DetailView):
    model = Product
    template_name = "shopapp/products-details.html"
    context_object_name = "product"


class ProductCreateView(CreateView):
    model = Product
    fields = ["name", "price", "description", "discount"]
    success_url = reverse_lazy("shopapp:products_list")


class ProductUpdateView(UpdateView):
    model = Product
    fields = ["name", "price", "description", "discount"]
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse_lazy("shopapp:product_details", kwargs={"pk": self.object.pk})


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrderListView(ListView):
    queryset = Order.objects.select_related("user").prefetch_related("products")
    template_name = "shopapp/orders-list.html"
    context_object_name = "orders"


class OrderDetailView(DetailView):
    queryset = Order.objects.select_related("user").prefetch_related("products")
    template_name = "shopapp/order_detail.html"
    context_object_name = "order"


class OrderCreateView(CreateView):
    model = Order
    fields = ["user", "products", "delivery_address", "promocode"]
    success_url = reverse_lazy("shopapp:orders_list")


class OrderUpdateView(UpdateView):
    model = Order
    fields = ["user", "products", "delivery_address", "promocode"]
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse_lazy("shopapp:order_details", kwargs={"pk": self.object.pk})


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:orders_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.products.clear()
        self.object.delete()
        return HttpResponseRedirect(success_url)