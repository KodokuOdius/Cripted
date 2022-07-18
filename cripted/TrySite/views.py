from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, View
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy, reverse
from django import forms
from django.http import HttpRequest
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
# from django.utils.translation import ugettext_lazy as _

from typing import *


# Create your views here.
class LogInForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    masterpass = forms.CharField(widget=forms.PasswordInput)

    def clean_masterpass(self):
        masterpass = self.cleaned_data['masterpass']

        if masterpass.lower() == self.cleaned_data["password"].lower():
            raise ValidationError('the Masterpass should not similar like a Password')

        return masterpass


class HomeView(View):
    template_name="./site/main.html"
    title = "Main Page"
    form = None

    def render(self, request, *args, **kwargs):
        return render(request, self.template_name, context=self.get_context_data(*args, **kwargs))

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        print("POST", *request.POST.keys())
        self.form = LogInForm(request.POST)
        if self.form.is_valid():
            clean = self.form.cleaned_data
            user = authenticate(username=clean['username'], password=clean['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    request.session["master"] = request.POST.get("masterpass")
                    return HttpResponseRedirect(reverse_lazy('main'))

        return self.render(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        print("GET", *request.GET.keys())
        print(*request.COOKIES.items())
        master = None
        if not request.user.is_authenticated:
            self.form = LogInForm()
            self.title = "Login Page"
            
        if request.GET.get("act", "") == "logout" and request.user.is_authenticated:
            logout(request)
            return HttpResponseRedirect(reverse_lazy('main'))
        if request.session.get("master", None):
            master = request.session.get("master", None)
            request.session["master"] = None
            
        return self.render(request, *args, **kwargs, masterpass=master)


    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        print("CONTEXT DATA -> ", kwargs.get("masterpass"))
        context = {"title": self.title, "form": self.form, "masterpass": kwargs.get("masterpass")}
        return context
