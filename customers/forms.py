from django import forms

from core.models import Item, ItemImage
# from .models import SupplierEmployee

# class UserForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ('username', 'first_name', 'last_name', 'email', 'password')

# class SupplierEmployeeForm(forms.ModelForm):
#     class Meta:
#         model = SupplierEmployee
#         fields = __all__

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