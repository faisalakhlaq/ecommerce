from django.urls import path

from .views import PartnersHome

app_name = 'customers'

urlpatterns = [
    path('home', PartnersHome.as_view(), name='home'),
]
