from multiprocessing import context
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required


def home(request):
    context={}
    
    return render(request, 'bank_app/home.html', context)

@login_required
def staff_page(request):
    context={}
    
    return render(request, 'bank_app/staff_page.html', context)
