import requests
import json

def get_symbols():
    codes = []
    try:
        r = requests.get('https://api.exchangerate.host/symbols', timeout=20)
        
        if not r:
            codes = [('DKK', 'DKK'), ('SEK', 'SEK'), ('EUR', 'EUR'),('USD', 'USD')]
        else:
            r_status = r.status_code  
            data = json.loads(r.text)
            if data:
                dest = data['symbols'].items()
                for key, value in dest:
                    codes.append((value['code'], value['code']))
            
        
    except requests.exceptions.RequestException as e:  
        raise SystemExit(e) 
    return codes
def convert(amount,from_currency,to_currency):
    try:
        r = requests.get(f'https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}&amount={amount}')
        r_status = r.status_code  
        if r_status == 200:
            data = json.loads(r.text)
            if data:
                result = data['result']
                return result
    except requests.exceptions.RequestException as e:  
        raise SystemExit(e) 

   