from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.shortcuts import render, redirect

from core.models import ItemImage
from utils.forms import AddressForm
from .forms import ItemForm, ItemImageForm, CreateSupplierEmployeeForm, UserForm
from .models import SupplierEmployee
from .decorators import is_supplier_employee

class PartnersHomeView(View):
    def __init__(self):
        self.ImageFormset = modelformset_factory(ItemImage, 
                                            form=ItemImageForm, 
                                            extra=1)
        super(PartnersHomeView, self).__init__()

    @method_decorator(login_required(login_url='/accounts/login/'))
    @method_decorator(is_supplier_employee)
    def get(self, *args, **kwargs):
        context = {
            'item_form': ItemForm(prefix='item'),
            'image_formset': self.ImageFormset(prefix='images_form', queryset=ItemImage.objects.none())
        }
        return render(self.request, 'customers/partners_home.html', context)

    @method_decorator(login_required(login_url='/accounts/login/'))
    @method_decorator(is_supplier_employee)
    def post(self, *args, **kwargs):
        try:
            image_formset = self.ImageFormset(self.request.POST, 
                                            self.request.FILES,
                                            queryset=ItemImage.objects.none(),
                                            prefix='images_form')
            item_form = ItemForm(self.request.POST,
                                self.request.FILES,
                                prefix='item' or None)
            if item_form.is_valid() and image_formset.is_valid():
                item = item_form.save()
                for form in image_formset.cleaned_data:
                    #this helps to not crash if the user   
                    #has not uploaded all the photos
                    if form:
                        image = form['image']
                        item_image = ItemImage(item=item, image=image)
                        item_image.save()
                messages.success(self.request, 'Successfully added new item')
                # return HttpResponseRedirect('customers:partners_home')
            # else:
            return redirect('customers:partners_home')
        except Exception as e:
            print('Exception while creating item by partner: ', e)
            messages.error(self.request, 'Sorry! Unable to add the item.') 
            return redirect('customers:partners_home')


class SupplierEmployeeCreateView(View):
    def get(self, *args, **kwargs):
        context = {
            'user_form': UserForm(),
            'employee_form': CreateSupplierEmployeeForm(),
            'address_form': AddressForm(),
        }
        return render(self.request, 'customers/signup.html', context)

    def post(self, *args, **kwargs):
        user_form = UserForm(self.request.POST)
        employee_form = CreateSupplierEmployeeForm(self.request.POST, self.request.FILES)
        address_form = AddressForm(self.request.POST)
        if user_form.is_valid() and employee_form.is_valid() and address_form.is_valid():
            user = user_form.save()
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            address = address_form.save()
            bday = employee_form.cleaned_data.get("birth_date")
            image = employee_form.cleaned_data.get('image')
            company = employee_form.cleaned_data.get('company')
            employee = SupplierEmployee.objects.create(
               user = user,
               birth_date = bday,
               image = image,
               company = company,
               address = address, 
            )
            messages.success(self.request, 'Your account was successfully created!')
            return redirect('/')
        messages.success(self.request, 'Unable to create account!')
        context = {
            'user_form':user_form,
            'employee_form':employee_form,
            'address_form':address_form,
        }
        return render(self.request, 'customers/signup.html', context)
