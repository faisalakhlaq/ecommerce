from django.contrib.auth.models import User
from django.db import models


class Supplier(models.Model):
    """Supplier supplies the products. Supplier can supply 
    a range of products from different brands."""
    title       = models.CharField(max_length=255)
    cvr         = models.CharField(max_length=20, blank=True, null=True)


class SupplierEmployee(models.Model):
    """This is a special user who is representing a company.
    This use will be able to login to a form and add their products.
    The products should come unders the model.Item. Supplier can
    edit, update, delete and add new items only for its company."""
    user        = models.OneToOneField(User, on_delete=models.CASCADE)
    company    = models.ForeignKey("Supplier", 
                    verbose_name=_("Supplier Employee"), 
                    related_name='supplier_employee', 
                    on_delete=models.SET_NULL,
                    blank=True, 
                    null=True)
    telephone   = models.CharField(_("Telephone Number"), 
                    max_length=50, blank=True, null=True)
    mobile      = models.CharField(_('Mobile'), 
                    max_length=50, blank=True, null=True)
