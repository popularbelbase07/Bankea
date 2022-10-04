from django.contrib import admin

from .models import BankList, Rank, Customer, Account, Ledger

admin.site.register(Rank)
admin.site.register(Customer)
admin.site.register(Account)
admin.site.register(Ledger)
admin.site.register(BankList)

