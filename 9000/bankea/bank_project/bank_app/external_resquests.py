import requests
import json
from requests.structures import CaseInsensitiveDict
from django.conf import settings

from .models import BankList


"""Send an external request with token in the headers"""
def send_trasfer(token, external_bank):
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = f"Bearer {token}"
    headers["Content-Type"] = "application/json"
    bank = BankList.objects.get(bank_name= external_bank)
    bank_host = bank.get_host
    print(f'{bank_host}/api/v1/transfer_details/')
    try: 
        r = requests.post(f'{bank_host}/api/v1/transfer_details/', headers=headers)
    except requests.exceptions.RequestException as e:  
        raise SystemExit(e)
    return r

def confirm_transfer(external_bank, transfer,user):
    bank = BankList.objects.get(bank_name= external_bank)
    bank_host = bank.get_host
    print(f'this is the confirm bank {bank_host}')
    user_data = {
        'user':user,
        'transfer':transfer
    }
    try:
        r = requests.put(f'{bank_host}/api/v1/get_external_transfer_confirmation/', data=json.dumps(user_data))
    except requests.exceptions.RequestException as e:  
        raise SystemExit(e)
    return r
