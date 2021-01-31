from django.contrib import messages
from django.shortcuts import redirect

from .models import SupplierEmployee

def is_supplier_employee(function):
    '''Restrict access. Check if the user signedup as suplier employee.
    Or if the user is superuser.'''
    def wrap(request, *args, **kwargs):
        employee = SupplierEmployee.objects.filter(user=request.user)
        # isinstance(request.user, SupplierEmployee)
        if request.user.is_superuser or len(employee) > 0:
            return function(request, *args, **kwargs)
        else:
            messages.warning(request, 'Sorry you are not registerd as Supplier. Permission Denied')
            return redirect('/')
    return wrap
