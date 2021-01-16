from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import View, ListView, DetailView
from pathlib import Path

from .models import (Item, Order, OrderItem, Address, 
Payment, Coupon, Refund)
from .forms import CheckoutForm, CouponForm, RefundForm
from .address_helper import process_default_address, process_order_address
import random
import string
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

class ItemListView(ListView):
    model = Item
    paginate_by = 1
    template_name = 'item_list.html'
    
    def get_queryset(self):
        qs = Item.objects.all()
        return qs

class HomeListView(ListView):
    model = Item
    paginate_by =12
    template_name = 'item_list.html'
    
    def get_queryset(self):
        qs = Item.objects.all()
        return qs
    
    def get_context_data(self, *args, **kwargs):
        context = super(HomeListView, self).\
            get_context_data(*args, **kwargs)
        query = self.request.GET.get('query')          
        qs = self.get_queryset()
        if query:
            qs = qs.search(query)
        context["object_list"] = qs
        return context

class OrderSummaryView(View):
    template_name = 'order_summary.html'
    model = Order

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.warning(self.request, 'Sorry your account is not recognized')
            return redirect('core:home')
        
        try:
            order = Order.objects.get(
                user=self.request.user, 
                ordered=False
                )
            context = {'order_object': order}
            return render(self.request, self.template_name, context)
        except ObjectDoesNotExist:
            messages.warning(self.request, 'Sorry you do not have an active order')
            return redirect('core:home')
        

class ItemDetailView(DetailView):
    model = Item
    template_name = 'product_detail.html'
    
    def get_object(self):
        slug = self.kwargs.get('slug')
        if slug is None:
            return redirect('core:home')
        return get_object_or_404(Item, slug=slug)

    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        images = self.get_object().images.all()
        context["images"] = images
        return context
    
class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            form = CheckoutForm()
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'form': form,
                'order': order,
                'DISPLAY_COUPON_FORM': True,
                'couponform': CouponForm(),
            }
            default_shipping_address_qs = Address.objects.filter(
                user = self.request.user,
                address_type = 'S',
                default=True,
            )
            if default_shipping_address_qs.exists():
                context.update({'default_shipping_address': default_shipping_address_qs[0]})

            default_billing_address_qs = Address.objects.filter(
                user = self.request.user,
                address_type = 'B',
                default=True,
            )
            if default_billing_address_qs.exists():
                context.update({'default_billing_address': default_billing_address_qs[0]})

            return render(self.request, 'checkout-page.html', context)
        except ObjectDoesNotExist:
            messages.warning('Sorry you do no have an active order')
            return redirect('core:checkout')

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            # TODO everything is set to required = False so not 
            # sure if its useful to check if the form.is_valid()
            if form.is_valid(): 
                shipping_address = None
                user_default_shipping = form.cleaned_data.get('use_default_shipping')
                if user_default_shipping:
                    try:
                        shipping_address = process_default_address(self.request, order, 'S')
                    except ObjectDoesNotExist:                        
                        messages.info(self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    try:
                        shipping_address = process_order_address(form, order, self.request, address_type='S')
                    except ValueError as e:
                        messages.info(self.request, e)
                        return redirect('core:checkout')
                same_billing_address = form.cleaned_data.get('same_billing_address')
                user_default_billing = form.cleaned_data.get('use_default_billing')
                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()
                elif user_default_billing:
                    try:
                        billing_address = process_default_address(self.request, order, 'B')
                    except ObjectDoesNotExist:                        
                        messages.info(self.request, "No default billing address available")
                        return redirect('core:checkout')
                else:
                    try:
                        billing_address = process_order_address(form, order, self.request, address_type='B')
                    except ValueError as e:
                        messages.info(self.request, e)
                        return redirect('core:checkout')

                payment_option = form.cleaned_data.get('payment_option')
                if payment_option == 'S':
                    return redirect('core:payment', payment_option='Stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='Paypal')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            redirect('core:order-summary')

class PaymentView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if not order.billing_address:
                messages.info('Sorry! you have not provided address yet')
                return redirect('core:checkout')

            context = {
                'order': order,
                'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
                'DISPLAY_COUPON_FORM': False,
            }
            return render(self.request, 'payment.html', context)
        except ObjectDoesNotExist:
            messages.warning('Sorry you do not have an active order')
            return redirect('core:home')

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)
        # import pdb; pdb.set_trace()
        try:
            # customer = stripe.Customer.create(
            #             email=self.request.user.email,
            #         )
            # customer.sources.create(source=token)
            charge = stripe.Charge.create(
                #the value will be in cents therefore, multiplying with 100
                amount=amount,
                currency="dkk",
                source=token,
            )
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = amount
            payment.save()

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.payment = payment
            order.ordered = True
            order.ref_code = str(order.id) + create_ref_code()
            order.save()
            messages.success(self.request, 'Your order was successful')
            return redirect("/")
        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/")
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return redirect("/")
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            messages.warning(self.request, "Invalid parameters")
            return redirect("/")
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Not authenticated")
            return redirect("/")
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Network error")
            return redirect("/")
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(
                self.request, "Payment unsuccessful. Please try again.")
            return redirect("/")
        except Exception as e:
            # send an email to ourselves
            print(e)
            messages.warning(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("/payment/stripe/") #TODO change redirect
        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")

@login_required(login_url='/accounts/login/')
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
        )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'This item quantity is updated!')
        else:
            order.items.add(order_item)
            messages.info(request, 'This item is added to your cart!')
    else:
        order_date = timezone.now()
        order = Order.objects.create(user = request.user, 
        order_date=order_date)
        order.items.add(order_item)
        messages.info(request, 'This item is added to your cart!')
    return redirect('core:order-summary')

def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    # order_item = 
    order_qs = Order.objects.filter(
        user=request.user, 
        ordered=False
        )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, 'This item is removed from your cart!')
            return redirect('core:order-summary')
        else:
            messages.info(request, 'This item is not in your cart!')
            return redirect('core:product', slug= slug)
    else:
        messages.info(request, 'You do not have an active order!')

    return redirect('core:product', slug= slug)

def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user, 
        ordered=False
        )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, 'This item quantity is updated!')
            return redirect('core:order-summary')
        else:
            messages.info(request, 'This item is not in your cart!')
            return redirect('core:product', slug= slug)
    else:
        messages.info(request, 'You do not have an active order!')
    return redirect('core:product', slug= slug)


def get_coupon(request, code):
    try:
        return Coupon.objects.get(code=code)
    except ObjectDoesNotExist:
        message = 'Sorry! This is not a valid coupon code'
        raise ValueError(message)
        # return redirect('core:checkout')

class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, 
                    ordered=False
                    )
                coupon = get_coupon(request=self.request, code=code)
                order.coupon = coupon
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect('core:checkout')
            except (ObjectDoesNotExist, ValueError) as e:
                message = 'You do not have an active order'
                if isinstance(e, ValueError):
                    message = e
                messages.warning(self.request, message)
                return redirect('core:checkout')


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {'form':form}
        return render(self.request, 'request_refund_form.html', context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email =     form.cleaned_data.get('email')
            try:
                order = Order.objects.get(ref_code=ref_code)
                if order.refund_requested:
                    messages.info(self.request, 'Your refund is already requested.')
                    return redirect('core:request-refund')
                order.refund_requested = True
                order.save()
                refund = Refund()
                refund.order = order
                refund.ref_code = ref_code
                refund.message = message
                refund.email = email   
                refund.save()
                messages.info(self.request, 'Your request was received')
                return redirect('core:request-refund')
            except ObjectDoesNotExist:
                messages.info(self.request, 'Sorry this order reference code is not found')
                return redirect('core:request-refund')
        else:
            messages.info(self.request, 'Sorry the information for refund is not correct')
            return redirect('core:request-refund')
