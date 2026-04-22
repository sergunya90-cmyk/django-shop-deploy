from django.urls import path
from .views import shop_index

urlpatterns = [
    path('', shop_index, name='index'),
]
