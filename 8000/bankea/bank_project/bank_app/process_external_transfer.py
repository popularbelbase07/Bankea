from .models import User, Account, Ledger
from .external_resquests import confirm_transfer

"""Process the received transfer from external account
and save it to Ledger table, then sends a PUT request """
def process_external_transfer(data):
    print(f'this is the data to process: {data}')
    credit_account = Account.objects.get(pk=data['receiver_account_pk'])
    print(credit_account)
    user_id = credit_account.user_id
    user = User.objects.get(pk=user_id)
    if credit_account:
        external_bank = User.objects.get(username='external_bank')
        print(data['sender_account'])
    try:
        external_account = Account.objects.get(name=data['sender_account'])
    except Account.DoesNotExist:
        external_account = Account.objects.create(user=external_bank, name= data['sender_account'], currency_type=data['sender_currency'])
        external_account.save()
        
        print(f'external account founded in process: {external_account}')
        # if not external_account:
        #     external_account = Account.objects.create(user=external_bank, name= data['sender_account'], currency_type=data['sender_currency'])
        transfer = Ledger.receive_transfer(float(data['sender_amount']), external_account, data['receiver_credit_text'],credit_account, data['sender_account'])
            # return transaction_details(request, transfer)
        if transfer:
            bank = data['sender_account'][0:4]
            print(f'this the bank to confirm the transfer: {bank}')
            # print(transfer)
            r = confirm_transfer(bank,str(transfer), str(user))
            return r 