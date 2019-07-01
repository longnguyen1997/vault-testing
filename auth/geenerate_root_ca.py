from hvac import Client as VaultClient
from os import getenv
from time import time


def generate_root_ca(cluster_id='1199', dev=False)
	'''
	cluster_id (str): ID of the PMK cluster. Mocked to 1199.

	Generates/enables a new Vault PKI engine for the cluster provided, if it does
	not already exist. This will be an internal PKI engine, so the private key is
	not exported.

	Uses the Python HVAC Vault API: https://hvac.readthedocs.io/en/stable/usage/secrets_engines/pki.html.
	'''
	# Assumes Vault is on localhost if no information is found.
	if dev is False:
	    client = VaultClient(url=os.getenv(
	        'VAULT_ADDR', 'http://127.0.0.1:8200'), token=os.getenv('VAULT_TOKEN'))
	else:
		client = VaultClient()

    vault_path = 'pmk-ca-' + cluster_id
    common_name = 'kubernetes-ca@%d' % time()
    enable_new_pki_secrets_engine(
        client, vault_path, description='PMK CA engine for cluster ' + cluster_id)

    ca_response = client.secrets.pki.generate_root(
        type='internal', common_name=common_name, mount_point=vault_path)

