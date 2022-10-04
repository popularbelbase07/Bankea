from pickle import TRUE
import secrets
from django.core.management.base import BaseCommand
# from django.contrib.auth.models import User
from bank_app.models import User, Account, Ledger, Customer, BankList


class Command(BaseCommand):
    def handle(self, **options):
        print('Adding demo data ...')
        
        bank1 = BankList.objects.create(bank_name='BNK1', host_name='http://localhost:8000')
        bank1.save()
        
        bank2 = BankList.objects.create(bank_name='BNK2', host_name='http://localhost:9000')
        bank2.save()

        bank_user = User.objects.create_user('bank', email='', password=secrets.token_urlsafe(64))
        bank_user.is_active = False
        bank_user.save()
        ipo_account = Account.objects.create(user=bank_user, name='Bank IPO Account', currency_type='DKK')
        ops_account = Account.objects.create(user=bank_user, name='Bank OPS Account', currency_type='DKK')
        Ledger.transfer(
            10_000_000,
            ipo_account,
            'Operational Credit',
            ops_account,
            'Operational Debit',
            is_loan=True
        )
        
        staff_user = User.objects.create_user(
            'admin', email='', password= 'admin')
        staff_user.is_active = True
        staff_user.is_staff =True
        staff_user.save()
        

        dummy_user = User.objects.create_user('julia', email='julia@gmail.com', password='Famous123')
        dummy_user.first_name = 'Julia'
        dummy_user.last_name  = 'Sand'
        dummy_user.save()
        dummy_customer = Customer(user=dummy_user, phone='28908070')
        dummy_customer.save()
        dummy_account = Account.objects.create(user=dummy_user, name='Checking account', currency_type='DKK')
        dummy_account.save()

        Ledger.transfer(
            5_000,
            ops_account,
            'Payout to julia',
            dummy_account,
            'Payout from bank'
        )

        john_user = User.objects.create_user('john', email='john@smith.com', password='Famous123')
        john_user.first_name = 'John'
        john_user.last_name = 'Smith'
        john_user.save()
        john_customer = Customer.objects.create(user=john_user, phone='28010203')
        john_customer.save()
        john_account = Account.objects.create(user=john_user, name='Checking account', currency_type='DKK')
        john_account.save()

        Ledger.transfer(
            5_000,
            ops_account,
            'Payout to john',
            john_account,
            'Payout from bank'
        )

      
        adam_user = User.objects.create_user('adam', email='adam@persen.com', password='Famous123')
        adam_user.first_name = 'Adam'
        adam_user.last_name = 'Persen'
        adam_user.save()
        adam_customer = Customer.objects.create(user=adam_user, phone='33481231')
        adam_customer.save()
        adam_account = Account.objects.create(user=adam_user, name='Checking account', currency_type='DKK')
        adam_account.save()

        Ledger.transfer(
            5_000,
            ops_account,
            'Payout to adam',
            adam_account,
            'Payout from bank'
        )
       
#create super user
        popular_user = User.objects.create_superuser('popularbelbase', email='popu0003@stud.kea.dk', password='Famous12345')
        popular_user.first_name = 'Popular'
        popular_user.last_name = 'Belbase'
        popular_user.save()


       
        isaac_user = User.objects.create_user('isaac', email='isaac@zam.com', password='Famous123')
        isaac_user.first_name = 'Isaac'
        isaac_user.last_name = 'Zam'
        isaac_user.save()
        isaac_customer = Customer.objects.create(user=isaac_user, phone='10233372')
        isaac_customer.save()
        isaac_account = Account.objects.create(user=isaac_user, name='Checking account', currency_type='DKK')
        isaac_account.save()

        Ledger.transfer(
            5_000,
            ops_account,
            'Payout to Isaac',
            isaac_account,
            'Payout from bank'
        )

        gabriel_user = User.objects.create_user('gabriel', email='gabriel@oscar.com', password='Famous123')
        gabriel_user.first_name = 'Gabriel'
        gabriel_user.last_name = 'Oscar'
        gabriel_user.save()
        gabriel_customer = Customer.objects.create(user=gabriel_user, phone='90772311')
        gabriel_customer.save()
        gabriel_account = Account.objects.create(user=gabriel_user, name='Checking account', currency_type='DKK')
        gabriel_account.save()

        Ledger.transfer(
            5_000,
            ops_account,
            'Payout to Gabriel',
            gabriel_account,
            'Payout from bank'
        )

        external_bank = User.objects.create_user('external_bank', email='', password=secrets.token_urlsafe(64))
        external_bank.is_active = False
        external_bank.save()
