from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.shortcuts import render, redirect

from .forms import ItemForm, ItemImageForm
from core.models import ItemImage

class PartnersHome(View):
    def __init__(self):
        self.ImageFormset = modelformset_factory(ItemImage, 
                                            form=ItemImageForm, 
                                            extra=5)
        super(PartnersHome, self).__init__()

    @method_decorator(login_required(login_url='/accounts/login/'))
    def get(self, *args, **kwargs):
        # image_formset = modelformset_factory(ItemImage, 
        #                                     form=ItemImageForm, 
        #                                     extra=5)
        context = {
            'item_form': ItemForm(prefix='item'),
            'image_formset': self.ImageFormset(prefix='images_form', queryset=ItemImage.objects.none())
        }
        return render(self.request, 'customers/partners_home.html', context)

    def post(self, *args, **kwargs):
        try:
            image_formset = self.ImageFormset(self.request.POST, 
                                            self.request.FILES,
                                            queryset=ItemImage.objects.none(),
                                            prefix='images_form')
            item_form = ItemForm(self.request.POST,
                                self.request.FILES,
                                prefix='item' or None)
            if item_form.is_valid() and image_formset.is_valid():
                item = item_form.save()
                for form in image_formset.cleaned_data:
                    #this helps to not crash if the user   
                    #do not upload all the photos
                    if form:
                        image = form['image']
                        item_image = ItemImage(item=item, image=image)
                        item_image.save()
                messages.success(self.request, 'Successfully added new item')
                return HttpResponseRedirect('customers:partners_home')
            else:
                return redirect('customers:partners_home')
        except Exception as e:
            print('Exception while creating item by partner: ', e)
            messages.error(self.request, 'Sorry! Unable to add the item.') 
            return redirect('customers:partners_home')
