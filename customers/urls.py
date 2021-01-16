from django.urls import path

from .views import PartnersHome

app_name = 'customers'

urlpatterns = [
    path('partners_home', PartnersHome.as_view(), name='partners_home'),
]
