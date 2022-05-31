from lib2to3.pgen2 import token
from django.shortcuts import render, reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.http import HttpResponseRedirect

#from . models import PasswordResetRequest


def login(request):
    context = {}

    if request.method == "POST":
      user = authenticate(request, username=request.POST['user'], password=request.POST['password'])
      if user:
            django_login(request, user)
            return HttpResponseRedirect(reverse('bank_app:staff_page'))
      else:
            context = {
               'error': 'Bad username or password.'
            }
    return render(request, 'login_app/login.html', context)


def logout(request):
   django_logout(request)
   return render(request, 'login_app/login.html')

def sign_up(request):
   context = {}
   if request.method == "POST":
      password = request.POST['password']
      repeat_password = request.POST['password_repeat']
      user_name = request.POST['user']
      email = request.POST['email']
      if password == repeat_password:
            if User.objects.create_user(user_name, email, password):
               return HttpResponseRedirect(reverse('login_app:login'))
            else:
               context = {
                  'error': 'Your account is not created - please try again.'
               }
      else:
            context = {
               'error': 'passwords are not matched. Please try again.'
            }
   return render(request, 'login_app/sign_up.html', context)


