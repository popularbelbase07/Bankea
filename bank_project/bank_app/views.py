from decimal import Decimal
from secrets import token_urlsafe
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from .forms import TransferForm, CreateUserForm, UpdateCustomerForm, UpdateUserForm, CustomerForm, UpdateUserForm, NewAccountForm, CustomerForm,AddNewRankForm,UpdateRankForm,ExternalTransferForm
from .models import Account, Ledger, Customer, Rank
from .errors import InsufficientFunds
#REST 
from .external_resquests import send_trasfer, confirm_transfer
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

    account_iban = request.user.customer.default_account
    #iban = account_iban.get_iban
    accounts = request.user.customer.accounts
    for account in accounts:
        account.modify_account_type
    context = {
        'accounts': accounts,
        #'iban':iban,
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
            # return redirect(to='/api/v1/')
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

# Staff views page     
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
        # 'type': type,
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
        customer_form = UpdateCustomerForm(request.POST, instance=customer)
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
            'title': 'Create Loan Error',
            'error': 'Loan could not be completed.'
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
        form.fields['credit_account'].queryset = request.user.customer.accounts
        if form.is_valid():
            amount = form.cleaned_data['amount']
            debit_account = Account.objects.get(pk=form.cleaned_data['debit_account'].pk)
            debit_text = form.cleaned_data['debit_text']
            credit_account = Account.objects.get(pk=form.cleaned_data['credit_account'].pk)
            print(credit_account.pk)
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
            
            # GET BANK NAME, CURRENCY AND PK OF EXTERNAL ACCOUNT
            external_bank = external_credit_account[ 0 : 4 ]
            external_currency =  external_credit_account[ 4 : 7 ]
            external_pk =  external_credit_account[ 7 : 8 ]
            user = request.user
            try:
                transfer_allowed = Ledger.check_external_transfer(debit_account, amount)            
                if transfer_allowed:
                    token = generate_token(user,debit_account.currency_type, external_pk, amount, external_currency, credit_text)
                    response = send_trasfer(token, external_bank)
                    if response.status_code == 201:
                        transfer = Ledger.external_transfer(amount, debit_account, debit_text, credit_text)

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
    response = {"Success": "Transfer received"}
    if request.method == 'POST':
        token = request.META.get('HTTP_AUTHORIZATION')[9:-1]
        token_data = jwt.decode(token, "secret", algorithms=["HS256"], verify=True)
        # print(token_data)
        serializer = ExternalTransferSerializer(data=token_data)
        
        if serializer.is_valid():
            serializer.save()
            # print(serializer.data)
            process_external_transfer(serializer.data)
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""Process the received transfer from external account
and save it to Ledger table, then sends a PUT request """
def process_external_transfer(data):
    print(data)
    account = Account.objects.get(pk=data['account_pk'])
    if account:
        transfer = Ledger.incoming_external_transfer(data['amount'], account, data['credit_text'])
        # return transaction_details(request, transfer)
        if transfer:
            # print(transfer)
            response = confirm_transfer('BNK2',str(transfer))
            print(response)  


@api_view(['PUT'])
@permission_classes([AllowAny])
def get_external_transfer_number(request):
    if request.method == 'PUT':
        print(json.loads(request.body))
        return Response(status=status.HTTP_200_OK)



#########################################
 # Serialize queryset methods starts here ----
    
class OneAccount(generics.RetrieveUpdateDestroyAPIView):
    permissions_classes = (IsAdminUser,)
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    

class AccountDetail(generics.ListCreateAPIView):
    permissions_classes = (IsAdminUser,)
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class OneRankAPI(generics.RetrieveUpdateDestroyAPIView):
    permissions_classes = (IsAdminUser,)
    queryset = Rank.objects.all()
    serializer_class = RankSerializer


class RankAPI(generics.ListCreateAPIView):
    permissions_classes = (IsAdminUser,)
    queryset = Rank.objects.all()
    serializer_class = RankSerializer
     

# get all and create user 
class UserAPI(generics.ListCreateAPIView):
    permissions_classes = (IsAdminUser,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class OneUserAPI(generics.RetrieveUpdateDestroyAPIView):
    permissions_classes = (IsAdminUser,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


#
class CustomerAPI(generics.ListCreateAPIView):
    permissions_classes = (IsAdminUser,)
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
class OneCustomerAPI(generics.RetrieveUpdateDestroyAPIView):
    permissions_classes = (IsAdminUser,)
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
    def update(self, instance, validated_data):
        # get the nested objects list
        customer_data = validated_data.pop('user')
        # get all nested objects related with this instance and make a dict(id, object)
        customer_dict = dict((i.id, i) for i in instance.users.all())

        for user in customer_data:
            if 'id' in user:
                # if exists id remove from the dict and update
                customer_data = customer_dict.pop(user['id'])
                customer_data.first_name = user['first_name']
                customer_data.last_name = user['last_name']
                customer_data.email = user['email']
                customer_data.username = user['username']
                customer_data.phone = user['phone']
                customer_data.created_at = user['created_at']
                customer_data.save()
            else:
                # else create a new object
                customer_data.objects.create(product=instance, **customer_data)
