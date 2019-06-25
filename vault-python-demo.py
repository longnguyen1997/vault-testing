import os

import hvac


vault_url = 'http://localhost:8200'
vault_token = 's.8SOecJ300gPlwpEF2P3OYD9k'
vault_unseal_key = '2qvqlCQc3C2QdFfG8Szf6+mT9gnUhKn44R/4Arw0Qt4='


client = hvac.Client()
client = hvac.Client(
 url=os.getenv('VAULT_URL', vault_url),
 token=os.getenv('VAULT_TOKEN', vault_token),
)

generate_intermediate_response = client.secrets.pki.generate_intermediate(
    type='exported',
    common_name='Vault integration tests'
)
print('Intermediate certificate: {}'.format(generate_intermediate_response))