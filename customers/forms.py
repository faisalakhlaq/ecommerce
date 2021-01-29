from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from core.models import Item, ItemImage
from .models import SupplierEmployee, Supplier


class UserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email', 'password')
        widgets = {
          'password': forms.PasswordInput()
         }


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = '__all__'

class ItemImageForm(forms.ModelForm):
    image = forms.ImageField(label='Item Image')    
    class Meta:
        model = ItemImage
        fields = ('image', )

class CreateSupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__'

class CreateSupplierEmployeeForm(forms.ModelForm):
    birth_date = forms.DateField(required=False,
    widget=forms.TextInput(     
        attrs={'type': 'date'} 
        )
    )    
    class Meta:
        model = SupplierEmployee
        fields = ['birth_date', 'image', 'company']
