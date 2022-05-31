from unicodedata import name
from django.db import models
from django.contrib.auth.models import User


class UID(models.Model):
    @classmethod
    @property
    def uid(cls):
        return cls.objects.create()

    def __str__(self):
        return f'{self.pk}'


class Rank(models.Model):
    name = models.CharField(max_length=15, unique=True, db_index=True)
    value = models.IntegerField(unique=True, db_index=True)


class Customer(models.Model):
    user = models.OneToOneField(
        User, primary_key=True, on_delete=models.PROTECT)
    rank = models.ForeignKey(Rank, default=2, on_delete=models.PROTECT)
    personal_id = models.IntegerField(db_index=True)
    phone = models.BigIntegerField(db_index=True)


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    name = models.CharField(max_length=50, db_index=True)


class Ledger(models.Model):
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    transaction = models.ForeignKey(UID, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    text = models.TextField()
    
    