from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.models import Address

User = settings.AUTH_USER_MODEL


class Supplier(models.Model):
    """Supplier supplies the products. Supplier can supply 
    a range of products from different brands."""
    address         = models.ForeignKey(Address, 
                            verbose_name=_("Supplier Employee"), 
                            related_name='supplier', 
                            on_delete=models.SET_NULL, 
                            blank=True, null=True)
    # name       = models.CharField(max_length=255)
    # cvr        = models.CharField(max_length=20, blank=True, null=True)


class SupplierEmployee(models.Model):
    """This is a special user who is representing a company.
    This user will be able to login to a form and add their products.
    The products should come unders the model.Item. Supplier can
    edit, update, delete and add new items only for its company."""
    user                = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date          = models.DateField(null=True, blank=True)
    image               = models.ImageField(_("Picture"), 
                            upload_to='profile_images/', 
                            null=True, blank=True)
    company             = models.ForeignKey("Supplier", 
                            verbose_name=_("Supplier Employee"), 
                            related_name='supplier_employee', 
                            on_delete=models.SET_NULL,
                            blank=True, null=True)
    address             = models.ForeignKey(Address, 
                            verbose_name=_("Supplier Employee Address"), 
                            related_name='supplier_employee', 
                            on_delete=models.SET_NULL, 
                            blank=True, null=True)
