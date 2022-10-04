from rest_framework import serializers
from .models import Account, Customer, Ledger, User, Rank


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('pk', 'user', 'name', 'currency_type', 'is_loan', 'created_at', )
        model = Account



class LedgeSerializer(serializers.ModelSerializer):
    class Meta:
        fields= ('amount', 'debit_account', 'credit_account', 'description', 'created_at')
        model = Ledger
        
        
class RankSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('rank_type', 'value', 'created_at', 'updated_at')
        model = Rank
        



####################        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'first_name', 'last_name', 'email')
        model = User

# for customer API View
class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    rank = RankSerializer()
      
    
    class Meta:
        fields = ('user','phone','created_at', 'rank',) 
        model = Customer 

class ExternalTransferSerializer(serializers.Serializer):
    sender_user = serializers.CharField(max_length=128)
    sender_account = serializers.CharField(max_length=50)
    sender_text = serializers.CharField(max_length=128)
    sender_amount = serializers.CharField(max_length=255)
    receiver_account_pk = serializers.CharField(max_length=128)
    sender_currency = serializers.CharField(max_length=128)
    receiver_currency = serializers.CharField(max_length=128)
    receiver_credit_text = serializers.CharField(max_length=128)
    
    class Meta:
        fields= ('sender_user', 'sender_account','sender_text','sender_amount', 'receiver_account_pk','sender_currency', 'receiver_currency', 'receiver_credit_text')

    def create(self, data):

        return ExternalTransferSerializer(data).data