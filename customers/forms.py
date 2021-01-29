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
    # def __init__(self, *args, **kwargs):
    #     super(ItemImageForm, self).__init__(*args, **kwargs)
    #     self.helper = FormHelper()

    #     self.helper.add_input(Submit('submit', 'Submit'))
    #     self.helper.add_input(Button('delete', 'Delete', onclick='window.location.href="{}"'.format('delete')))

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
