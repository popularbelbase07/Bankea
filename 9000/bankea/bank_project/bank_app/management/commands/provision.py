from django.core.management.base import BaseCommand
from bank_app.models import Rank 


class Command(BaseCommand):
    def handle(self, **options):
        print('Provisioning ...')
        if not Rank.objects.all():
            Rank.objects.create(rank_type='Gold', value=90)
            Rank.objects.create(rank_type='Silver', value=60)
            Rank.objects.create(rank_type='Basic', value=25)
            
