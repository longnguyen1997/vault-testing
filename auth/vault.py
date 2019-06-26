import hvac
import os
import subprocess


def mock_sign_intermediate(client, csr, role, cn):
	return client.secrets.pki.sign_intermediate(csr=csr, common_name=cn)


def mock_cluster_init(client, cluster_name):
	disable_secrets_engine(client, cluster_name)
	enable_new_pki_secrets_engine(client, cluster_name)
	client.secrets.pki.create_or_update_role(
	   cluster_name,
	   {
	      'ttl': '72h',
	      'allow_localhost': 'false',
	      'allow_subdomains': 'true',
	      'allowed_domains': ['platform9.com', 'platform9.horse']
	   }
	)


def mock_root_ca(client):
	# Flush current data.
	try:
		disable_secrets_engine(client, 'pki')
	except:
		pass
	enable_new_pki_secrets_engine(client, 'pki')
	# Internal, private key not exported.
	ca_response = client.secrets.pki.generate_root(type='internal',common_name='ca.com')


def get_client():
	url = os.getenv('VAULT_URL', 'http://localhost:8200')
	token = subprocess.check_output('vault token create -format=json | jq -r .auth.client_token', shell=True)
	if not token:
		raise ValueError('No Vault token to authenticate client!')
	return hvac.Client(url, token.strip())

def get_secrets_engines(client):
	"""
	Taken from hvac documentation website.
	"""
	secrets_engines_list = client.sys.list_mounted_secrets_engines()['data']
	print('The following secrets engines are mounted: %s' % ', '.join(sorted(secrets_engines_list.keys())))

def enable_new_pki_secrets_engine(client, engine_path):
	"""
	client (hvac.Client): HVAC client. Must be authenticated.
	engine_path (str): Desired endpoint for the new PKI secrets engine.
	"""
	client.sys.enable_secrets_engine(backend_type='pki', path=engine_path)

def disable_secrets_engine(client, engine_path):
	"""
	Uses client to disable the secrets engine at engine_path.
	"""
	client.sys.disable_secrets_engine(path=engine_path)

def move_secrets_engine(client, old_path, new_path):
	"""
	client (hvac.Client): Authenticated Vault client.
	old_path (str): Old path of secrets engine to be moved.
	new_path (str): Path to migrate the secrets engine to.
	"""
	client.sys.move_backend(
    	from_path=old_path,
    	to_path=new_path,
	)

def generate_and_sign_intermediate(client, cluster_name):
	"""
	Works on behalf of a cluster.
	Generates an intermediate CSR and signs it using a root CA's key.
	Intermediates engines are enabled and formatted by clusters,
	cluster_name (str): Name of the K8S cluster.
	"""

	try:
		enable_new_pki_secrets_engine(client, 'pki-int')
	except:
		pass

	# TODO: Set expiration / TTLs for these Vault engines.

	cn = cluster_name + '.platform9.horse'

	# requests.Response object given in json dict format.
	response = client.secrets.pki.generate_intermediate(
    	type='internal',
    	common_name=cn,
    	mount_point='pki-int'
	).json()

	csr = response['data']['csr'] # Intermediate CSR to be signed by the DU CA's key.
	print('CSR FOR INTERMEDIATE CERTIFICATE')
	print(csr)

	'''
	TODO: Actually plug this in to the DU CA and get a real signed response.
	Current root CA being used to sign this intermediate is the main PKI engine at pki/.
	'''

	signed_intermediate = mock_sign_intermediate(client, csr, cluster_name, cn).json()['data']['certificate']
	print()
	print('SIGNED INTERMEDIATE')
	print(signed_intermediate)
	client.secrets.pki.set_signed_intermediate(signed_intermediate, mount_point='pki-int')