from django.shortcuts import render
from .models import Product, Order

def shop_index(request):
    return render(request, 'shopapp/shop-index.html')

def products_list(request):
    context = {'products': Product.objects.all()}
    return render(request, 'shopapp/products-list.html', context=context)

def orders_list(request):
    context = {
        'orders': Order.objects.select_related('user').prefetch_related('products').all()
    }
    return render(request, 'shopapp/orders-list.html', context=context)