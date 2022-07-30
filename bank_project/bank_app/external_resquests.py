import requests
import json
from requests.structures import CaseInsensitiveDict
from django.conf import settings


"""Send an external request with token in the headers"""
def send_trasfer(token, external_bank):
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = f"Bearer {token}"
    headers["Content-Type"] = "application/json"
    bank_host = settings.BANK_LIST[external_bank]
    try: 
        r = requests.post(f'{bank_host}/api/v1/transfer_details/', headers=headers)
    except requests.exceptions.RequestException as e:  
        raise SystemExit(e)
    return r

def confirm_transfer(external_bank, transfer):
    bank_host = settings.BANK_LIST[external_bank]
    try:
        r = requests.put(f'{bank_host}/api/v1/get_external_transfer_number/', data=transfer)
    except requests.exceptions.RequestException as e:  
        raise SystemExit(e)
    return r
