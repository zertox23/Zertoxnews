from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="اسم المستخدم",
        widget=forms.TextInput(attrs={"placeholder": "اسم المستخدم"}),
        error_messages={
            "required": "هذا الحقل مطلوب",
            "unique": "اسم المستخدم موجود بالفعل",
        },
    )
    password1 = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={"placeholder": "كلمة المرور"}),
        error_messages={
            "required": "هذا الحقل مطلوب",
        },
    )
    password2 = forms.CharField(
        label="أكد كلمة المرور",
        widget=forms.PasswordInput(attrs={"placeholder": "أكد كلمة المرور"}),
        error_messages={
            "required": "هذا الحقل مطلوب",
        },
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/1")
        else:
            messages.warning(request, ("حدث خطأ اثناء تسجيل الدخول"))
            return redirect("/authinticate/login/")

    else:
        return render(request, "authinticate/login.html", {})


# Create your views here.


def logout_user(request):
    logout(request)
    messages.success(request, ("تم طردك من القروب"))
    return redirect("/authinticate/login/")


def register_user(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            password1 = form.cleaned_data["password1"]
            password2 = form.cleaned_data["password2"]
            if password1 == password2:
                user = authenticate(username=username, password=password1)
                login(request, user)
                messages.success(request, ("مبروك عليك الحساب"))
                return redirect("/1")

    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})
    # return render(request,"authinticate/register.html")
