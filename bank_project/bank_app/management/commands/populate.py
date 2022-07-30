import secrets
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bank_app.models import Account, Ledger, Customer


class Command(BaseCommand):
    def handle(self, **options):
        print('Adding demo data ...')

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

        victoria_user = User.objects.create_user('victoria', email='victoria@gmail.com', password='Famous12345')
        victoria_user.first_name = 'Victoria'
        victoria_user.last_name  = 'Sandra'
        victoria_user.save()
        victoria_customer = Customer(user=victoria_user, phone='34343434')
        victoria_customer.save()
        victoria_account = Account.objects.create(user=victoria_user, name='Checking account', currency_type='DKK')
        victoria_account.save()

        Ledger.transfer(
            5_000,
            ops_account,
            'Payout to victoria',
            victoria_account,
            'Payout from bank'
        )

        harry_user = User.objects.create_user('harry', email='harry@smith.com', password='Famous12345')
        harry_user.first_name = 'Harry'
        harry_user.last_name = 'Smith'
        harry_user.save()
        harry_customer = Customer.objects.create(user=harry_user, phone='12345678')
        harry_customer.save()
        harry_account = Account.objects.create(user=harry_user, name='Checking account', currency_type='DKK')
        harry_account.save()

        Ledger.transfer(
            6_000,
            ops_account,
            'Payout to harry',
            harry_account,
            'Payout from bank'
        )

        toni_user = User.objects.create_user('Toni', email='toni@jarmusch.com', password='Famous12345')
        toni_user.first_name = 'Toni'
        toni_user.last_name = 'Dipp'
        toni_user.save()
        toni_customer = Customer.objects.create(user=toni_user, phone='23232323')
        toni_customer.save()
        toni_account = Account.objects.create(user=toni_user, name='Checking account', currency_type='USD')
        toni_account.save()

        Ledger.transfer(
            5_000,
            ops_account,
            'Payout to toni',
            toni_account,
            'Payout from bank'
        )