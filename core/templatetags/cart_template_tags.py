from django import template
from core.models import Order

register = template.Library()

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user = user, ordered=False)
        if qs.exists():
            # TODO check the quantity of each item
            return qs[0].items.count()
    return 0
