from django.views.generic import View
from django.shortcuts import render


class PartnersHome(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'customers/partners_home.html', {})
