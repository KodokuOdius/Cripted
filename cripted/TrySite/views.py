from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, View
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy, reverse
from django import forms
from django.http import HttpRequest
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.validators import validate_email
from . import models
from . import chiper

from typing import *


class UserForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    masterpass = forms.CharField(widget=forms.PasswordInput)

    def clean_masterpass(self):
        masterpass = self.cleaned_data["masterpass"]

        user = User.objects.get(username=self.cleaned_data["username"])
        private = str.encode(models.UserKey.objects.get(user_id=user.pk).private)

        if not chiper.is_masterpass(private, masterpass=str(self.cleaned_data["masterpass"])):
            raise ValidationError("Incorrect Masterpass")

        return masterpass

class CreateUserForm(forms.ModelForm):
    repeated = forms.CharField(widget=forms.PasswordInput, label="Repeat Password")
    masterpass = forms.CharField(widget=forms.PasswordInput)

    def clean_repeated(self):
        if repeated := self.cleaned_data["repeated"] != self.cleaned_data["password"]:
            raise ValidationError("Passwords don`t match")
        return repeated

    def clean_masterpass(self):
        masterpass = self.cleaned_data["masterpass"]

        if masterpass.lower() == self.cleaned_data["password"].lower():
            raise ValidationError("the Masterpass should not similar like a Password")

        return masterpass
    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            "password": forms.PasswordInput,
            "email": forms.TextInput(attrs={ 'required': 'true' })
        }
        help_texts = {"username": None}

class PasswordForm(forms.ModelForm):
    masterpass = forms.CharField(widget=forms.PasswordInput)

    @classmethod
    def add_user(cls, user):
        cls.user = user
        # print("USER_USER_USER", user.pk)

    def clean_masterpass(self):
        masterpass = self.cleaned_data["masterpass"]

        user = User.objects.get(username=self.user)
        private = str.encode(models.UserKey.objects.get(user_id=user.pk).private)

        if not chiper.is_masterpass(private, masterpass=self.cleaned_data["masterpass"]):
            raise ValidationError("Incorrect Masterpass")

        return masterpass

    class Meta:
        model = models.UserPassword
        fields = ["login", "password"]
        widgets = {
            "password": forms.PasswordInput
        }


class ShareForm(forms.Form):
    login = forms.CharField()# disabled=True)
    user = forms.CharField()
    masterpass = forms.CharField(widget=forms.PasswordInput)

    @classmethod
    def add_user(cls, user):
        cls.user = user

    def clean_user(self):
        if not User.objects.get(username=(user := self.cleaned_data["user"])):
            raise ValidationError("No such User")
        return user

    def clean_masterpass(self):
        masterpass = self.cleaned_data["masterpass"]

        user = User.objects.get(username=self.user)
        private = str.encode(models.UserKey.objects.get(user_id=user.pk).private)

        if not chiper.is_masterpass(private, masterpass=self.cleaned_data["masterpass"]):
            raise ValidationError("Incorrect Masterpass")

        return masterpass

class DeleteForm(forms.Form):
    login = forms.CharField() # disabled=True)
    masterpass = forms.CharField(widget=forms.PasswordInput)

    @classmethod
    def add_user(cls, user):
        cls.user = user

    def clean_masterpass(self):
        masterpass = self.cleaned_data["masterpass"]

        user = User.objects.get(username=self.user)
        private = str.encode(models.UserKey.objects.get(user_id=user.pk).private)

        if not chiper.is_masterpass(private, masterpass=self.cleaned_data["masterpass"]):
            raise ValidationError("Incorrect Masterpass")

        return masterpass


class HomeView(View):
    # template_name="./site/main.html"
    title = "Main Page"
    form = None

    def render(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            template_name = "./site/home.html"
        else:
            template_name = "./site/land.html"
        return render(request, template_name, context=self.get_context_data(*args, **kwargs))

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            print("===========> FORM POST", *request.POST.items())
            if request.POST.get("user"):
                share_form = ShareForm(request.POST or None)
                share_form.add_user(request.user)
                if share_form.is_valid():
                    clean = share_form.cleaned_data

                    recipient = User.objects.get(username=clean["user"])
                    # print(recipient)
                    public_recipient = models.UserKey.objects.get(user_id=recipient.pk).public
                    password = models.UserPassword.objects.get(login=clean["login"]).password
                    private = models.UserKey.objects.get(user_id=request.user.id).private
                    master = clean["masterpass"]

                    encrypt_session, nonce, tag, chiper_text = map(lambda part: str.encode(part, encoding="latin-1"), password.split("===()==="))
                    decrypted_password = chiper.decrypt(
                            private=str.encode(private), masterpass=master,
                            encrypt_session=encrypt_session, tag=tag,
                            nonce=nonce, cryped_data=chiper_text
                        )

                    models.UserPassword.objects.create(
                        user=recipient,
                        login=clean["login"],
                        password="===()===".join(map(
                            lambda _bytes: _bytes.decode(encoding="latin-1"),
                            chiper.encrypt(str.encode(public_recipient), data=decrypted_password)
                            ))
                    )

                    # print("===========> DONE SHARE!")

                    return HttpResponseRedirect(reverse_lazy("main"))
                else:
                    return self.render(request, modal=share_form, *args, **kwargs)

            if len(request.POST.keys()) == 3:
                delete_form = DeleteForm(request.POST or None)
                delete_form.add_user(request.user)
                if delete_form.is_valid():
                    login_pass = request.POST.get("login")
                    password = models.UserPassword.objects.get(user_id=request.user.pk, login=login_pass)
                    password.delete()
                    print("Deleted")

                    return HttpResponseRedirect(reverse_lazy("main"))
                else:
                    return self.render(request, modal=delete_form, *args, **kwargs)

            form = PasswordForm(request.POST or None)
            form.add_user(request.user)
            if form.is_valid():
                clean = form.cleaned_data
                public = models.UserKey.objects.get(user_id=request.user.id).public

                # encrypt_session, nonce, tag, chiper_text = chiper.encrypt(public, str.encode(clean["password"]))
                # all bytes
                # print(type(encrypt_session), type(nonce), type(tag), type(chiper_text))

                models.UserPassword.objects.create(
                    user=request.user,
                    login=clean["login"],
                    password="===()===".join(map(
                        lambda _bytes: _bytes.decode(encoding="latin-1"), 
                        chiper.encrypt(str.encode(public), str.encode(clean["password"]))
                        ))
                )

                return HttpResponseRedirect(reverse_lazy("main"))
            else:
                return self.render(request, passform=form, *args, **kwargs)

        self.form = UserForm(request.POST)
        if self.form.is_valid():
            clean = self.form.cleaned_data
            user = authenticate(username=clean["username"], password=clean["password"])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    request.session["master"] = request.POST.get("masterpass")
                    return HttpResponseRedirect(reverse_lazy("main"))

        return self.render(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # print("GET", *request.GET.keys())
        # master = None
        passwords = []
        if not request.user.is_authenticated:
            self.form = UserForm()
            self.title = "Login Page"
        elif master := request.session.get("master"):
            # master = request.session.get("master")
            request.session["master"] = None
            for user_data in models.UserPassword.objects.filter(user=request.user):
                try:
                    encrypt_session, nonce, tag, chiper_text = map(lambda part: str.encode(part, encoding="latin-1"), user_data.password.split("===()==="))
                    private = str.encode(models.UserKey.objects.get(user=request.user).private)
                    password = chiper.decrypt(
                            private=private, masterpass=master,
                            encrypt_session=encrypt_session, tag=tag,
                            nonce=nonce, cryped_data=chiper_text
                        )
                    passwords.append((user_data.login, password.decode()))
                except Exception as ex:
                    print(ex)
            
        if request.GET.get("act", "") == "logout" and request.user.is_authenticated:
            logout(request)
            return HttpResponseRedirect(reverse_lazy("main"))
            
        return self.render(request, passwords=passwords, *args, **kwargs)


    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        # print("CONTEXT DATA -> ", kwargs.get("masterpass"))
        context = {"title": self.title, "form": self.form}
        return context | kwargs


class CreateUser(View):
    form = None

    def render(self, request, *args, **kwargs):
        return render(request, "./site/create.html", context=self.get_context_data(*args, **kwargs))


    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.form = CreateUserForm(request.POST)
        if self.form.is_valid():
            clean = self.form.cleaned_data
            user = User.objects.create_user(username=clean["username"], email=clean["email"])
            user.set_password(clean["password"])
            user.save()
            public, private = chiper.get_keys(masterpass=clean["masterpass"])

            models.UserKey.objects.create(
                user=user,
                public=public.decode(),
                private=private.decode()
            )
            print("===========> CREATION DONE!")

            return HttpResponseRedirect(reverse_lazy("main"))

        return self.render(request, *args, **kwargs)


    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy("main"))
        else:
            self.form = CreateUserForm()
        return self.render(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = {"title": "Creation", "form": self.form}
        return context | kwargs


def add_pass(request):
    return render(
        request,
        template_name="./site/modalpass.html",
        context={"modal": PasswordForm(), "btn": "add"}
    )

def share_pass(request):
    return render(
        request,
        template_name="./site/modalpass.html",
        context={"modal": ShareForm(), "btn": "share"}
    )

def delete_pass(request):
    return render(
        request,
        template_name="./site/modalpass.html",
        context={"modal": DeleteForm(), "btn": "delete"}
    )

