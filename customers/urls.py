from django.urls import path

from .views import PartnersHome, SupplierEmployee

app_name = 'customers'

urlpatterns = [
    path('partners_home', PartnersHome.as_view(), name='partners_home'),
    path('employee_signup', SupplierEmployee.as_view(), name='employee_signup'),
]
