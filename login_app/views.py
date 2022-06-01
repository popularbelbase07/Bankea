from http.client import HTTPMessage, HTTPResponse
from lib2to3.pgen2 import token
from urllib import response
from django.shortcuts import render, reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.http import HttpResponse, HttpResponseRedirect
from . models import PasswordResetRequest


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



def request_password_reset(request):
    if request.method == "POST":
        old_user = request.POST['username']
        user = None

        if old_user:
            try:
                user = User.objects.get(username=old_user)
            except:
                print(f"Password request is invalid: {old_user}")
        else:
            new_user = request.POST['email']
            try:
                user = User.objects.get(email=old_user)
            except:
                print(f"Invalid password request: {old_user}")
        if user:
            reset_pass = PasswordResetRequest()
            reset_pass.user = user
            reset_pass.save()
            print(reset_pass)
          
            return HttpResponseRedirect(reverse('login_app:password_reset'))

    return render(request, 'login_app/request_password_reset.html')
 
 

def password_reset(request):
    if request.method == "POST":
        old_user = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        token = request.POST['token']

        if password == confirm_password:
            try:
                reset_pass = PasswordResetRequest.objects.get(token=token)
                reset_pass.save()
            except:
                print("Invalid password reset attempt.")
                return render(request, 'login_app/password_reset.html')

            user = reset_pass.user
            user.set_password(password)
            user.save()
            return HttpResponseRedirect(reverse('login_app:login'))

    return render(request, 'login_app/password_reset.html')
