from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.shortcuts import render, redirect

from .forms import ItemForm

class PartnersHome(View):
    @method_decorator(login_required(login_url='/accounts/login/'))
    def get(self, *args, **kwargs):
        context = {
            'form': ItemForm(),
        }
        return render(self.request, 'customers/partners_home.html', context)

    def post(self, *args, **kwargs):
        form = ItemForm(self.request.POST, self.request.FILES or None)
        try:
            if form.is_valid():
                form.save()
                form.clear()
                return redirect('customers:partners_home')
        except Exception as e:
            print('Exception while creating item by partner: ', e)
            return redirect('customers:partners_home')
