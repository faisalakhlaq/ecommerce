from .models import SupplierEmployee

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')

class SupplierEmployeeForm(forms.ModelForm):
    class Meta:
        model = SupplierEmployee
        fields = __all__