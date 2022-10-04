from ast import arg
from decimal import Decimal
from itertools import groupby
from multiprocessing import context
from re import template
from secrets import token_urlsafe
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.shortcuts import render, reverse, get_object_or_404, redirect
# from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from .forms import TransferForm, CreateUserForm, UpdateCustomerForm, UpdateUserForm, staffUpdateCustomerForm, CustomerForm, UpdateUserForm, NewAccountForm, CustomerForm, AddNewRankForm, UpdateRankForm, ExternalTransferForm, AddNewBankForm, UpdateBankForm
from .models import User, Account, Ledger, Customer, Rank, BankList
from django.db.models import Q
from .errors import InsufficientFunds, TransferNotAllowed
#REST 
from .external_resquests import send_trasfer, confirm_transfer
# from .process_external_transfer import process_external_transfer
from .generate_token import generate_token
#REST 
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import jwt
from .permissions import IsAdminUser
from .serializers import AccountSerializer, UserSerializer, CustomerSerializer, RankSerializer, ExternalTransferSerializer
import requests
import json
from django.conf import settings
from bank_app import forms
# For print the pdf files
from bank_app.generatepdf import generate_pdf




# Common dashboard 
@login_required(login_url='')
def index(request):
    if request.user.is_staff:
        return HttpResponseRedirect(reverse('bank_app:staff_dashboard'))
    else:
        return HttpResponseRedirect(reverse('bank_app:dashboard'))



@login_required
def dashboard(request):
    assert not request.user.is_staff, 'Staff user routing customer view.'

    customer_rank = request.user.customer.rank
    account_balance = request.user.customer.default_account
    balance = (round(account_balance.balance, 2))
    account_iban = request.user.customer.default_account
    iban = account_iban.get_iban
    accounts = request.user.customer.accounts
    for account in accounts:
        account.modify_account_type
    context = {
        'accounts': accounts,
        'accountNo':iban,
        'balance': balance,
        'rank':customer_rank,
    }
    return render(request, 'bank_app/dashboard.html', context)

@login_required
def user_profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'GET':
        user_form = UpdateUserForm(instance=user)
    elif request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Profile Updated')
    context = {
        'user': user,
        'user_form': user_form,
    }
    return render(request, 'bank_app/user_profile.html', context)

@login_required
def customer_profile(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'GET':
        user_form = UpdateUserForm(instance=customer.user)
        customer_form = UpdateCustomerForm(instance=customer)
    elif request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=customer.user)
        customer_form = UpdateCustomerForm(request.POST, instance=customer)
        if user_form.is_valid() and customer_form.is_valid():
            user_form.save()
            customer_form.save()
            messages.success(request, 'Profile Updated')
            # return redirect(to='/')
    context = {
        'customer': customer,
        'user_form': user_form,
        'customer_form': customer_form,
    }

    return render(request, 'bank_app/customer_profile.html', context)

@login_required
def staff_dashboard(request):
    assert request.user.is_staff, 'Customer user routing staff view.'

    return render(request, 'bank_app/staff_dashboard.html')


# Customer Look Up page provides customers list
@login_required
def search_partial(request):
    assert request.user.is_staff, 'Customer user routing staff view.'

    search_term = request.POST['search_term']
    customers = Customer.search(search_term)
    context = {
        'customers': customers,
    }
    return render(request, 'bank_app/search_partial.html', context)


# Showing all the account a customer has in the customer details page
@login_required
def staff_account_details(request, pk):
    assert request.user.is_staff, 'Customer user routing staff view.'

    account = get_object_or_404(Account, pk=pk)
   
   
    type = account.modify_account_type
    context = {
        'account': account,
        'type': type,
    }
    return render(request, 'bank_app/account_details.html', context)


@login_required
def account_list_partial(request, pk):
    assert request.user.is_staff, 'Customer user routing staff view.'

    customer = get_object_or_404(Customer, pk=pk)
    accounts = customer.accounts
  
    for account in accounts:
            account.modify_account_type
    context = {
        'accounts': accounts,
    }
    return render(request, 'bank_app/account_list_partial.html', context)


@login_required
def customer_account_details(request, pk):
    assert not request.user.is_staff, 'Staff user routing customer view.'

    account = get_object_or_404(Account, user=request.user, pk=pk)
    account = account.modify_account_type
    context = {
        'account': account,
    }
    return render(request, 'bank_app/customer_ac_details.html', context)




# provides details of the customer & can update/ show add accounts form to the customer profile 
@login_required
def customer_details(request, pk):
    assert request.user.is_staff, 'Customer user routing staff view.'
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'GET':
        user_form = CreateUserForm(instance=customer.user)
        customer_form = CustomerForm(instance=customer)
    elif request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=customer.user)
        customer_form = staffUpdateCustomerForm(
            request.POST, instance=customer)
        if user_form.is_valid() and customer_form.is_valid():
            user_form.save()
            customer_form.save()
    new_account_form = NewAccountForm()
    context = {
        'customer': customer,
        'user_form': user_form,
        'customer_form': customer_form,
        'new_account_form': new_account_form,
    }
    return render(request, 'bank_app/customer_details.html', context)


# creating new customer
@login_required
def new_customer(request):
    assert request.user.is_staff, 'Customer user routing staff view.'

    if request.method == 'POST':
        new_user_form = CreateUserForm(request.POST)
        customer_form = CustomerForm(request.POST)
        if new_user_form.is_valid() and customer_form.is_valid():
            username    = new_user_form.cleaned_data['username']
            first_name  = new_user_form.cleaned_data['first_name']
            last_name   = new_user_form.cleaned_data['last_name']
            email       = new_user_form.cleaned_data['email']
            password    = token_urlsafe(16)
            rank        = customer_form.cleaned_data['rank']
            # customer_number = customer_form.cleaned_data['customer_number']
            phone       = customer_form.cleaned_data['phone']
            try:
                user = User.objects.create_user(
                        username=username,
                        password=password,
                        email=email,
                        first_name=first_name,
                        last_name=last_name
                )
                print(f'********** Username: {username} -- Password: {password}')
                Customer.objects.create(user=user, rank=rank, phone=phone)
                return customer_details(request, user.pk)
            except IntegrityError:
                context = {
                    'title': 'Database Error',
                    'error': 'User could not be created.'
                }
                return render(request, 'bank_app/error.html', context)
    else:
        new_user_form = CreateUserForm()
        customer_form = CustomerForm()
    context = {
        'new_user_form': new_user_form,
        'customer_form': customer_form,
    }
    return render(request, 'bank_app/new_customer.html', context)


# Adding new accounts to the customer profile
@login_required
def new_account_partial(request, user):
    assert request.user.is_staff, 'Customer user routing staff view.'  
    
    if request.method == 'POST':
        new_account_form = NewAccountForm(request.POST)
        
        if new_account_form.is_valid():

            Account.objects.create(user=User.objects.get(pk=user), name=new_account_form.cleaned_data['name'], currency_type=new_account_form.cleaned_data['currency_type'], is_loan= new_account_form.cleaned_data['is_loan']) 
    return HttpResponseRedirect(reverse('bank_app:customer_details', args=(user,)))


@login_required
def add_new_bank(request):
    assert request.user.is_staff, 'Routing staff view.'
    
    bank_list = BankList.objects.all()
       
    if request.method == 'POST':
        new_bank_form = AddNewBankForm(request.POST)

        if new_bank_form.is_valid():
            BankList.objects.create(
            bank_name = new_bank_form.cleaned_data['bank_name'],
            host_name = new_bank_form.cleaned_data['host_name']
            )
    
    new_bank_form = AddNewBankForm()

    context = {
        'banklist': bank_list,
        'new_bank_form': new_bank_form,
        }
    return render(request, 'bank_app/add_new_bank.html', context)





@login_required
def transaction_details(request, transaction):
    movements = Ledger.objects.filter(transaction=transaction)
    if not request.user.is_staff:
        if not movements.filter(account__in=request.user.customer.accounts):
            raise PermissionDenied('Customer is not part of the transaction.')
    context = {
        'movements': movements,
        'user':request.user,

    }
    return render(request, 'bank_app/transaction_details.html', context)


@login_required
def make_loan(request):
    assert not request.user.is_staff, 'Staff user routing customer view.'  
    if not request.user.customer.can_make_loan:
        context = {
                'title': 'Loan not allowed',
                'error': 'You can not make loan with your rank.You need to upgrade your rank to make loan.'
                }
        return render(request, 'bank_app/error.html', context)
    
    if request.method == 'POST':
        request.user.customer.make_loan(Decimal(request.POST['amount']), request.POST['name'])
        return HttpResponseRedirect(reverse('bank_app:dashboard'))
    return render(request, 'bank_app/make_loan.html', {})
     


@login_required
def make_transfer(request):
    assert not request.user.is_staff, 'Staff user routing customer view.'

    if request.method == 'POST':
        form = TransferForm(request.POST)
        form.fields['debit_account'].queryset = request.user.customer.accounts
        # form.fields['credit_account'].queryset = request.user.customer.accounts
    
        if form.is_valid():
            amount = form.cleaned_data['amount']
            debit_account = Account.objects.get(pk=form.cleaned_data['debit_account'].pk)
            debit_text = form.cleaned_data['debit_text']
            print(form.cleaned_data['credit_account'])
            # credit_account = Account.objects.get(pk=form.cleaned_data['credit_account'].pk)
            credit_account = Account.objects.get(pk=form.cleaned_data['credit_account'])
            
            # print(credit_account.pk)
            credit_text = form.cleaned_data['credit_text']
            try:
                transfer = Ledger.transfer(amount, debit_account, debit_text, credit_account, credit_text)
                return transaction_details(request, transfer)
            except InsufficientFunds:
                    context = {
                        'title': 'Transfer Error',
                        'error': 'Insufficient funds for transfer.'
                    }
                    return render(request, 'bank_app/error.html', context)
            except  TransferNotAllowed:
                    context = {
                        'title': 'Transfer Error',
                        'error': 'Transfer forbidden to same account.'
                    }
                    return render(request, 'bank_app/error.html', context)
    else:
        form = TransferForm()
    form.fields['debit_account'].queryset = request.user.customer.accounts
    form.fields['credit_account'].queryset = request.user.customer.accounts
    context = {
        'form': form,
    }
    return render(request, 'bank_app/make_transfer.html', context)


#SENDER VIEW
"""Gets data from the form, send a request to the external bank, 
receives a response and adds the transaction to the Ledger"""
@login_required
def make_external_transfer(request):
    assert not request.user.is_staff, 'Staff user routing customer view.'
    if request.method == 'POST':
        form = ExternalTransferForm(request.POST)
        form.fields['debit_account'].queryset = request.user.customer.accounts
        if form.is_valid():
            amount = form.cleaned_data['amount']
            debit_account = Account.objects.get(pk=form.cleaned_data['debit_account'].pk)
            debit_text = form.cleaned_data['debit_text']
            external_credit_account = form.cleaned_data['external_credit_account']
            credit_text = form.cleaned_data['credit_text']
            print(len(external_credit_account))
            # GET BANK NAME, CURRENCY AND PK OF EXTERNAL ACCOUNT
            external_bank = external_credit_account[ 0 : 4 ]
            external_currency =  external_credit_account[ 4 : 7 ]
            external_pk =  external_credit_account[ 7 : 43 ]
            user = request.user
            try:
                transfer_allowed = Ledger.check_external_transfer(debit_account, amount)            
                if transfer_allowed:
                    token = generate_token(user,debit_account, external_pk, amount, external_currency, debit_text, credit_text)
                    response = send_trasfer(token, external_bank)
                    print(response)
                    if response.status_code == 201:
                        print(response.json())
                        # external_user = response.data
                        external_bank = User.objects.filter(username='external_bank').first()
                        try:
                            external_account = Account.objects.get(name= external_credit_account)
                        except Account.DoesNotExist:
                            external_account = Account.objects.create(user=external_bank, name= external_credit_account, currency_type=external_currency)
                            external_account.save()                        
                        print(f'external account founded: {external_account}')
                        transfer = Ledger.transfer(amount, debit_account, debit_text, external_account,credit_text)
                        print(external_account)
                        messages.success(request, response.text)
                        return transaction_details(request, transfer)
                    else:
                        print(response.json())
                        context = {
                            'title': 'External Transfer Error',
                            'error': 'There was a problem with the transfer.'
                        }
                        return render(request, 'bank_app/error.html', context)
                form = ExternalTransferForm()
            except InsufficientFunds:
                context = {
                    'title': 'Transfer Error',
                    'error': 'Insufficient funds for transfer.'
                }
                return render(request, 'bank_app/error.html', context)
    else:
        form = ExternalTransferForm()
    form.fields['debit_account'].queryset = request.user.customer.accounts
    context = {
        'form': form,
    }
    return render(request, 'bank_app/make_external_transfer.html', context)                   
    


#RECEIVER VIEWS
################
"""REST endpoint to receive the external POST request from external bank"""
@api_view(['POST'])
@permission_classes([AllowAny])
def transfer_details(request):
    response_success = {"success": "Transfer Succeed"}
    response_fail = {"failure": "There was a problem with your transfer"}
    if request.method == 'POST':
        token = request.META.get('HTTP_AUTHORIZATION')[9:-1]
        token_data = jwt.decode(token, "secret", algorithms=["HS256"], verify=True)
        # print(token_data)
        serializer = ExternalTransferSerializer(data=token_data)
        
        if serializer.is_valid():
            serializer.save()
            # print(serializer.data)
            response = process_external_transfer(serializer.data)
            print(f'this is the response from process: {response}')
            if response.status_code == 200:
                return Response(response_success, status=status.HTTP_201_CREATED)
            else:
                return Response(response_fail, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""Process the received transfer from external account
and save it to Ledger table, then sends a PUT request """
def process_external_transfer(data):
    print(f'this is the data to process: {data}')
    credit_account = Account.objects.get(pk=data['receiver_account_pk'])
    print(credit_account)
    user_id = credit_account.user_id
    user = User.objects.get(pk=user_id)
    if credit_account:
        external_bank = User.objects.get(username='external_bank')
        print(data['sender_account'])
    try:
        external_account = Account.objects.get(name=data['sender_account'])
    except Account.DoesNotExist:
        external_account = Account.objects.create(user=external_bank, name= data['sender_account'], currency_type=data['sender_currency'])
        external_account.save()
        
        print(f'external account founded in process: {external_account}')
    transfer = Ledger.receive_transfer(float(data['sender_amount']), external_account, data['receiver_credit_text'],credit_account, data['sender_account'])
            
    if transfer:
        bank = data['sender_account'][0:4]
        print(f'this the bank to confirm the transfer: {bank}')
        # print(transfer)
        r = confirm_transfer(bank,str(transfer), str(user))
        return r      


@api_view(['PUT'])
@permission_classes([AllowAny])
def get_external_transfer_confirmation(request):
    if request.method == 'PUT':
        print(f'from 8000: {json.loads(request.body)}')
        return Response(status=status.HTTP_200_OK)




@login_required
def currency_converter(request):
    api_request = requests.get("https://api.exchangerate.host/rates")
    currency_dict = json.loads(api_request.text)

    currency_rates = currency_dict['rates']
    list_of_country_currency_code = [x for x in currency_rates.keys()]
    country_codes = [tuple([x,x]) for x in list_of_country_currency_code]
    
    # initialize form with country currency code
    currency_form = forms.CurrencyForm(country_codes, request.POST or None)

    converted_currency = ""
    if request.method == "POST":
        if currency_form.is_valid():
            # values from the frontend input fields
            source_currency_code = currency_form.cleaned_data['source_currency_code']
            target_currency_code = currency_form.cleaned_data['target_currency_code']
            input_currency_value = currency_form.cleaned_data['source_currency_value']

            # get live amount of selected country 
            from_country_base_value = currency_rates[source_currency_code]
            to_country_base_value = currency_rates[target_currency_code]
            
            # calculate the converted currency
            converted_currency = (to_country_base_value / from_country_base_value) * float(input_currency_value)
            rounded_converted_currency = (round(converted_currency, 2))

            return render(request, 'bank_app/currency-converter.html', {'currency_form':currency_form, 'converted_currency':rounded_converted_currency})

    # form initialization
    context = {
        'currency_form': currency_form,
        'converted_currency': converted_currency
    } 
    return render(request, 'bank_app/currency-converter.html', context)

  
                
                
#function for printing pdf                
# def transaction_pdf(request):
#     template_name = "bank_app/transaction_details.html"
#     movements = Ledger.objects.all().order_by("transaction")
    
#     return generate_pdf(
#         template_name,
#         {
#         'movements' : movements,
#         'user': request.user
        
#         }
#     )

def transaction_pdf(request):
    # template_name = "bank_app/transaction_details.html"
    template_name = "bank_app/transaction_pdf.html"
    movements = Ledger.objects.all().order_by("transaction")

    return generate_pdf(
        template_name,
        {
            'movements' : movements,
             'user': request.user
        },
    )
    