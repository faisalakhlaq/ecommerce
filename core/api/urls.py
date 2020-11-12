from django.urls import path
from .views import (ItemListView, AddToCartView, OrderDetailView, 
AddCouponView, PaymentView, ItemDetailView, ItemImagesView)

urlpatterns = [
    path('products/', ItemListView.as_view(), name='product-list'),
    path('add-to-cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('order-summary/', OrderDetailView.as_view(), name='order-summary'),
    path('add-coupon/', OrderDetailView.as_view(), name='add-coupon'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('product/<slug>', ItemDetailView.as_view(), name='product'),
    path('product-images/<slug>', ItemImagesView.as_view(), name='product-images'),
]
