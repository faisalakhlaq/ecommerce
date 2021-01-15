from django.urls import path

from .views import (
    ItemListView,
    CheckoutView, 
    HomeListView, 
    ItemDetailView,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    PaymentView,
    AddCouponView,
    RequestRefundView,
    )
app_name = 'core'

urlpatterns = [
    path('', HomeListView.as_view(), name='home'),
    path('category-search/<category_name>', HomeListView.as_view(), 
    name='category-search'),
    path('item_list/', ItemListView.as_view(), name='items'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('product_detail/<slug>', ItemDetailView.as_view(), name='product'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-single-item-from-cart/<slug>/', remove_single_item_from_cart, 
    name='remove-single-item-from-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
]
