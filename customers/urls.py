from django.urls import path

from .views import PartnersHomeView, SupplierEmployeeCreateView

app_name = 'customers'

urlpatterns = [
    path('partners_home', PartnersHomeView.as_view(), name='partners_home'),
    path('employee_signup', SupplierEmployeeCreateView.as_view(), name='employee_signup'),
]
