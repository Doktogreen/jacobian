import json
import urllib3
from decouple import config
from urllib3.exceptions import HTTPError
from wallet.views import providusAuthentication


HEADERS = {
    "Content-Type": "application/json",
    "Client-Id": providusAuthentication()['Client-Id'],
    "X-Auth-Signature": providusAuthentication()['X-Auth-Signature']
}

URL = config('BASEURL_PROVIDUS')
http = urllib3.PoolManager()


def create_reserved_account_number(account_name: str, bvn: str):
    url = f'{URL}/PiPCreateReservedAccountNumber'
    
    if config('DJANGO_DEBUG'):
        data = json.dumps({
            'account_name': account_name,
            'bvn': ""
        })
    else:
        data = json.dumps({
            'account_name': account_name,
            'bvn': bvn
        })
        
    response = http.request('POST', url=url, headers=HEADERS, body=data)
    
    data = json.loads(response.data)
    print(data)
    
    if not data.get('requestSuccessful'):
        raise HTTPError('Invalid Request')
    return data.get('account_number')


if __name__ == '__main__':
    an = create_reserved_account_number("chioma")
    print(an)
    