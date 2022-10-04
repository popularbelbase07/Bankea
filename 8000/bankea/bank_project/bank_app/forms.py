from random import choices
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .models import Customer, Account, Rank, BankList
from .currency_api import get_symbols
from crispy_bootstrap5.bootstrap5 import FloatingField


class TransferForm(forms.Form):
    amount  = forms.DecimalField(label='Amount', max_digits=10)
    debit_account = forms.ModelChoiceField(label='Debit Account', queryset=Customer.objects.none()) 
    debit_text = forms.CharField(label='Debit Account Description', max_length=25)
    credit_account = forms.UUIDField(label='Credit Account Number')
    # credit_account = forms.ModelChoiceField(label='Credit Account', queryset=Customer.objects.none())
    credit_text = forms.CharField(label='Credit Account Description', max_length=25)

    def clean(self):
        super().clean()

        # Checking if credit account exists in the db
        credit_account = self.cleaned_data.get('credit_account')
        print(credit_account)
        # try:
        #     Account.objects.get(pk= credit_account)
        # except ObjectDoesNotExist:
        #     self._errors['credit_account'] = self.error_class(['Credit account does not exist.'])

        # Ensure positive amount
        if self.cleaned_data.get('amount') < 0:
            self._errors['amount'] = self.error_class(['Amount must be positive.'])

        return self.cleaned_data


class CreateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean(self):
        super().clean()
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username):
            self._errors['username'] = self.error_class(['Username already exists.'])
        return self.cleaned_data 
    

class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=60,
    required=True,
    widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    first_name = max_length=60, 
    required=True, 
    widget=forms.TextInput(attrs={'class': 'form-control'})
    
    last_name = max_length=60, 
    required=True,
    widget=forms.TextInput(attrs={'class': 'form-control'})

    email = max_length=60, 
    required=True,
    widget=forms.TextInput(attrs={'class': 'form-control'})

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('rank','phone')


class UpdateCustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ('user', 'rank')
        # fields = ('phone',)
        
class staffUpdateCustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ('user',)


class NewAccountForm(forms.ModelForm):
    codes = get_symbols()
    name = forms.CharField(label='name')
    currency_type = forms.ChoiceField(label='currency', choices= [x for x in codes], initial='DKK')
    is_loan = forms.BooleanField(label='is_loan', required=False)
    

    class Meta:
        model = Account
        fields = ('name', 'currency_type', 'is_loan')
    
    def clean(self):
        super().clean()
        account_name = self.cleaned_data.get('name')
        if Account.objects.filter(name=account_name):
            self._errors['name'] = self.error_class(['Account already exists.'])
        return self.cleaned_data 

class AddNewRankForm(forms.ModelForm):
    class Meta:
        model = Rank
        fields = ('rank_type','value')

class UpdateRankForm(forms.ModelForm):
    rank_type = forms.CharField(label='Rank Type', disabled=True)
    created_at = forms.DateTimeField(label='Created_at', disabled=True)


    class Meta:
        model = Rank
        fields = ('rank_type','value')

class ExternalTransferForm(forms.Form):
    amount  = forms.DecimalField(label='Amount', max_digits=10)
    debit_account = forms.ModelChoiceField(
        label='Debit Account', queryset=Customer.objects.none())  # here we have problem
    debit_text = forms.CharField(label='Debit Account Text', max_length=25)
    external_credit_account = forms.CharField(label='External Credit Account Number')
    credit_text = forms.CharField(label='Credit Account Text', max_length=25)

    def clean(self):
        super().clean()

        # Ensure positive amount
        if self.cleaned_data.get('amount') < 0:
            self._errors['amount'] = self.error_class(['Amount must be positive.'])

        return self.cleaned_data

# dummy choices 
choices=INTEGER_CHOICES = [('', '')]

class CurrencyForm(forms.Form):
    source_currency_value = forms.DecimalField(label='Amount')
    source_currency_code = forms.CharField(label='From', widget = forms.Select(choices=INTEGER_CHOICES))
    target_currency_code = forms.CharField(label='To', widget = forms.Select(choices=INTEGER_CHOICES))


    def __init__(self, tuple_country_code, *args, **kwargs):
        # required to set the initial form drop down with choices
        self.tuple_country_code = tuple_country_code
        super(CurrencyForm,self).__init__(*args, **kwargs)

        self.fields['source_currency_code'].widget.choices = self.tuple_country_code
        self.fields['target_currency_code'].widget.choices = self.tuple_country_code
    
    
    
class AddNewBankForm(forms.ModelForm):
        
    class Meta:
        model = BankList
        fields = ('bank_name', 'host_name')

class UpdateBankForm(forms.ModelForm):
    bank_name = forms.CharField(label='Bank Name')
    host_name = forms.CharField(label='Host Name' ,required=False)


    class Meta:
        model = BankList
        fields = ('bank_name','host_name')
