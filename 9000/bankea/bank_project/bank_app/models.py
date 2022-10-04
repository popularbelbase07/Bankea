from __future__ import annotations
from pickle import TRUE
from unittest.util import _MAX_LENGTH
from django.db import models, transaction
from django.db.models import Q
from django.contrib.auth.models import User
from decimal import Decimal
from django.db.models.query import QuerySet
from django.conf import settings
from .errors import InsufficientFunds, TransferNotAllowed
from django.urls import reverse
from uuid import uuid4

class UID(models.Model):
    @classmethod
    @property
    def uid(cls):
        return cls.objects.create()

    def __str__(self):
        return f'{self.pk}'


class BankList(models.Model):
    bank_name= models.CharField(max_length= 10,unique=True)
    host_name=models.CharField(max_length=200,unique=True)
    

    def __str__(self):
        return f'{self.bank_name} - {self.host_name}'

    @property
    def get_host(self) -> str:
        return f'{self.host_name}'



class Rank(models.Model):
    rank_type = models.CharField(max_length=20, unique=True, db_index=True)
    value = models.IntegerField(unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def default_rank(cls) -> Rank:
        return cls.objects.all().aggregate(models.Min('value'))['value__min']


    def __str__(self):
        return f'{self.rank_type}'


class Customer(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    rank = models.ForeignKey(Rank, default=2, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)


    @property
    def full_name(self) -> str :
        return f'{self.user.first_name} {self.user.last_name}'
    
    @property
    def accounts(self) -> QuerySet:
        return Account.objects.filter(user=self.user)

    def __str__(self):
        return f'({self.rank}) - ({self.phone})'
    
    @property
    def can_make_loan(self) -> bool:
        return self.rank.value > settings.CUSTOMER_RANK_LOAN

    @property
    def default_account(self) -> Account:
        return Account.objects.filter(user=self.user).first()

    def make_loan(self, amount, name):
        assert self.can_make_loan, 'User rank does not allow for making loans.'
        assert amount >= 0, 'Negative amount not allowed for loan.'
        user_account = Account.objects.filter(user=self.user).earliest()               
        loan = Account.objects.create(user=self.user, name=f'Loan: {name}', currency_type = user_account.currency_type, is_loan=True )
        Ledger.transfer(
            amount,
            loan,
            f'Loan paid out to account {self.default_account}',
            self.default_account,
            f'Credit from loan {loan.pk}: {loan.name}',
            is_loan= True
        )
    @classmethod
    def search(cls, search_term):
        return cls.objects.filter(
            # Querying with Django Q objects , Q object encapsulates a SQL expression in a Python object
            Q(user__username__contains=search_term) |
            Q(user__first_name__contains=search_term) |
            Q(user__last_name__contains=search_term)  |
            Q(user__email__contains=search_term)      |
            Q(phone__contains=search_term)
        )[:15]

    def __str__(self):
        return f'{self.full_name}'

class Account(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    name = models.TextField(max_length=50)
    currency_type= models.CharField(max_length=5)
    is_loan = models.BooleanField(default=False) ## changing  to True can change the value 
    created_at = models.DateTimeField(auto_now_add=True)
    

    def get_absolute_url(self):
        return reverse('customer_details', args=[str(self.pk)])

    class Meta:
        get_latest_by = 'pk'

    @property
    def movements(self) -> QuerySet:
        return Ledger.objects.filter(account=self)

    @property
    def balance(self) -> Decimal:
        return self.movements.aggregate(models.Sum('amount'))['amount__sum'] or Decimal(0)

    @property
    def get_iban(self) -> str:
        bank = settings.BANK_NAME
        return f'{bank}{self.currency_type}{self.pk}'
        return f'{self.pk}'

    @property
    def modify_account_type(self):
        if self.is_loan == False:
            self.is_loan = 'daily'
        elif self.is_loan == True:
            self.is_loan = 'loan'
        return self
    
    

    def __str__(self):
        if self.is_loan == False:
            return f'{self.pk} - {self.name} - {self.currency_type} - daily'
        elif self.is_loan == True:
            return f'{self.pk} - {self.name} - {self.currency_type} - loan'
    

class Ledger(models.Model):
    account     = models.ForeignKey(Account, on_delete=models.PROTECT)
    transaction = models.ForeignKey(UID, on_delete=models.PROTECT)
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True, db_index=True)

    @classmethod
    def transfer(cls, amount, debit_account, debit_text, credit_account, credit_text, is_loan=False) -> int:
        assert amount >= 0, 'Negative amount not allowed for transfer.'
        with transaction.atomic():
            if debit_account == credit_account:
                raise TransferNotAllowed
            if debit_account.balance >= amount or is_loan:
                uid = UID.uid
                cls(amount=-amount, transaction=uid, account=debit_account, description=debit_text).save()
                cls(amount=amount, transaction=uid, account=credit_account, description=credit_text).save()
            else:
                raise InsufficientFunds
        return uid
    @classmethod
    def receive_transfer(cls, amount, external_account, debit_text, credit_account, sender_account, is_loan=False) -> int:
        assert amount >= 0, 'Negative amount not allowed for transfer.'
        with transaction.atomic():
            # if debit_account.balance >= amount or is_loan:
                uid = UID.uid
                cls(amount=amount, transaction=uid, account=credit_account, description=debit_text).save()
                cls(amount=-amount, transaction=uid, account=external_account, description=sender_account).save()               
            # else:
            #     raise InsufficientFunds
        return uid
 
    @classmethod
    def check_external_transfer(cls, debit_account, amount)-> bool:
        assert amount >= 0, 'Negative amount not allowed for transfer.'
        if debit_account.balance >= amount:
            return True
        else:
            raise InsufficientFunds  
    

    def __str__(self):
        return f'{self.transaction} - {self.account} - {self.description} - {self.created_at}'