from distutils.sysconfig import customize_compiler
from django.test import TestCase
from .models import Rank, Customer, Account
from django.contrib.auth.models import User
from django.conf import settings

class CustomerTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(first_name="pepe", last_name="ortega",username="pepe75", email="pepe@mail.com", password="Pass12345")
        new_rank = Rank.objects.create(rank_type="gold", value=60)
        customer = Customer.objects.create(user=user, rank= new_rank, phone="50571216")
        Account.objects.create(user=user, name="credit", is_loan=True)
        Account.objects.create(user=user, name="debit", is_loan=False)
        



    def test_customer_with_rank(self):
        """Customer is correctly identified"""
        rank = Rank.objects.get(rank_type="gold")
        customer = Customer.objects.get(user = 1)
        self.assertEqual(rank.rank_type, 'gold')
        self.assertEqual(rank.value, 60)
        self.assertEqual(customer.phone, '50571216')
        self.assertEqual(f'{customer.user}', 'pepe75')

    def test_customer_full_name(self):
        """Customer full name is correct"""
        customer = Customer.objects.get(user = 1)
        assert customer.full_name == 'pepe ortega'
        self.assertEqual(customer.full_name, 'pepe ortega')
        
    def test_customer_default_account(self):
        """Default account is the first one"""
        customer = Customer.objects.get(user = 1)
        self.assertIsInstance(customer.default_account, Account )

    def test_can_make_loan(self):
        """Customer can make loan"""
        customer = Customer.objects.get(user = 1)
        self.assertEqual(customer.can_make_loan, True) 

    def test_customer_accounts(self):
        """Customer has accounts"""
        customer = Customer.objects.get(user = 1)
        a = customer.accounts
        self.assertEqual(a.count(), 2)
