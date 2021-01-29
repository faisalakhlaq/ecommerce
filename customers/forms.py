from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from core.models import Item, ItemImage
from .models import SupplierEmployee, Supplier


class UserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email', 'password')

class ItemForm(forms.ModelForm):
    
    class Meta:
        model = Item
        fields = '__all__'

class ItemImageForm(forms.ModelForm):
    # TODO provide a delete button
    image = forms.ImageField(label='Item Image')    
    class Meta:
        model = ItemImage
        fields = ('image', )

class CreateSupplierForm(forms.ModelForm):
    
    class Meta:
        model = Supplier
        fields = '__all__'

class CreateSupplierEmployeeForm(forms.ModelForm):
    
    class Meta:
        model = SupplierEmployee
        fields = '__all__'
