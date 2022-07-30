import jwt
import time
from .currency_api import convert

"""Generates a token with the request data"""
def generate_token(user,account_currency, external_pk, amount, external_currency, credit_text):
    iat = int(time.time())
    exp = iat + 600
    user = str(user)
    if account_currency == external_currency:
        token = jwt.encode({"iat": iat, "exp": exp,'from_user': user, 'account_pk': external_pk, 'amount': str(amount),'currency': external_currency,'credit_text': credit_text}, "secret", algorithm="HS256")
    else:
        result = convert(amount, account_currency, external_currency)
        result = repr(round(result, 2))
        token = jwt.encode({"iat": iat, "exp": exp,'from_user': user,'account_pk': external_pk,'amount': result,'currency': external_currency,'credit_text': credit_text}, "secret", algorithm="HS256")
    return token