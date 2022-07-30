from django.core.management.base import BaseCommand
from bank_app.models import Rank 


class Command(BaseCommand):
    def handle(self, **options):
        print('Provisioning ...')
        if not Rank.objects.all():
            Rank.objects.create(rank_type='Gold', value=75)
            Rank.objects.create(rank_type='Silver', value=50)
            Rank.objects.create(rank_type='Basic', value=10)
