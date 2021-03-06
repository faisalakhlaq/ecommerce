from django.conf import settings
from django.db import models
from django.db.models import Q
from django.shortcuts import reverse
from django.db.models.signals import pre_save, pre_delete
from django.dispatch.dispatcher import receiver
from .utils import unique_slug_generator

User = settings.AUTH_USER_MODEL

CATEGORY_CHOICES = (
    ('S', 'Shirt'),
    ('SW', 'Sport Wear'),
    ('OW', 'Outwear'),
    ('P', 'Pants'),
    ('O', 'Other'),
)
LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danser'),
)
ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

class ItemQuerySet(models.query.QuerySet):
    def search(self, query):
        if query:
            query = query.strip()
            return self.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__icontains=query)
                ).distinct()
        return self

class ItemManager(models.Manager):
    def get_queryset(self):
        return ItemQuerySet(self.model, using=self._db)

    def search(self, query):
        return self.get_queryset().search(query)

class Item(models.Model):
    title               = models.CharField(max_length=100)
    price               = models.FloatField()
    discount_price      = models.FloatField(blank=True, null=True)
    category            = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label               = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug                = models.SlugField(blank=True, null=True)
    description         = models.TextField()
    quantity            = models.IntegerField(default=1)
    image               = models.ImageField(upload_to='products/', 
                          null=True, 
                          blank=True)

    objects             = ItemManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={"slug": self.slug})


class ItemImage(models.Model):
    item    = models.ForeignKey(Item, related_name="images", on_delete=models.CASCADE)
    image   = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.item.title


class OrderItem(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered     = models.BooleanField(default=False)
    item        = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity    = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.item.price * self.quantity

    def get_total_discount_item_price(self):
        discount_price = self.item.discount_price
        if discount_price and discount_price > 0:
            return discount_price * self.quantity
        else:
            return 0

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    order_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('Address',
        related_name = 'billing_address',
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        )
    shipping_address = models.ForeignKey('Address',
        related_name = 'shipping_address',
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        )
    payment = models.ForeignKey('Payment',
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True
        )
    coupon = models.ForeignKey('Coupon',
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True
        )
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.start_date)

    def get_total(self):
        total = 0
        for oi in self.items.all():
            total += oi.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total


class Address(models.Model):
    user                  = models.ForeignKey(User, 
                            blank=True, 
                            null=True,
                            on_delete=models.SET_NULL)
    street_address        = models.CharField(max_length=100)
    apartment_address     = models.CharField(max_length=100)
    country               = models.CharField(max_length=100)
    zip                   = models.CharField(max_length=100)
    address_type          = models.CharField(max_length=2, choices=ADDRESS_CHOICES)
    default               = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(User, 
        on_delete=models.SET_NULL, 
        blank=True,
        null=True
        )
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        if self.user:
            return "User: " + self.user.username + " Amount: " + str(self.amount)
        else:
            return "User: Deleted User. Amount: " + str(self.amount)


class Coupon(models.Model):
    code    = models.CharField(max_length=15)
    amount  = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()
    def __str__(self):
        return f"{self.pk}"
    
def item_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance=instance)

@receiver(pre_delete, sender=Item)
@receiver(pre_delete, sender=ItemImage)
def image_delete_handler(sender, instance, *args, **kwargs):
    if instance.image and instance.image.url:
        instance.image.delete()

pre_save.connect(item_pre_save_receiver, sender=Item)
