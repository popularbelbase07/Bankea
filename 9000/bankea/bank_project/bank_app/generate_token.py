import jwt
import time
from .currency_api import convert

"""Generates a token with the request data"""
def generate_token(user,debit_account, external_pk, amount, external_currency, debit_text,credit_text):
    iat = int(time.time())
    exp = iat + 600
    user = str(user)
    account_currency = debit_account.currency_type
    account_iban = debit_account.get_iban
    if account_currency == external_currency:
        token = jwt.encode(
            {"iat": iat, 
            "exp": exp,
            'sender_user': user, 
            'sender_account': account_iban,
            'sender_text':debit_text,
            'sender_amount': str(amount),  
            'receiver_account_pk': external_pk,
            'sender_currency': account_currency,
            'receiver_currency': external_currency,    
            'receiver_credit_text': credit_text}, 
            "secret", algorithm="HS256")
    else:
        result = convert(amount, account_currency, external_currency)
        result = repr(round(result, 2))
        token = jwt.encode(
            {"iat": iat, 
            "exp": exp,
            'sender_user': user, 
            'sender_account': account_iban,
            'sender_text':debit_text,
            'sender_amount': result,
            'receiver_account_pk': external_pk, 
            'sender_currency': account_currency,
            'receiver_currency': external_currency,       
            'receiver_credit_text': credit_text}, 
            "secret", algorithm="HS256")
    return token