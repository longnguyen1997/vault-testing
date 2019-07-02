from os import system
from secrets_engines import *
from signer import *


def test():
    client = get_client(True)
    disable_secrets_engine(client, 'pmk-ca-1199')
    try:
        data = generate_root_ca().json()['data']
        print(data['certificate'])
    except:
        exit(1)
    print(sign_csr('./req.csr').json()['data']['certificate'])


def teardown():
    client = get_client(True)
    disable_secrets_engine(client, 'pmk-ca-1199')


test()
teardown()
