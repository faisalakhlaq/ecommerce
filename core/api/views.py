from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from core.models import (Item, ItemImage, Order, OrderItem, Payment, 
Address, Coupon)
from core.views import create_ref_code
from .serializers import ItemSerializer, OrderSerializer, ItemImageSerializer

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

class ItemListView(ListAPIView):
    # permission_classes = (AllowAny)
    permission_classes = [IsAuthenticated,]
    serializer_class = ItemSerializer
    queryset = Item.objects.all()
    # linenos = 'table' if self.linenos else False


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated,]

    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug' or None)
        if slug is None:
            return Response({'message':'Invalid request. Slug not provided'},
            status=HTTP_400_BAD_REQUEST)

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
                # messages.info(request, 'This item quantity is updated!')
            else:
                order.items.add(order_item)
                # messages.info(request, 'This item is added to your cart!')
        else:
            order_date = timezone.now()
            order = Order.objects.create(user = request.user, 
            order_date=order_date)
            order.items.add(order_item)
            # messages.info(request, 'This item is added to your cart!')
        return Response(status=HTTP_200_OK)


# class OrderDetailView(APIView):
#     permission_classes = [IsAuthenticated,]
#     serializer_class = OrderSerializer
#     # queryset = Item.objects.all()

#     def get(self, *args, **kwargs):
#         try:
#             order = Order.objects.get(
#                 user=self.request.user, 
#                 ordered=False
#                 )
#             return Response(OrderSerializer(order).data, status=HTTP_200_OK)
#         except ObjectDoesNotExist:
#             context = {
#                 'messages': 'Sorry you do not have an active order',
#             }
#             return Response(context, status=HTTP_200_OK)
        
class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return order
        except ObjectDoesNotExist:
            raise Http404("You do not have an active order")
            # return Response({"message": "You do not have an active order"}, status=HTTP_400_BAD_REQUEST)

class PaymentView(APIView):

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = request.data.get('stripeToken')
        billing_address_id = request.data.get('selectedBillingAddress')
        shipping_address_id = request.data.get('selectedShippingAddress')
        amount = int(order.get_total() * 100)

        billing_address = Address.objects.get(id=billing_address_id)
        shipping_address = Address.objects.get(id=shipping_address_id)

        try:
            # charge once off on the token
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                source=token
            )

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.billing_address = billing_address
            order.shipping_address = shipping_address
            order.ref_code = str(order.id) + create_ref_code()
            order.save()

            return Response(status=HTTP_200_OK)

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            return Response({"message": f"{err.get('message')}"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            return Response({"message": "Rate limit error"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.InvalidRequestError as e:
            print(e)
            # Invalid parameters were supplied to Stripe's API
            return Response({"message": "Invalid parameters"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            return Response({"message": "Not authenticated"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            return Response({"message": "Network error"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            return Response({"message": "Something went wrong. You were not charged. Please try again."}, status=HTTP_400_BAD_REQUEST)

        except Exception as e:
            # send an email to ourselves
            return Response({"message": "A serious error occurred. We have been notifed."}, status=HTTP_400_BAD_REQUEST)

        return Response({"message": "Invalid data received"}, status=HTTP_400_BAD_REQUEST)


class AddCouponView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            code = request.data.get('code', None)
            if code is None:
                return Response({'message':'Sorry this coupon is not valid'},
                status=HTTP_400_BAD_REQUEST)
            order = Order.objects.get(user=request.user, ordered=False)
            coupon = get_object_or_404(Coupon, code=code)
            order.coupon = coupon
            order.save()
            return Response(status=HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            raise Http404("Sorry no active order found")
            # return Response({'message':'Sorry no active order found'},
            #     status=HTTP_400_BAD_REQUEST)
    

class ItemImagesView(APIView):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug' or None)
        if slug is None:
            return Response({'message':'No item specified'},
                status=HTTP_400_BAD_REQUEST)
        item = get_object_or_404(Item, slug=slug)
        item_images = ItemImage.objects.filter(item=item)
        images = ItemImageSerializer(item_images, many=True).data
        return Response(images, status=HTTP_200_OK)


class ItemDetailView(RetrieveAPIView):
    serializer_class = ItemSerializer
    # permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            slug = self.kwargs.get('slug' or None)
            item = Item.objects.get(slug=slug)
            return item
        except ObjectDoesNotExist:
            raise Http404("You do not have an active order")
