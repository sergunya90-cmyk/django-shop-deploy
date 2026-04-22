from django.shortcuts import render

def shop_index(request):
    context = {
        'shop_name': 'Мой первый магазин',
        'products': [
            {'name': 'Ноутбук', 'price': 1500},
            {'name': 'Мышка', 'price': 50},
            {'name': 'Подарок', 'price': 0},
        ]
    }
    return render(request, 'shopapp/shop-index.html', context=context)
