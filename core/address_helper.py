from django.core.exceptions import ObjectDoesNotExist

from .models import Address

def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            return False
    return valid

def process_default_address(request, order, address_type=None):
    '''This method will search for the 
    default billing address details 
    and update the order if default exists.
    '''
    print(f"Using the defualt {address_type} address")
    address_qs = Address.objects.filter(
        user = request.user,
        address_type = address_type,
        default = True,
    )
    if address_qs.exists():
        if address_type == 'S':
            order.shipping_address = address_qs[0]
        else:
            order.billing_address = address_qs[0]
        order.save()
    else:
        raise ObjectDoesNotExist
    return address_qs[0]

def process_order_address(form, order, request, address_type):
    '''Get the address data from the checkout
    form and update the order address
    '''
    # import pdb; pdb.set_trace()

    address_type_complete = 'billing'
    if address_type == 'S':
        address_type_complete = 'shipping'
        
    address1 = form.cleaned_data.get(f'{address_type_complete}_address')
    address2 = form.cleaned_data.get(f'{address_type_complete}_address2')
    country = form.cleaned_data.get(f'{address_type_complete}_country')
    zip = form.cleaned_data.get(f'{address_type_complete}_zip')

    if is_valid_form([address1, country, zip]):
        address = Address(
            user = request.user,
            street_address = address1,
            apartment_address = address2,
            country = country,
            zip = zip,
            address_type = address_type,
        )
        address.save()
        if address_type == 'S':
            set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
            if set_default_shipping:
                address.default = True            
                address.save()
            order.shipping_address = address
        else:
            set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
            if set_default_billing:
                address.default = True            
                address.save()
            order.billing_address = address
        order.save()
        return address
    else:
        message = f"Please fill in the required {address_type_complete} address fields"
        raise ValueError(message)
